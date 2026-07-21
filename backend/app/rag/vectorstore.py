"""Chroma-backed vector store, one collection per role.

Keeping collections per-role means retrieval is naturally scoped to the
knowledge base that matters for the selected job — a Backend interview never
retrieves from the Data-Science corpus.
"""
from __future__ import annotations

from functools import lru_cache

from langchain_chroma import Chroma

from app.config import settings
from app.services.llm import get_embeddings


def collection_name(role: str) -> str:
    return f"{settings.COLLECTION_PREFIX}{role}"


@lru_cache
def get_store(role: str) -> Chroma:
    return Chroma(
        collection_name=collection_name(role),
        persist_directory=settings.CHROMA_DIR,
        embedding_function=get_embeddings(),
    )
