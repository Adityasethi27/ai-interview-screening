import { useEffect, useRef, useState } from "react";
import { api } from "../api.js";

export default function Setup({ onStart }) {
  const [roles, setRoles] = useState([]);
  const [role, setRole] = useState("");
  const [name, setName] = useState("");
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [mode, setMode] = useState("file");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef();

  useEffect(() => {
    api.getRoles().then((r) => {
      setRoles(r);
      if (r[0]) setRole(r[0].id);
    }).catch((e) => setError(e.message));
  }, []);

  const ready = role && ((mode === "file" && file) || (mode === "text" && text.trim().length > 30));

  const start = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const s = await api.startSession({
        role,
        candidateName: name,
        resumeFile: mode === "file" ? file : null,
        resumeText: mode === "text" ? text : null,
      });
      onStart(s);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="setup-wrap">
      <div className="setup-card">
        <div className="mark">av<span>·</span>a</div>
        <h1>Technical screening</h1>
        <p className="sub">
          A short, adaptive interview. Ava reads your resume, asks grounded
          questions, and follows up where it matters.
        </p>

        <form onSubmit={start}>
          <input
            className="text-in"
            placeholder="Your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <div className="seg">
            {roles.map((r) => (
              <button
                type="button"
                key={r.id}
                className={role === r.id ? "on" : ""}
                onClick={() => setRole(r.id)}
                title={r.description}
              >
                {r.label}
              </button>
            ))}
          </div>

          <div className="resume">
            <div className="resume-tabs">
              <button type="button" className={mode === "file" ? "on" : ""} onClick={() => setMode("file")}>
                Upload PDF
              </button>
              <button type="button" className={mode === "text" ? "on" : ""} onClick={() => setMode("text")}>
                Paste text
              </button>
            </div>
            {mode === "file" ? (
              <button type="button" className="drop" onClick={() => fileRef.current?.click()}>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".pdf,.txt"
                  hidden
                  onChange={(e) => setFile(e.target.files[0] || null)}
                />
                {file ? <span className="fname">{file.name}</span> : "Choose a resume file"}
              </button>
            ) : (
              <textarea
                className="paste"
                rows={5}
                placeholder="Paste your resume text…"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            )}
          </div>

          {error && <div className="err">{error}</div>}

          <button className="go" disabled={!ready || loading}>
            {loading ? "Preparing your interview…" : "Start interview"}
          </button>
        </form>
      </div>
      <div className="setup-foot">Grounded in a role-specific knowledge base · RAG + Gemini</div>
    </div>
  );
}
