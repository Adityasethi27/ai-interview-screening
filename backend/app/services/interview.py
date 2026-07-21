"""Interview orchestration for the adaptive conversational agent.

Owns session state + persistence; delegates the "what to say next" decision to
`conversation.py`. Each candidate message drives exactly one turn:
    record answer + assessment -> decide advance/follow_up/conclude -> next message
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Answer, InterviewSession, Question
from app.rag.retriever import retrieve_for_topic
from app.services import analysis, conversation
from app.services.context_builder import select_focus_topics
from app.services.resume_parser import build_profile
from app.services.roles import get_role


# ----------------------------------------------------------------- helpers
def _sorted_questions(session: InterviewSession) -> list[Question]:
    return sorted(session.questions, key=lambda q: q.order_index)


def _history(session: InterviewSession) -> list[dict]:
    turns: list[dict] = []
    for q in _sorted_questions(session):
        turns.append({"role": "interviewer", "text": q.text})
        if q.answer is not None:
            turns.append({"role": "candidate", "text": q.answer.text})
    return turns


def _last_unanswered(session: InterviewSession) -> Question | None:
    for q in reversed(_sorted_questions(session)):
        if q.answer is None:
            return q
    return None


def _context_payload(chunks: list[dict]) -> list[dict]:
    return [
        {"source": c["source"], "snippet": c["snippet"][:400], "score": c["score"]}
        for c in chunks
    ]


def _plan(session: InterviewSession) -> list[str]:
    return session.focus_topics or []


# ----------------------------------------------------------------- lifecycle
def start_session(
    db: Session, *, role_id: str, resume_text: str, candidate_name: str
) -> InterviewSession:
    role = get_role(role_id)
    profile = build_profile(resume_text, role["label"])
    topics = select_focus_topics(role_id, profile)[: settings.NUM_TOPICS]

    session = InterviewSession(
        candidate_name=candidate_name or "Candidate",
        role=role_id,
        resume_text=resume_text[:20000],
        resume_profile=profile,
        focus_topics=topics,
        topic_index=0,
        followup_depth=0,
        status="in_progress",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def open_conversation(db: Session, session: InterviewSession) -> str:
    """Create and persist the interviewer's opening message (greeting + Q1)."""
    if session.questions:  # already opened (idempotent)
        return _sorted_questions(session)[0].text

    plan = _plan(session)
    role = get_role(session.role)
    topic = plan[0] if plan else "core concepts"
    query, chunks = retrieve_for_topic(session.role, topic, session.resume_profile)

    reply = conversation.opening_turn(
        role_label=role["label"],
        candidate_name=session.candidate_name,
        profile=session.resume_profile,
        topic=topic,
        context=chunks,
    )
    q = Question(
        session_id=session.id,
        order_index=0,
        text=reply,
        topic=topic,
        kind="question",
        difficulty=session.resume_profile.get("seniority", "mid"),
        retrieval_query=query,
        context_sources=_context_payload(chunks),
    )
    db.add(q)
    db.commit()
    return reply


def handle_message(db: Session, session: InterviewSession, text: str) -> dict:
    """Process one candidate answer; return {reply, done}."""
    if session.status == "completed":
        return {"reply": "This interview has already concluded.", "done": True}

    current_q = _last_unanswered(session)
    if current_q is None:
        # No pending question — nothing to answer.
        return {"reply": "Let's continue.", "done": False}

    plan = _plan(session)
    role = get_role(session.role)
    idx = session.topic_index
    current_topic = plan[idx] if idx < len(plan) else current_q.topic
    next_topic = plan[idx + 1] if (idx + 1) < len(plan) else None

    # Reuse the current question's stored context; retrieve fresh for the next topic.
    current_context = current_q.context_sources or []
    next_context: list[dict] = []
    next_query = ""
    if next_topic:
        next_query, next_chunks = retrieve_for_topic(
            session.role, next_topic, session.resume_profile
        )
        next_context = _context_payload(next_chunks)

    asked_count = len(session.questions)

    result = conversation.interview_turn(
        role_label=role["label"],
        profile=session.resume_profile,
        plan=plan,
        history=_history(session),
        candidate_answer=text,
        current_topic=current_topic,
        next_topic=next_topic,
        current_context=current_context,
        next_context=next_context,
        asked_count=asked_count,
        max_questions=settings.MAX_QUESTIONS,
        followup_depth=session.followup_depth,
        max_followups=settings.MAX_FOLLOWUPS_PER_TOPIC,
        topics_remaining=max(0, len(plan) - (idx + 1)),
    )

    # 1) Persist the assessment of the answer we just received.
    db.add(
        Answer(
            question_id=current_q.id,
            text=text,
            quality=result["quality"],
            score=result["score"],
            feedback=result["note"],
        )
    )

    action = result["action"]

    # 2) Conclude?
    if action == "conclude":
        db.commit()
        db.refresh(session)
        finalize(db, session, role_label=role["label"])
        return {"reply": result["reply"], "done": True}

    # 3) Advance vs follow-up -> create the next interviewer question.
    if action == "advance" and next_topic is not None:
        session.topic_index = idx + 1
        session.followup_depth = 0
        topic, kind, ctx, query = next_topic, "question", next_context, next_query
    else:  # follow_up (stay on current topic, deeper)
        session.followup_depth += 1
        topic, kind, ctx, query = current_topic, "follow_up", current_context, current_q.retrieval_query

    db.add(
        Question(
            session_id=session.id,
            order_index=asked_count,
            text=result["reply"],
            topic=topic,
            kind=kind,
            difficulty=session.resume_profile.get("seniority", "mid"),
            retrieval_query=query,
            context_sources=ctx,
        )
    )
    db.commit()
    return {"reply": result["reply"], "done": False}


def finalize(db: Session, session: InterviewSession, *, role_label: str) -> InterviewSession:
    if session.status == "completed" and session.summary:
        return session
    summary = analysis.build_summary(
        role_label=role_label,
        profile=session.resume_profile,
        transcript=transcript(session),
    )
    session.summary = summary
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


def transcript(session: InterviewSession) -> list[dict]:
    items = []
    for q in _sorted_questions(session):
        items.append(
            {
                "order_index": q.order_index,
                "topic": q.topic,
                "kind": q.kind,
                "difficulty": q.difficulty,
                "question": q.text,
                "answer": q.answer.text if q.answer else None,
                "quality": q.answer.quality if q.answer else None,
                "score": q.answer.score if q.answer else None,
                "feedback": q.answer.feedback if q.answer else None,
                "context_sources": q.context_sources,
            }
        )
    return items
