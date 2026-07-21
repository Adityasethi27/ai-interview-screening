"""Context construction stage.

Given the role and the parsed resume profile, decide *what to evaluate*:
a ranked list of focus topics. These topics then drive retrieval.

The LLM picks topics that sit at the intersection of (a) what the role
demands and (b) what the candidate claims — so a Backend candidate strong in
Postgres gets probed on indexing/transactions, while one strong in Kafka gets
probed on streaming/consistency. This is what makes the resume *meaningfully
influence topic selection and interview direction*.
"""
from __future__ import annotations

from app.config import settings
from app.services.llm import complete_json
from app.services.roles import get_role


def select_focus_topics(role_id: str, profile: dict) -> list[str]:
    role = get_role(role_id)
    seed = role["seed_topics"]
    n = settings.NUM_TOPICS

    prompt = f"""You are designing a technical interview for the role: "{role['label']}".

Core role topics (knowledge base coverage):
{seed}

Candidate profile:
- Skills: {profile.get('skills')}
- Technologies: {profile.get('technologies')}
- Domains: {profile.get('domains')}
- Seniority: {profile.get('seniority')}

Choose exactly {n} focus topics to evaluate this specific candidate. Rules:
- Every topic MUST be covered by the role's knowledge base (draw from / stay
  close to the core role topics list; you may specialise a topic toward the
  candidate's technologies, e.g. "database indexing in PostgreSQL").
- Prioritise topics that intersect the role with the candidate's background.
- Order from foundational to advanced.

Return STRICT JSON: a list of {n} short topic strings. Example:
["REST API design", "PostgreSQL indexing and query planning", ...]
"""
    try:
        data = complete_json(prompt)
        if isinstance(data, dict):  # tolerate {"topics": [...]}
            data = data.get("topics") or next(iter(data.values()), [])
        topics = [str(t).strip() for t in data if str(t).strip()]
        if topics:
            return topics[:n]
    except Exception:
        pass
    return seed[:n]
