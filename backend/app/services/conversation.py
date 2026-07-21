"""The interviewer agent — one adaptive turn at a time.

Unlike a fixed question list, the agent reads the running conversation plus the
candidate's latest answer and *decides* what to do next:

  * strong answer  -> a brief compliment, then ADVANCE to the next topic
  * partial/weak   -> a FOLLOW_UP that probes the specific gap
  * confused       -> a FOLLOW_UP that clarifies / reframes to help them
  * plan covered   -> CONCLUDE with a closing line

Every reply is grounded in retrieved knowledge-base context, so questions stay
non-generic and factual. The agent returns structured control data (assessment +
action) alongside the natural chat message, which keeps the whole thing traceable.
"""
from __future__ import annotations

from app.services.llm import complete, complete_json

# Rough numeric mapping kept only for an internal average; the UI shows bands.
QUALITY_SCORE = {
    "strong": 9.0,
    "good": 7.5,
    "partial": 5.0,
    "weak": 3.0,
    "confused": 3.0,
    "off_topic": 1.0,
}

_PERSONA = (
    "You are Ava, a warm but sharp senior technical interviewer. You speak "
    "conversationally and concisely, like a real person in a live interview — "
    "never robotic, never a wall of text. You ground every question in the "
    "provided reference material and never reveal answers."
)


def _fmt_context(chunks: list[dict], limit: int = 3) -> str:
    if not chunks:
        return "(no context)"
    return "\n\n".join(
        f"[{c.get('source','?')}] {c.get('snippet','')[:700]}" for c in chunks[:limit]
    )


def _fmt_history(history: list[dict]) -> str:
    if not history:
        return "(conversation just started)"
    lines = []
    for turn in history[-8:]:  # keep the prompt bounded
        who = "Ava" if turn["role"] == "interviewer" else "Candidate"
        lines.append(f"{who}: {turn['text']}")
    return "\n".join(lines)


def opening_turn(
    *, role_label: str, candidate_name: str, profile: dict, topic: str, context: list[dict]
) -> str:
    """Generate the interviewer's very first message: a short greeting + Q1."""
    prompt = f"""Start a technical interview for the role of {role_label}.

Candidate: {candidate_name}
Their background — skills: {profile.get('skills')}, technologies: {profile.get('technologies')}, seniority: {profile.get('seniority')}.

First topic to assess: "{topic}"
Reference material to ground the question in:
{_fmt_context(context)}

Write a SHORT opening message (2-4 sentences max): a one-line friendly greeting
that references their background, then ONE clear first question on the topic,
grounded in the reference material and angled toward their experience. Sound
human and relaxed. Output ONLY the message text, no preamble.
"""
    return complete(prompt, system=_PERSONA)


def interview_turn(
    *,
    role_label: str,
    profile: dict,
    plan: list[str],
    history: list[dict],
    candidate_answer: str,
    current_topic: str,
    next_topic: str | None,
    current_context: list[dict],
    next_context: list[dict],
    asked_count: int,
    max_questions: int,
    followup_depth: int,
    max_followups: int,
    topics_remaining: int,
) -> dict:
    """Assess the latest answer and produce the next interviewer message."""
    must_conclude = asked_count >= max_questions or (next_topic is None and followup_depth >= max_followups)
    followups_exhausted = followup_depth >= max_followups

    guidance = f"""Decision rules:
- Assess the candidate's answer quality: one of strong, good, partial, weak, confused, off_topic.
- If the answer is strong/good: briefly acknowledge or compliment it (one short clause), then ACTION "advance" to the next topic and ask the next question.
- If it is partial/weak: ACTION "follow_up" — probe the SPECIFIC missing piece with a pointed question (unless follow-ups are exhausted).
- If it is confused/off_topic: ACTION "follow_up" — gently reframe or give a small nudge to help them, then re-ask more concretely (unless exhausted).
- Follow-ups on the current topic used: {followup_depth}/{max_followups}. {"Follow-ups are EXHAUSTED — you must advance or conclude." if followups_exhausted else ""}
- Questions asked so far: {asked_count}/{max_questions}. Topics still in the plan after this: {topics_remaining}.
- {"You MUST set action to 'conclude' now (limits reached)." if must_conclude else "If the plan is essentially covered, you may 'conclude'."}
"""

    next_block = (
        f'Next planned topic: "{next_topic}"\nReference material for the next topic:\n{_fmt_context(next_context)}'
        if next_topic
        else "There is no next topic left in the plan (only follow-ups or conclusion remain)."
    )

    prompt = f"""Role: {role_label}. Candidate seniority: {profile.get('seniority')}.
Interview plan (topics): {plan}

Conversation so far:
{_fmt_history(history)}

The candidate just answered your last question. Their answer:
\"\"\"{candidate_answer}\"\"\"

Current topic: "{current_topic}"
Reference material for the current topic (use when probing a follow-up):
{_fmt_context(current_context)}

{next_block}

{guidance}

Return STRICT JSON:
{{
  "assessment": {{"quality": "strong|good|partial|weak|confused|off_topic", "note": "<one concise sentence on why>"}},
  "action": "advance|follow_up|conclude",
  "topic": "<the topic your reply addresses>",
  "reply": "<your next chat message: a short natural reaction (compliment if deserved) + the next question OR follow-up probe OR a warm closing line if concluding. 2-4 sentences, human, no lists>"
}}
"""
    try:
        data = complete_json(prompt, system=_PERSONA)
        if isinstance(data, dict) and data.get("reply") and data.get("action"):
            action = str(data["action"]).lower()
            if action not in {"advance", "follow_up", "conclude"}:
                action = "advance"
            if must_conclude:
                action = "conclude"
            if followups_exhausted and action == "follow_up":
                action = "conclude" if next_topic is None else "advance"
            assessment = data.get("assessment") or {}
            quality = str(assessment.get("quality", "partial")).lower()
            if quality not in QUALITY_SCORE:
                quality = "partial"
            return {
                "quality": quality,
                "note": str(assessment.get("note", "")).strip(),
                "action": action,
                "topic": str(data.get("topic", current_topic)).strip() or current_topic,
                "reply": str(data["reply"]).strip(),
                "score": QUALITY_SCORE[quality],
            }
    except Exception:
        pass

    # Robust fallback keeps the interview moving.
    action = "conclude" if must_conclude else ("advance" if next_topic else "conclude")
    reply = (
        "Thanks — that's a good place to wrap up. Appreciate you walking me through your thinking!"
        if action == "conclude"
        else f"Got it, thanks. Let's shift gears — {('tell me about ' + next_topic) if next_topic else 'let us continue'}."
    )
    return {
        "quality": "partial",
        "note": "auto-assessment unavailable",
        "action": action,
        "topic": next_topic or current_topic,
        "reply": reply,
        "score": QUALITY_SCORE["partial"],
    }
