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
        <div className="mark">
          <span className="avatar">A</span>
          <span className="mark-name">Ava</span>
        </div>
        <h1>Let's talk through your experience.</h1>
        <p className="sub">
          A short, conversational screening — usually under ten minutes. Answer in
          your own words, and we'll ask a few follow-up questions based on what you
          share.
        </p>

        <form onSubmit={start}>
          <div className="field">
            <span className="overline">Your name</span>
            <input
              className="text-in"
              placeholder="Jordan Lee"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="field">
            <span className="overline">Role</span>
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
          </div>

          <div className="field resume">
            <span className="overline">Resume</span>
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
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                  <path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2Z" />
                </svg>
                {file ? <span className="fname">{file.name}</span> : "Attach your resume (PDF or text)"}
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
            {loading ? "Getting your interview ready…" : "Let's begin"}
          </button>
        </form>
      </div>
      <div className="setup-foot">Your responses simply help us get to know your background.</div>
    </div>
  );
}
