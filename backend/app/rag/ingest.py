"""Knowledge ingestion: load role docs -> chunk -> embed -> persist in Chroma.

Design choices (documented for the reviewer):
  * RecursiveCharacterTextSplitter with overlap preserves local context across
    chunk boundaries so a retrieved chunk rarely cuts a concept in half.
  * Chunk size ~1000 chars (~250 tokens) balances retrieval precision against
    keeping enough surrounding context for grounded question generation.
  * Each chunk keeps `source` + `topic` metadata for traceability and so the
    UI can show *where* a question came from.
"""
from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.rag.vectorstore import get_store

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None


def _read_pdf(path: Path) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf is required to ingest PDF knowledge sources.")
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _load_documents(role_dir: Path) -> list[Document]:
    docs: list[Document] = []
    for path in sorted(role_dir.rglob("*")):
        if path.is_dir():
            continue
        if path.suffix.lower() in {".md", ".txt"}:
            text = _read_text(path)
        elif path.suffix.lower() == ".pdf":
            text = _read_pdf(path)
        else:
            continue
        if text.strip():
            docs.append(Document(page_content=text, metadata={"source": path.name}))
    return docs


def ingest_role(role: str, reset: bool = True) -> dict:
    """Ingest every document under knowledge_base/<role>/ into the role collection."""
    role_dir = Path(settings.KB_DIR) / role
    if not role_dir.exists():
        raise FileNotFoundError(f"No knowledge base directory for role '{role}': {role_dir}")

    documents = _load_documents(role_dir)
    if not documents:
        raise FileNotFoundError(f"No .md/.txt/.pdf documents found in {role_dir}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(documents)

    # Derive a coarse topic tag from the source filename for nicer traceability.
    for ch in chunks:
        stem = Path(ch.metadata.get("source", "")).stem.replace("_", " ").replace("-", " ")
        ch.metadata["topic"] = stem.title()

    store = get_store(role)
    if reset:
        try:
            store.reset_collection()
        except Exception:
            pass  # fresh collection

    store.add_documents(chunks)
    return {
        "role": role,
        "documents": len(documents),
        "chunks": len(chunks),
        "collection": store._collection.name,  # type: ignore[attr-defined]
    }


def available_roles() -> list[str]:
    kb = Path(settings.KB_DIR)
    return sorted(p.name for p in kb.iterdir() if p.is_dir()) if kb.exists() else []
