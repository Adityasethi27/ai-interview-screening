"""Thin wrappers around the Gemini chat + embedding models.

Centralising model construction means the rest of the codebase never touches
API keys or model names directly — it just asks for `chat()` or `embeddings()`.
"""
from __future__ import annotations

import json
import re
import time
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.config import settings


@lru_cache
def get_llm(model: str | None = None) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model or settings.LLM_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.4,
        convert_system_message_to_human=True,
        # Disable the SDK's slow internal retry (it blocks ~35s on 429);
        # our own fast backoff + model fallback in complete() handles limits.
        max_retries=0,
    )


def _models_to_try() -> list[str]:
    """Primary model first, then fallbacks — lets us survive a single model's
    daily free-tier cap by rolling over to another model."""
    chain = [settings.LLM_MODEL] + settings.LLM_FALLBACKS
    seen, out = set(), []
    for m in chain:
        m = m.strip()
        if m and m not in seen:
            seen.add(m)
            out.append(m)
    return out


@lru_cache
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
    )


def _content_to_text(content) -> str:
    """Gemini may return a plain string or a list of content parts."""
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return str(content)


def complete(prompt: str, system: str | None = None) -> str:
    """Single-shot completion returning plain text, with backoff on rate limits."""
    messages = []
    if system:
        messages.append(("system", system))
    messages.append(("human", prompt))

    last_exc: Exception | None = None
    for model in _models_to_try():
        for attempt in range(2):
            try:
                resp = get_llm(model).invoke(messages)
                return _content_to_text(resp.content).strip()
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                msg = str(exc)
                is_rate = "RESOURCE_EXHAUSTED" in msg or "429" in msg
                if is_rate and attempt == 0:
                    time.sleep(2)  # brief backoff, then one more try on this model
                    continue
                # Rate-limited again -> roll over to the next fallback model.
                # Any other (hard) error also breaks to the next model.
                break
    raise last_exc  # type: ignore[misc]


def complete_json(prompt: str, system: str | None = None) -> dict | list:
    """Completion that is expected to return JSON. Robust to code fences / prose."""
    raw = complete(prompt, system=system)
    return _extract_json(raw)


def _extract_json(raw: str):
    # Strip ```json ... ``` fences if present.
    fenced = re.search(r"```(?:json)?\s*(.*?)```", raw, re.DOTALL)
    candidate = fenced.group(1) if fenced else raw
    candidate = candidate.strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Fall back to the first {...} or [...] block.
        match = re.search(r"(\{.*\}|\[.*\])", candidate, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise
