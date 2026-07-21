"""Thin wrappers around the Gemini chat + embedding models.

Centralising model construction means the rest of the codebase never touches
API keys or model names directly — it just asks for `chat()` or `embeddings()`.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.config import settings


@lru_cache
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.4,
        convert_system_message_to_human=True,
    )


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
    """Single-shot completion returning plain text."""
    messages = []
    if system:
        messages.append(("system", system))
    messages.append(("human", prompt))
    resp = get_llm().invoke(messages)
    return _content_to_text(resp.content).strip()


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
