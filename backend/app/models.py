"""ORM models — the structured record of every interview.

Schema mirrors the required pipeline: a Session owns many Questions, each
Question owns one Answer. Every Question also stores the retrieved context
that produced it, giving full *traceability* (Context -> Question -> Answer).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def _uuid() -> str:
    return uuid.uuid4().hex


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    candidate_name: Mapped[str] = mapped_column(String(255), default="Candidate")
    role: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="in_progress")  # in_progress | completed

    # Resume-derived context (parsed once, reused throughout the session).
    resume_text: Mapped[str] = mapped_column(Text, default="")
    resume_profile: Mapped[dict] = mapped_column(JSON, default=dict)  # skills, techs, domains...
    focus_topics: Mapped[list] = mapped_column(JSON, default=list)  # the coverage plan

    # Adaptive-agent state: where we are in the plan and how deep we've probed.
    topic_index: Mapped[int] = mapped_column(Integer, default=0)
    followup_depth: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Final structured analysis (populated on completion).
    summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    questions: Mapped[list["Question"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Question.order_index",
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"), index=True
    )
    order_index: Mapped[int] = mapped_column(Integer)

    text: Mapped[str] = mapped_column(Text)
    topic: Mapped[str] = mapped_column(String(255), default="")
    difficulty: Mapped[str] = mapped_column(String(32), default="medium")
    kind: Mapped[str] = mapped_column(String(16), default="question")  # question | follow_up

    # Traceability: what retrieval query + KB chunks generated this question.
    retrieval_query: Mapped[str] = mapped_column(Text, default="")
    context_sources: Mapped[list] = mapped_column(JSON, default=list)  # [{source, snippet, score}]

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["InterviewSession"] = relationship(back_populates="questions")
    answer: Mapped["Answer | None"] = relationship(
        back_populates="question", cascade="all, delete-orphan", uselist=False
    )


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    question_id: Mapped[str] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), unique=True, index=True
    )
    text: Mapped[str] = mapped_column(Text)

    # Per-answer assessment produced live by the interviewer agent.
    quality: Mapped[str] = mapped_column(String(32), default="")  # strong|good|partial|weak|confused|off_topic
    score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-10 (internal)
    feedback: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    question: Mapped["Question"] = relationship(back_populates="answer")
