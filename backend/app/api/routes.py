"""HTTP surface for the conversational interview.

Lifecycle:
    POST /api/sessions              -> start + opening interviewer message
    POST /api/sessions/{id}/message -> one candidate turn -> next interviewer message
    GET  /api/sessions/{id}/summary -> final qualitative assessment + transcript
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import InterviewSession
from app.schemas import (
    MessageRequest,
    MessageResponse,
    RoleInfo,
    SessionSummary,
    StartSessionResponse,
)
from app.services import interview
from app.services.resume_parser import extract_text_from_pdf_bytes
from app.services.roles import get_role, list_roles

router = APIRouter(prefix="/api")


@router.get("/roles", response_model=list[RoleInfo])
def get_roles():
    return list_roles()


def _load_session(db: Session, session_id: str) -> InterviewSession:
    session = db.get(InterviewSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/sessions", response_model=StartSessionResponse)
async def create_session(
    role: str = Form(...),
    candidate_name: str = Form("Candidate"),
    resume_text: str | None = Form(None),
    resume_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    try:
        get_role(role)
    except KeyError:
        raise HTTPException(status_code=422, detail=f"Unknown role '{role}'")

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
    opening = interview.open_conversation(db, session)
    db.refresh(session)

    return StartSessionResponse(
        session_id=session.id,
        role=session.role,
        candidate_name=session.candidate_name,
        profile=session.resume_profile,
        focus_topics=session.focus_topics,
        opening=opening,
    )


@router.post("/sessions/{session_id}/message", response_model=MessageResponse)
def post_message(session_id: str, body: MessageRequest, db: Session = Depends(get_db)):
    session = _load_session(db, session_id)
    result = interview.handle_message(db, session, body.text.strip())
    return MessageResponse(reply=result["reply"], done=result["done"])


@router.get("/sessions/{session_id}/summary", response_model=SessionSummary)
def get_summary(session_id: str, db: Session = Depends(get_db)):
    session = _load_session(db, session_id)
    role = get_role(session.role)

    if session.status != "completed":
        interview.finalize(db, session, role_label=role["label"])
        db.refresh(session)

    s = session.summary or {}
    return SessionSummary(
        session_id=session.id,
        candidate_name=session.candidate_name,
        role=role["label"],
        status=session.status,
        created_at=session.created_at,
        completed_at=session.completed_at,
        profile=session.resume_profile,
        focus_topics=session.focus_topics,
        overall_rating=s.get("overall_rating", "Satisfactory"),
        headline=s.get("headline", ""),
        topic_ratings=s.get("topic_ratings", []),
        strengths=s.get("strengths", []),
        areas_to_improve=s.get("areas_to_improve", []),
        narrative=s.get("narrative", ""),
        transcript=interview.transcript(session),
    )
