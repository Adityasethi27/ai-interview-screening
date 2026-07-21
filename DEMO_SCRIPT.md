# Demo Video Script (~3–4 minutes)

A tight walkthrough that hits every requirement the assignment asks the video to
show: **complete system flow, key features, and how components interact.**

## Before recording
```bash
./run_dev.sh
# Frontend: http://localhost:5173   Backend docs: http://127.0.0.1:8000/docs
```
Have a resume PDF ready (any technical resume works).

---

### 0:00 — Intro (15s)
"This is an AI-powered, role-based candidate screening system. It runs a
technical interview where the questions are generated live from the candidate's
resume and a role-specific knowledge base using a RAG pipeline."

### 0:15 — Architecture (30s)
Show the README architecture diagram. Call out the four layers: **React
frontend → FastAPI (thin routes) → service layer → RAG (Chroma) + SQLite**, all
talking to **Gemini** for generation and embeddings.

### 0:45 — Setup / Candidate Entry (30s)
- Enter a candidate name, pick a **role**.
- Upload the resume PDF and click **Begin interview**.
- Narrate: "The backend parses the resume, extracts a structured profile, and
  selects focus topics at the intersection of the role and this candidate's
  background."

### 1:15 — Resume influence (25s)
On the interview screen, point to the **left profile panel**: extracted skills,
technologies, inferred seniority, and the **focus topics** it chose. Emphasise
that these topics are personalised to the resume.

### 1:40 — Grounded question + traceability (40s)
- Read the first question — note it references the candidate's own tech.
- Expand **"Retrieved context · N chunks (traceability)"** to show the exact
  knowledge-base chunks (with similarity scores) that produced the question.
- Narrate: "Every question is grounded in retrieved material and stores exactly
  what it was generated from."

### 2:20 — Answer + live grading (30s)
Type an answer, submit, and show the **score + feedback**. Mention grading is
done against the same retrieved context. Click **Next question**; note the flow
is aware of previous answers.

### 2:50 — Summary / Final output (40s)
Answer through to the end (or click through) to reach the **Summary**: overall
score, verdict, strengths, areas to improve, narrative, and the full traceable
transcript.

### 3:30 — Wrap (20s)
Optionally open `http://127.0.0.1:8000/docs` to show the clean API surface and
mention persistence (SQLite), env-var configuration, and Docker support.
"Everything is modular: thin API routes, a dedicated service layer, a
self-contained RAG package, and relational persistence."

---

## Key lines to make sure you say
- "Questions are **not predefined** — they're generated from resume → topics →
  retrieved knowledge → question."
- "The **resume influences** topic selection, difficulty, and direction."
- "Full **traceability**: Context → Question → Answer → Storage."
