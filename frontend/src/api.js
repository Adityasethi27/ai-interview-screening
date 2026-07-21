// Single place that talks to the backend. Uses same-origin relative URLs which
// the Vite dev server proxies to FastAPI (see vite.config.js).
const BASE = import.meta.env.VITE_API_BASE || "";

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch (_) {}
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  getRoles: () => fetch(`${BASE}/api/roles`).then(handle),

  startSession: ({ role, candidateName, resumeFile, resumeText }) => {
    const form = new FormData();
    form.append("role", role);
    form.append("candidate_name", candidateName || "Candidate");
    if (resumeFile) form.append("resume_file", resumeFile);
    if (resumeText) form.append("resume_text", resumeText);
    return fetch(`${BASE}/api/sessions`, { method: "POST", body: form }).then(handle);
  },

  nextQuestion: (sessionId) =>
    fetch(`${BASE}/api/sessions/${sessionId}/next-question`).then(handle),

  submitAnswer: (sessionId, questionId, answer) =>
    fetch(`${BASE}/api/sessions/${sessionId}/answers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: questionId, answer }),
    }).then(handle),

  getSummary: (sessionId) =>
    fetch(`${BASE}/api/sessions/${sessionId}/summary`).then(handle),
};
