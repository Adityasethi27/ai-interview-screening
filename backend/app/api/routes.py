"""HTTP surface. Routes are intentionally thin: validate input, delegate to the
service layer, shape the response. Each stage of the interview lifecycle maps
to a clear resource/endpoint.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.models import InterviewSession
from app.schemas import (
    NextQuestionResponse,
    QuestionOut,
    RoleInfo,
    SessionSummary,
    StartSessionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.db.database import get_db
from app.services import interview
from app.services.resume_parser import extract_text_from_pdf_bytes
from app.services.roles import get_role, list_roles

router = APIRouter(prefix="/api")


# ---------------------------------------------------------------- roles
@router.get("/roles", response_model=list[RoleInfo])
def get_roles():
    return list_roles()


# ---------------------------------------------------------------- helpers
def _load_session(db: Session, session_id: str) -> InterviewSession:
    session = db.get(InterviewSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def _question_out(q, answered: bool | None = None) -> QuestionOut:
    return QuestionOut(
        id=q.id,
        order_index=q.order_index,
        text=q.text,
        topic=q.topic,
        difficulty=q.difficulty,
        retrieval_query=q.retrieval_query,
        context_sources=q.context_sources,
        answered=(q.answer is not None) if answered is None else answered,
    )


# ---------------------------------------------------------------- start session
@router.post("/sessions", response_model=StartSessionResponse)
async def create_session(
    role: str = Form(...),
    candidate_name: str = Form("Candidate"),
    resume_text: str | None = Form(None),
    resume_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    # Validate role early with a clear error.
    try:
        get_role(role)
    except KeyError:
        raise HTTPException(status_code=422, detail=f"Unknown role '{role}'")

    # Resolve resume text from either the uploaded file or the pasted text.
    text = (resume_text or "").strip()
    if resume_file is not None:
        data = await resume_file.read()
        if resume_file.filename and resume_file.filename.lower().endswith(".pdf"):
            try:
                text = extract_text_from_pdf_bytes(data)
            except Exception as exc:
                raise HTTPException(status_code=422, detail=f"Could not read PDF: {exc}")
        else:
            text = data.decode("utf-8", errors="ignore").strip()

    if len(text) < 30:
        raise HTTPException(
            status_code=422,
            detail="Resume content is empty or too short. Upload a PDF or paste text.",
        )

    session = interview.start_session(
        db, role_id=role, resume_text=text, candidate_name=candidate_name
    )
    return StartSessionResponse(
        session_id=session.id,
        role=session.role,
        candidate_name=session.candidate_name,
        profile=session.resume_profile,
        focus_topics=session.focus_topics,
        total_questions=min(settings.NUM_QUESTIONS, len(session.focus_topics)),
    )


# ---------------------------------------------------------------- next question
@router.get("/sessions/{session_id}/next-question", response_model=NextQuestionResponse)
def get_next_question(session_id: str, db: Session = Depends(get_db)):
    session = _load_session(db, session_id)
    question = interview.next_question(db, session)
    db.refresh(session)
    return NextQuestionResponse(
        session_id=session.id,
        question=_question_out(question, answered=False) if question else None,
        remaining=interview.remaining(session),
        finished=question is None,
    )


# ---------------------------------------------------------------- submit answer
@router.post("/sessions/{session_id}/answers", response_model=SubmitAnswerResponse)
def submit_answer(session_id: str, body: SubmitAnswerRequest, db: Session = Depends(get_db)):
    session = _load_session(db, session_id)
    try:
        answer = interview.submit_answer(
            db, session, question_id=body.question_id, answer_text=body.answer.strip()
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    db.refresh(session)
    return SubmitAnswerResponse(
        evaluation={"score": answer.score or 0.0, "feedback": answer.feedback},
        remaining=interview.remaining(session),
        finished=interview.remaining(session) == 0,
    )


# ---------------------------------------------------------------- summary
@router.get("/sessions/{session_id}/summary", response_model=SessionSummary)
def get_summary(session_id: str, db: Session = Depends(get_db)):
    session = _load_session(db, session_id)
    role = get_role(session.role)

    # Finalise on demand if the client asks for the summary early.
    if session.status != "completed":
        interview.finalize(db, session, role_label=role["label"])
        db.refresh(session)

    summary = session.summary or {}
    transcript = []
    for q in sorted(session.questions, key=lambda x: x.order_index):
        transcript.append(
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

    return SessionSummary(
        session_id=session.id,
        candidate_name=session.candidate_name,
        role=role["label"],
        status=session.status,
        created_at=session.created_at,
        completed_at=session.completed_at,
        profile=session.resume_profile,
        focus_topics=session.focus_topics,
        overall_score=summary.get("overall_score"),
        verdict=summary.get("verdict", "borderline"),
        strengths=summary.get("strengths", []),
        areas_to_improve=summary.get("areas_to_improve", []),
        narrative=summary.get("narrative", ""),
        transcript=transcript,
    )
