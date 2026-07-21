"""Question generation — the RAG 'generation' step.

A question is produced from THREE inputs, keeping it grounded and personalised:
  1. Retrieved knowledge-base context (grounding — avoids hallucinated facts).
  2. The candidate's resume profile (personalisation — difficulty & angle).
  3. The conversation so far (adaptivity — avoid repetition, optionally follow
     up on a weak previous answer).
"""
from __future__ import annotations

from app.services.llm import complete_json

_SYSTEM = (
    "You are a senior technical interviewer. You ask precise, non-generic "
    "questions grounded strictly in the provided reference material. You never "
    "reveal the answer."
)


def _difficulty_for(seniority: str) -> str:
    return {"junior": "easy-to-medium", "mid": "medium", "senior": "medium-to-hard"}.get(
        seniority, "medium"
    )


def generate_question(
    *,
    role_label: str,
    topic: str,
    profile: dict,
    context_chunks: list[dict],
    previous_qa: list[dict],
    order_index: int,
) -> dict:
    context_block = "\n\n".join(
        f"[Source: {c['source']}]\n{c['snippet'][:900]}" for c in context_chunks
    ) or "(no context retrieved)"

    history_block = (
        "\n".join(
            f"Q{i+1} ({qa.get('topic','')}): {qa['question']}\nA: {qa.get('answer','(unanswered)')}"
            for i, qa in enumerate(previous_qa)
        )
        or "(this is the first question)"
    )

    target_difficulty = _difficulty_for(profile.get("seniority", "mid"))

    prompt = f"""Design ONE interview question.

ROLE: {role_label}
TOPIC TO ASSESS: {topic}
TARGET DIFFICULTY: {target_difficulty}

CANDIDATE PROFILE:
- Skills: {profile.get('skills')}
- Technologies: {profile.get('technologies')}
- Seniority: {profile.get('seniority')}

REFERENCE MATERIAL (ground your question in these concepts — do NOT invent
facts beyond them):
{context_block}

INTERVIEW SO FAR (do not repeat these):
{history_block}

Requirements for the question:
- Grounded in the reference material above.
- Tailored to the candidate: where natural, frame it around their technologies.
- Tests conceptual understanding AND applied reasoning, not recall of a definition.
- Specific and answerable in a short paragraph. Avoid vague/generic prompts.
- If a previous answer was weak on a related idea, you may probe deeper.

Return STRICT JSON:
{{"question": "<the question>", "topic": "{topic}", "difficulty": "easy|medium|hard", "rationale": "<1 sentence: why this question for this candidate>"}}
"""
    try:
        data = complete_json(prompt, system=_SYSTEM)
        if isinstance(data, dict) and data.get("question"):
            diff = str(data.get("difficulty", "medium")).lower()
            if diff not in {"easy", "medium", "hard"}:
                diff = "medium"
            return {
                "question": str(data["question"]).strip(),
                "topic": str(data.get("topic", topic)).strip() or topic,
                "difficulty": diff,
                "rationale": str(data.get("rationale", "")).strip(),
            }
    except Exception:
        pass
    # Fallback keeps the interview flowing even if generation fails.
    return {
        "question": f"Explain the key ideas behind {topic} and how you'd apply "
        f"them in a real {role_label} scenario.",
        "topic": topic,
        "difficulty": "medium",
        "rationale": "fallback question",
    }
