# Demo Video Script (~3–4 minutes) — side by side

A shot-by-shot script with **what to SAY** (voiceover) next to **what to SHOW/DO**
(on screen). Covers everything the assignment asks the video to demonstrate: the
complete system flow, the key features, and how the components interact.

## Pre-flight (before hitting record)
```bash
./run_dev.sh
# App:  http://localhost:5173
# Docs: http://127.0.0.1:8000/docs
```
- Have a technical resume PDF (or text) ready.
- Zoom the browser to ~110% so text is readable on video.
- **Warm-up run first:** do one full interview, then record a fresh one — this
  avoids waiting on model latency, and (importantly) confirms you have Gemini
  quota left today. If turns get slow or the final report says *"rating derived
  from live assessments"*, your free-tier daily quota is exhausted — see the
  README's free-tier note (use a billing-enabled key, or wait for reset).

---

## The script

| # | Time | 🎙️ SAY (voiceover) | 🖥️ SHOW / DO (screen) |
|---|------|--------------------|------------------------|
| 1 | 0:00–0:15 | "This is my submission for the AI/ML & Backend intern assignment — an AI-powered candidate screening system. Instead of a fixed quiz, it runs a live, adaptive interview with an agent called Ava, whose questions come from the candidate's resume and a role-specific knowledge base via RAG." | The minimal setup screen. Move the cursor across the title and the role options. |
| 2 | 0:15–0:45 | "Architecture: a React chat frontend talks to a FastAPI backend with thin routes and a service layer. The RAG layer uses Chroma with one vector collection per role, and Gemini for embeddings and generation. Everything persists to a database, and each question stores exactly what it was grounded in." | Show the **README architecture diagram**. Point at each layer: Frontend → API → Services → RAG/Chroma + SQLite → Gemini. |
| 3 | 0:45–1:05 | "Let's run it. I enter a name, pick the Backend Engineer role, and give it my resume. On start, the backend parses the resume, extracts a structured profile, and builds a personalised topic plan." | Type a name → select **Backend Engineer** → **Upload PDF** (or Paste text) → **Start interview**. Let the "Preparing…" state show. |
| 4 | 1:05–1:35 | "Ava opens with a greeting that references my background, then a first question grounded in the knowledge base and angled at my stack — here, FastAPI. Notice it's a real conversation, not a form." | The chat loads; Ava's opening message types out. Read/point to how it references the candidate's technologies. |
| 5 | 1:35–2:20 | "Now the key behaviour — it's adaptive. When I give a strong, on-topic answer, Ava acknowledges it and moves to the next topic. Watch what happens when I'm vague instead…" | Type a solid answer → send (show the typing dots). Ava compliments + advances. Then on the next question type a deliberately **weak** answer (e.g. "caching just makes things faster"). |
| 6 | 2:20–2:45 | "…it doesn't just move on — it asks a targeted follow-up to probe the gap, exactly like a real interviewer. Follow-ups are capped so the session always ends." | Show Ava's **follow-up** question drilling into the weak answer. Answer it properly this time; Ava advances. |
| 7 | 2:45–3:20 | "After a few topics it wraps up and produces a qualitative assessment: an overall rating band, per-topic ratings, concrete strengths and gaps, and a panel narrative — plus the full transcript, where each turn shows what it was grounded in." | Click **See your assessment →**. Scroll the report: rating band → per-topic ratings → strengths / areas to improve → panel note → expand **Show full transcript** and point to a "grounded in …" line. |
| 8 | 3:20–3:45 | "Under the hood it's modular and grounded: thin API routes, a conversation agent that assesses each answer and decides advance-vs-follow-up, a self-contained RAG package, and SQLite persistence — all configured through environment variables, with Docker and tests." | Open **http://127.0.0.1:8000/docs** to show the clean API (sessions, message, summary). Optionally flash the repo file tree. |

---

## Delivery tips
- **One take is fine.** If you fumble, pause two seconds and repeat the line; trim later.
- Keep the **cursor on whatever you're describing** — reviewers follow the mouse.
- Steps 3, 5, 6 make live model calls (a few seconds each). Let the typing dots
  show, or trim the wait in editing.
- To reliably show a follow-up, give one clearly weak/one-line answer on purpose.

## Three lines to be sure you say
1. "Questions are **not predefined** — resume → topic plan → retrieved knowledge → live question."
2. "It's **adaptive**: compliment and advance on a strong answer, probe with a **follow-up** on a weak one."
3. "Full **traceability** and a **qualitative** final assessment."

---

_After recording, paste the link into the README's `Demo video:` line and commit._
