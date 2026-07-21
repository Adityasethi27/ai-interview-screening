# Demo Video Script (~4 minutes) — side by side

A shot-by-shot script with **what to SAY** (voiceover) next to **what to SHOW/DO**
(on screen). It covers everything the assignment asks the video to demonstrate:
the complete system flow, the key features, and how the components interact.

## Pre-flight (before hitting record)
```bash
./run_dev.sh
# App:  http://localhost:5173
# Docs: http://127.0.0.1:8000/docs
```
- Have a technical resume PDF ready on the desktop.
- Zoom the browser to ~110% so text is readable on video.
- Optional: run one full interview first so the LLM responses are "warm", then
  record a second, fresh run to avoid waiting on camera.

---

## The script

| # | Time | 🎙️ SAY (voiceover) | 🖥️ SHOW / DO (screen) |
|---|------|--------------------|------------------------|
| 1 | 0:00–0:15 | "Hi, this is my submission for the AI/ML & Backend intern assignment — an AI-powered, role-based candidate screening system. The interview questions aren't predefined; they're generated live from the candidate's resume and a role-specific knowledge base using a RAG pipeline." | Setup screen visible. Move the cursor across the header and the 3-step progress bar (Candidate & Role → Interview → Summary). |
| 2 | 0:15–0:45 | "Quick architecture overview. A React frontend talks to a FastAPI backend with thin routes and a dedicated service layer. The RAG layer uses Chroma with one vector collection per role, and Gemini for embeddings and generation. Sessions are persisted in a database, and every question stores exactly what it was generated from — full traceability." | Show the **README architecture diagram**. Point at each layer: Frontend → API → Services → RAG/Chroma + SQLite → Gemini. |
| 3 | 0:45–1:10 | "Let's run it. I'll enter the candidate's name, choose the Backend Engineer role, and upload a resume. On begin, the backend parses the resume, extracts a structured profile, and selects focus topics tailored to this candidate." | Type a name → click **Backend Engineer** → **Upload PDF**, pick the resume → **Begin interview**. Let the "Analysing resume…" state show. |
| 4 | 1:10–1:35 | "Here's the resume actually influencing the interview. On the left, the system pulled out the candidate's skills, technologies, and inferred seniority — and it chose these focus topics specifically for them. Notice the topics blend the role with their real background." | Hover down the **left profile panel**: Skills chips → Technologies chips → seniority badge → the numbered **Focus topics** list. |
| 5 | 1:35–2:15 | "Now the key part — question generation. This question is grounded in the knowledge base and personalised to the candidate's own stack. And I can prove the grounding: expanding 'Retrieved context' shows the exact knowledge-base chunks, with similarity scores, that produced this question. That's the traceability — Context leads to Question." | Read the **question** aloud. Click **"▸ Retrieved context · N chunks (traceability)"** to expand. Point to a source filename and its **score**. |
| 6 | 2:15–2:45 | "I'll answer it. On submit, the system grades the answer from 0 to 10 against that same retrieved context and gives specific feedback — so questions and evaluation stay consistent." | Type a solid answer → **Submit answer**. Wait for the **score circle + feedback**. Point at the score, read one line of feedback. |
| 7 | 2:45–3:05 | "I click Next and the flow continues — each new question is aware of previous answers, so it can adapt and probe deeper. I'll move through the rest quickly." | Click **Next question →**. Briefly answer 1–2 more, clicking through. Let the progress bar advance. |
| 8 | 3:05–3:40 | "After the last answer, the system produces the final structured output: an overall score, a hire verdict, concrete strengths and areas to improve, a narrative assessment, and the full transcript — where every question still shows what it was grounded in." | Land on the **Summary** screen. Scroll slowly: score + verdict → Strengths / Areas to improve → narrative → the **transcript**, pausing on a "Grounded in:" line. |
| 9 | 3:40–4:00 | "Under the hood it's fully modular — thin API routes, a service layer for business logic, a self-contained RAG package, and relational persistence, all configured through environment variables, with Docker support and unit tests. Thanks for watching." | Open **http://127.0.0.1:8000/docs** to show the clean API. Optionally flash the repo file tree. End on the README. |

---

## Delivery tips
- **One take is fine.** If you fumble, pause two seconds and repeat the line; trim later.
- Keep the **cursor moving to whatever you're describing** — reviewers follow the mouse.
- The live LLM bits (steps 3, 5, 6) take a few seconds. Either let the loading
  state show (it reads as intentional) or record and trim the dead air.

## Three lines to be sure you say
1. "Questions are **not predefined** — resume → topics → retrieved knowledge → question."
2. "The **resume influences** topic selection, difficulty, and direction."
3. "Full **traceability**: Context → Question → Answer → Storage."

---

_After recording, paste the link into the README's `Demo video:` line and commit._
