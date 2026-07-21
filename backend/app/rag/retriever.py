"""Retrieval mechanism: build resume+role-aware queries, fetch grounded chunks.

The retriever is deliberately *query-aware of the candidate*. Instead of a
single generic "backend engineer questions" query, we construct one focused
query per topic that fuses:
    role  +  topic  +  the candidate's own skills/technologies
so the retrieved context (and therefore the questions) are personalised.
"""
from __future__ import annotations

from app.config import settings
from app.rag.vectorstore import get_store


def build_query(role: str, topic: str, profile: dict) -> str:
    """Fuse role, topic and resume signals into a single retrieval query."""
    skills = ", ".join((profile.get("skills") or [])[:6])
    techs = ", ".join((profile.get("technologies") or [])[:6])
    role_label = role.replace("_", " ")
    parts = [f"{role_label} interview concept: {topic}."]
    if skills:
        parts.append(f"Candidate skills: {skills}.")
    if techs:
        parts.append(f"Technologies: {techs}.")
    parts.append("Explain core principles, trade-offs and applied usage.")
    return " ".join(parts)


def retrieve(role: str, query: str, k: int | None = None) -> list[dict]:
    """Return the top-k grounded chunks with source + similarity score."""
    store = get_store(role)
    k = k or settings.RETRIEVAL_K
    results = store.similarity_search_with_relevance_scores(query, k=k)
    out: list[dict] = []
    for doc, score in results:
        out.append(
            {
                "source": doc.metadata.get("source", "unknown"),
                "topic": doc.metadata.get("topic", ""),
                "snippet": doc.page_content.strip(),
                "score": round(float(score), 4),
            }
        )
    return out


def retrieve_for_topic(role: str, topic: str, profile: dict) -> tuple[str, list[dict]]:
    query = build_query(role, topic, profile)
    return query, retrieve(role, query)
