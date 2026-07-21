"""Evaluation logic: per-answer grading and the final session analysis.

Grading is grounded in the same retrieved context that produced the question,
so scoring is consistent with what the candidate was actually asked about.
"""
from __future__ import annotations

from app.services.llm import complete_json

_GRADER_SYSTEM = (
    "You are a fair, calibrated technical interviewer grading a candidate's "
    "answer against reference material. Be constructive and specific."
)


def evaluate_answer(
    *, question: str, answer: str, topic: str, context_chunks: list[dict]
) -> dict:
    context_block = "\n\n".join(c["snippet"][:700] for c in context_chunks) or "(none)"
    prompt = f"""Grade the candidate's answer.

TOPIC: {topic}
QUESTION: {question}
CANDIDATE ANSWER: \"\"\"{answer}\"\"\"

REFERENCE MATERIAL (ground truth):
{context_block}

Score 0-10 (10 = complete, correct, well-reasoned; 0 = empty/incorrect).
Give 1-2 sentences of specific, constructive feedback.

Return STRICT JSON: {{"score": <number 0-10>, "feedback": "<text>"}}
"""
    try:
        data = complete_json(prompt, system=_GRADER_SYSTEM)
        if isinstance(data, dict):
            score = float(data.get("score", 0))
            score = max(0.0, min(10.0, score))
            return {"score": round(score, 1), "feedback": str(data.get("feedback", "")).strip()}
    except Exception:
        pass
    return {"score": None, "feedback": "Automatic grading unavailable for this answer."}


def build_summary(*, role_label: str, profile: dict, transcript: list[dict]) -> dict:
    scored = [t for t in transcript if t.get("score") is not None]
    overall = round(sum(t["score"] for t in scored) / len(scored), 2) if scored else None

    qa_block = "\n\n".join(
        f"Topic: {t['topic']} (difficulty {t['difficulty']})\n"
        f"Q: {t['question']}\nA: {t.get('answer') or '(no answer)'}\n"
        f"Score: {t.get('score')}"
        for t in transcript
    )

    prompt = f"""Write a structured assessment of this technical interview.

ROLE: {role_label}
CANDIDATE PROFILE: {profile}
OVERALL AVERAGE SCORE: {overall}

TRANSCRIPT:
{qa_block}

Return STRICT JSON with keys:
- "verdict": one of "strong hire", "hire", "borderline", "no hire".
- "strengths": list of 2-4 specific strengths shown.
- "areas_to_improve": list of 2-4 specific gaps.
- "narrative": a 3-4 sentence overall assessment referencing concrete answers.
"""
    fallback = {
        "verdict": "borderline",
        "strengths": [],
        "areas_to_improve": [],
        "narrative": "Summary generation was unavailable; see per-question scores.",
    }
    try:
        data = complete_json(prompt)
        if not isinstance(data, dict):
            data = fallback
    except Exception:
        data = fallback

    def _as_list(v):
        return [str(x).strip() for x in v if str(x).strip()] if isinstance(v, list) else []

    return {
        "overall_score": overall,
        "verdict": str(data.get("verdict", "borderline")),
        "strengths": _as_list(data.get("strengths")),
        "areas_to_improve": _as_list(data.get("areas_to_improve")),
        "narrative": str(data.get("narrative", "")).strip(),
    }
