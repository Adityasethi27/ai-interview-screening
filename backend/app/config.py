"""Central configuration, sourced entirely from environment variables.

Keeping every tunable in one place (and out of the code) satisfies the
"configuration through environment variables" requirement and makes the
service portable across local / Docker / cloud deployments.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load a local .env if present (no-op in production where env is injected).
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent  # .../backend


class Settings:
    # --- LLM / embeddings (Google Gemini) ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-flash-latest")
    # Fallback models tried (in order) when the primary hits its daily free-tier cap.
    LLM_FALLBACKS: list[str] = os.getenv(
        "LLM_FALLBACKS", "gemini-2.0-flash,gemini-2.5-flash,gemini-flash-lite-latest"
    ).split(",")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")

    # --- Vector store (Chroma, persisted on disk) ---
    CHROMA_DIR: str = os.getenv("CHROMA_DIR", str(BASE_DIR / "storage" / "chroma"))
    COLLECTION_PREFIX: str = os.getenv("COLLECTION_PREFIX", "kb_")

    # --- Relational store (SQLite by default, swappable via URL) ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'storage' / 'app.db'}"
    )

    # --- Knowledge base ---
    KB_DIR: str = os.getenv("KB_DIR", str(BASE_DIR / "knowledge_base"))

    # --- RAG tuning ---
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K", "5"))

    # --- Interview behaviour (adaptive conversational agent) ---
    # Target number of distinct topics to walk through (the "coverage plan").
    NUM_TOPICS: int = int(os.getenv("NUM_TOPICS", "4"))
    # Hard cap on total interviewer questions (topics + follow-ups) so a session ends.
    MAX_QUESTIONS: int = int(os.getenv("MAX_QUESTIONS", "6"))
    # Max consecutive follow-up probes on a single topic before moving on.
    MAX_FOLLOWUPS_PER_TOPIC: int = int(os.getenv("MAX_FOLLOWUPS_PER_TOPIC", "2"))

    # --- API ---
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    def validate(self) -> None:
        if not self.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and fill it in."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Ensure storage directories exist at import time.
Path(settings.CHROMA_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.DATABASE_URL.replace("sqlite:///", "")).parent.mkdir(
    parents=True, exist_ok=True
) if settings.DATABASE_URL.startswith("sqlite") else None
