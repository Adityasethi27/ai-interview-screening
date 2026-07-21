# Knowledge Base

Each subdirectory is a **role-specific corpus** that becomes one vector-store
collection. The retriever is scoped per role, so an interview only ever draws
context from the matching corpus.

```
knowledge_base/
├── ai_ml_engineer/     -> collection kb_ai_ml_engineer
├── backend_engineer/   -> collection kb_backend_engineer
└── data_science/       -> collection kb_data_science
```

## What's included
The bundled `.md` files are **original, concept-accurate notes** written for this
project so the RAG pipeline is grounded and fully runnable out of the box, without
redistributing copyrighted textbooks.

## Using the assignment's recommended textbooks
The pipeline ingests **`.pdf`, `.md`, and `.txt`** transparently. To ground the
interview on the recommended books instead (e.g. *Machine Learning* — Tom Mitchell,
*The Hundred-Page Machine Learning Book* — Andriy Burkov), simply drop the PDFs
into the relevant role folder and re-run ingestion:

```bash
cp "Hundred-Page-ML-Book.pdf" backend/knowledge_base/ai_ml_engineer/
python -m scripts.ingest_kb ai_ml_engineer
```

No code changes are required — chunking, embedding, and retrieval all work the
same on the added documents.

## Ingestion
```bash
python -m scripts.ingest_kb                 # all roles
python -m scripts.ingest_kb backend_engineer  # a single role
```
