"""Interview orchestration — the service layer that sequences the whole
pipeline and owns all persistence. API routes stay thin; this is where the
business logic lives.

Lifecycle:
    start_session() -> parse resume, build profile, pick focus topics
    next_question()  -> RAG retrieve -> generate -> persist Question
    submit_answer()  -> persist Answer + grade it
    finalize()       -> aggregate transcript -> LLM summary -> persist
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Answer, InterviewSession, Question
from app.rag.retriever import retrieve_for_topic
from app.services import analysis, question_gen
from app.services.context_builder import select_focus_topics
from app.services.resume_parser import build_profile
from app.services.roles import get_role


def start_session(
    db: Session, *, role_id: str, resume_text: str, candidate_name: str
) -> InterviewSession:
    role = get_role(role_id)  # raises KeyError if unknown
    profile = build_profile(resume_text, role["label"])
    focus_topics = select_focus_topics(role_id, profile)

    session = InterviewSession(
        candidate_name=candidate_name or "Candidate",
        role=role_id,
        resume_text=resume_text[:20000],
        resume_profile=profile,
        focus_topics=focus_topics,
        status="in_progress",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _answered_count(session: InterviewSession) -> int:
    return sum(1 for q in session.questions if q.answer is not None)


def _transcript(session: InterviewSession) -> list[dict]:
    items = []
    for q in session.questions:
        items.append(
            {
                "order_index": q.order_index,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "question": q.text,
                "answer": q.answer.text if q.answer else None,
                "score": q.answer.score if q.answer else None,
                "feedback": q.answer.feedback if q.answer else None,
                "context_sources": q.context_sources,
            }
        )
    return items


def next_question(db: Session, session: InterviewSession) -> Question | None:
    """Generate & persist the next question, or None if the interview is done."""
    total = settings.NUM_QUESTIONS
    existing = sorted(session.questions, key=lambda q: q.order_index)

    # If the most recent question is still unanswered, return it (idempotent).
    if existing and existing[-1].answer is None:
        return existing[-1]

    order_index = len(existing)
    if order_index >= total or order_index >= len(session.focus_topics):
        return None

    role = get_role(session.role)
    topic = session.focus_topics[order_index]

    # RAG: retrieve grounded context for this topic + candidate.
    query, chunks = retrieve_for_topic(session.role, topic, session.resume_profile)

    previous_qa = _transcript(session)
    generated = question_gen.generate_question(
        role_label=role["label"],
        topic=topic,
        profile=session.resume_profile,
        context_chunks=chunks,
        previous_qa=previous_qa,
        order_index=order_index,
    )

    question = Question(
        session_id=session.id,
        order_index=order_index,
        text=generated["question"],
        topic=generated["topic"],
        difficulty=generated["difficulty"],
        retrieval_query=query,
        context_sources=[
            {"source": c["source"], "snippet": c["snippet"][:400], "score": c["score"]}
            for c in chunks
        ],
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def submit_answer(db: Session, session: InterviewSession, *, question_id: str, answer_text: str):
    question = next((q for q in session.questions if q.id == question_id), None)
    if question is None:
        raise KeyError("question not found in this session")
    if question.answer is not None:
        # Idempotent: return the existing evaluation.
        return question.answer

    role = get_role(session.role)
    evaluation = analysis.evaluate_answer(
        question=question.text,
        answer=answer_text,
        topic=question.topic,
        context_chunks=question.context_sources,
    )
    answer = Answer(
        question_id=question.id,
        text=answer_text,
        score=evaluation["score"],
        feedback=evaluation["feedback"],
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    # Auto-finalise when the last expected answer arrives.
    if _answered_count(session) >= min(settings.NUM_QUESTIONS, len(session.focus_topics)):
        finalize(db, session, role_label=role["label"])
    return answer


def finalize(db: Session, session: InterviewSession, *, role_label: str) -> InterviewSession:
    if session.status == "completed" and session.summary:
        return session
    summary = analysis.build_summary(
        role_label=role_label,
        profile=session.resume_profile,
        transcript=_transcript(session),
    )
    session.summary = summary
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


def remaining(session: InterviewSession) -> int:
    total = min(settings.NUM_QUESTIONS, len(session.focus_topics))
    return max(0, total - _answered_count(session))
