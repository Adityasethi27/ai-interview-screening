"""Final holistic evaluation.

Instead of a single number, the outcome is a qualitative band (an adjective the
candidate can be told), backed by per-topic ratings, strengths, gaps and a short
narrative — grounded in the actual answers given.
"""
from __future__ import annotations

from app.services.llm import complete_json

# Ordered from lowest to highest; used for the deterministic fallback band.
BANDS = ["Needs Work", "Developing", "Satisfactory", "Strong", "Exceptional"]


def _band_from_score(avg: float | None) -> str:
    if avg is None:
        return "Satisfactory"
    if avg < 3:
        return "Needs Work"
    if avg < 5:
        return "Developing"
    if avg < 6.75:
        return "Satisfactory"
    if avg < 8.25:
        return "Strong"
    return "Exceptional"


def build_summary(*, role_label: str, profile: dict, transcript: list[dict]) -> dict:
    scored = [t for t in transcript if t.get("score") is not None]
    avg = round(sum(t["score"] for t in scored) / len(scored), 2) if scored else None
    fallback_band = _band_from_score(avg)

    qa_block = "\n\n".join(
        f"[{t.get('kind','question')}] Topic: {t['topic']}\n"
        f"Ava: {t['question']}\n"
        f"Candidate: {t.get('answer') or '(no answer)'}\n"
        f"Live assessment: {t.get('quality')} — {t.get('feedback')}"
        for t in transcript
    )

    prompt = f"""You are the hiring panel writing up a technical interview.

ROLE: {role_label}
CANDIDATE PROFILE: {profile}

FULL TRANSCRIPT (with the interviewer's live per-answer assessments):
{qa_block}

Write a fair, evidence-based assessment. Use a QUALITATIVE overall rating chosen
from exactly one of: {BANDS} (pick the single best fit).

Return STRICT JSON:
{{
  "overall_rating": "one of {BANDS}",
  "headline": "<one vivid sentence summarising the candidate's performance>",
  "topic_ratings": [{{"topic": "<topic>", "rating": "one of {BANDS}"}}, ...],
  "strengths": ["<2-4 items. Each MUST start with a 2-4 word label, then ': ', then one concrete sentence citing an answer. e.g. 'Async fundamentals: explained the event loop and where asyncio helps'>"],
  "areas_to_improve": ["<2-4 items, same 'Short label: one concrete sentence' format>"],
  "narrative": "<3-4 sentences referencing concrete moments in the interview>"
}}
"""
    fallback = {
        "overall_rating": fallback_band,
        "headline": "",
        "topic_ratings": [],
        "strengths": [],
        "areas_to_improve": [],
        "narrative": "Summary generation was unavailable; rating derived from live assessments.",
    }
    try:
        data = complete_json(prompt)
        if not isinstance(data, dict):
            data = fallback
    except Exception:
        data = fallback

    def _as_list(v):
        return [x for x in v if x] if isinstance(v, list) else []

    rating = str(data.get("overall_rating", fallback_band))
    if rating not in BANDS:
        rating = fallback_band

    topic_ratings = []
    for tr in _as_list(data.get("topic_ratings")):
        if isinstance(tr, dict) and tr.get("topic"):
            r = str(tr.get("rating", "Satisfactory"))
            topic_ratings.append({"topic": str(tr["topic"]), "rating": r if r in BANDS else "Satisfactory"})

    return {
        "overall_rating": rating,
        "overall_score": avg,  # internal, not shown prominently
        "headline": str(data.get("headline", "")).strip(),
        "topic_ratings": topic_ratings,
        "strengths": [str(x).strip() for x in _as_list(data.get("strengths"))],
        "areas_to_improve": [str(x).strip() for x in _as_list(data.get("areas_to_improve"))],
        "narrative": str(data.get("narrative", "")).strip(),
    }
