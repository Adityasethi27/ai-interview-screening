"""Fast, offline unit tests for the deterministic pieces of the pipeline.
Run with:  python -m pytest -q   (from the backend/ directory)

These avoid any network/LLM calls so they run in CI without an API key.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm import _extract_json
from app.rag.retriever import build_query
from app.services.roles import list_roles, get_role
from app.services.resume_parser import _normalise_profile, _fallback_profile


def test_extract_json_plain():
    assert _extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_fenced():
    raw = "Here you go:\n```json\n{\"score\": 8, \"feedback\": \"ok\"}\n```"
    assert _extract_json(raw) == {"score": 8, "feedback": "ok"}


def test_extract_json_embedded_list():
    raw = "Sure! [\"a\", \"b\", \"c\"] hope that helps"
    assert _extract_json(raw) == ["a", "b", "c"]


def test_build_query_includes_role_topic_and_skills():
    q = build_query(
        "backend_engineer",
        "database indexing",
        {"skills": ["SQL", "PostgreSQL"], "technologies": ["Redis"]},
    )
    assert "backend engineer" in q.lower()
    assert "database indexing" in q
    assert "PostgreSQL" in q
    assert "Redis" in q


def test_roles_registry():
    roles = list_roles()
    ids = {r["id"] for r in roles}
    assert {"ai_ml_engineer", "backend_engineer", "data_science"} <= ids
    assert get_role("backend_engineer")["label"] == "Backend Engineer"


def test_normalise_profile_bounds_and_defaults():
    p = _normalise_profile(
        {"skills": ["a"] * 30, "seniority": "wizard", "summary": "  hi "}
    )
    assert len(p["skills"]) <= 12
    assert p["seniority"] == "mid"  # invalid value falls back
    assert p["summary"] == "hi"


def test_fallback_profile_keyword_match():
    p = _fallback_profile("Experienced with Python, FastAPI and PostgreSQL.")
    assert "Python" in p["technologies"]
    assert "FastAPI" in p["technologies"]
    assert "PostgreSQL" in p["technologies"]
