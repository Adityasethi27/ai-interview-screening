"""CLI: build the vector store from the knowledge base.

Usage:
    python -m scripts.ingest_kb            # ingest all roles
    python -m scripts.ingest_kb ai_ml_engineer backend_engineer
"""
from __future__ import annotations

import sys

# Allow running as a script from the backend/ directory.
from app.config import settings  # noqa: E402
from app.rag.ingest import available_roles, ingest_role  # noqa: E402


def main(argv: list[str]) -> None:
    settings.validate()
    roles = argv or available_roles()
    if not roles:
        print("No roles found under", settings.KB_DIR)
        return
    print(f"Ingesting roles: {roles}\n")
    for role in roles:
        try:
            result = ingest_role(role)
            print(
                f"  ✓ {role}: {result['documents']} docs -> {result['chunks']} chunks "
                f"(collection '{result['collection']}')"
            )
        except Exception as exc:
            print(f"  ✗ {role}: {exc}")
    print("\nDone. Vector store at:", settings.CHROMA_DIR)


if __name__ == "__main__":
    main(sys.argv[1:])
