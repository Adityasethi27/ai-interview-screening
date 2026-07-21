"""Pydantic request/response models — the API contract with the frontend."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RoleInfo(BaseModel):
    id: str
    label: str
    description: str


class ResumeProfile(BaseModel):
    skills: list[str] = []
    technologies: list[str] = []
    domains: list[str] = []
    seniority: str = "mid"
    summary: str = ""


class ContextSource(BaseModel):
    source: str
    snippet: str
    score: float


# ---- Session start (returns the opening chat message) ----
class StartSessionResponse(BaseModel):
    session_id: str
    role: str
    candidate_name: str
    profile: ResumeProfile
    focus_topics: list[str]
    opening: str  # the interviewer's first message


# ---- One conversational turn ----
class MessageRequest(BaseModel):
    text: str = Field(min_length=1)


class MessageResponse(BaseModel):
    reply: str
    done: bool


# ---- Final summary ----
class TopicRating(BaseModel):
    topic: str
    rating: str


class TranscriptItem(BaseModel):
    order_index: int
    topic: str
    kind: str
    question: str
    answer: str | None
    quality: str | None
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
    overall_rating: str
    headline: str
    topic_ratings: list[TopicRating]
    strengths: list[str]
    areas_to_improve: list[str]
    narrative: str
    transcript: list[TranscriptItem]
