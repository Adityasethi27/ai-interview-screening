"""Pydantic request/response models — the API contract with the frontend."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ---- Roles ----
class RoleInfo(BaseModel):
    id: str
    label: str
    description: str


# ---- Resume profile ----
class ResumeProfile(BaseModel):
    skills: list[str] = []
    technologies: list[str] = []
    domains: list[str] = []
    seniority: str = "mid"
    summary: str = ""


# ---- Session lifecycle ----
class StartSessionResponse(BaseModel):
    session_id: str
    role: str
    candidate_name: str
    profile: ResumeProfile
    focus_topics: list[str]
    total_questions: int


class ContextSource(BaseModel):
    source: str
    snippet: str
    score: float


class QuestionOut(BaseModel):
    id: str
    order_index: int
    text: str
    topic: str
    difficulty: str
    retrieval_query: str = ""
    context_sources: list[ContextSource] = []
    answered: bool = False


class NextQuestionResponse(BaseModel):
    session_id: str
    question: QuestionOut | None
    remaining: int
    finished: bool


class SubmitAnswerRequest(BaseModel):
    question_id: str
    answer: str = Field(min_length=1)


class AnswerEvaluation(BaseModel):
    score: float
    feedback: str


class SubmitAnswerResponse(BaseModel):
    evaluation: AnswerEvaluation
    remaining: int
    finished: bool


# ---- Final summary ----
class QAItem(BaseModel):
    order_index: int
    topic: str
    difficulty: str
    question: str
    answer: str | None
    score: float | None
    feedback: str | None
    context_sources: list[ContextSource] = []


class SessionSummary(BaseModel):
    session_id: str
    candidate_name: str
    role: str
    status: str
    created_at: datetime
    completed_at: datetime | None
    profile: ResumeProfile
    focus_topics: list[str]
    overall_score: float | None
    verdict: str
    strengths: list[str]
    areas_to_improve: list[str]
    narrative: str
    transcript: list[QAItem]
