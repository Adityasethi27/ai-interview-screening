import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function SetupScreen({ onStarted }) {
  const [roles, setRoles] = useState([]);
  const [role, setRole] = useState("");
  const [candidateName, setCandidateName] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeText, setResumeText] = useState("");
  const [mode, setMode] = useState("file"); // "file" | "text"
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getRoles()
      .then((r) => {
        setRoles(r);
        if (r[0]) setRole(r[0].id);
      })
      .catch((e) => setError("Could not load roles: " + e.message));
  }, []);

  const canSubmit =
    role && ((mode === "file" && resumeFile) || (mode === "text" && resumeText.trim().length > 30));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const s = await api.startSession({
        role,
        candidateName,
        resumeFile: mode === "file" ? resumeFile : null,
        resumeText: mode === "text" ? resumeText : null,
      });
      onStarted(s);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card setup">
      <h2>Start a screening</h2>
      <p className="muted">
        Upload a resume and pick a role. The system parses the resume, selects
        focus topics, and generates a grounded interview from the role's
        knowledge base.
      </p>

      <form onSubmit={submit}>
        <label className="field">
          <span>Candidate name</span>
          <input
            type="text"
            placeholder="e.g. Aditya Sethi"
            value={candidateName}
            onChange={(e) => setCandidateName(e.target.value)}
          />
        </label>

        <label className="field">
          <span>Target role</span>
          <div className="role-grid">
            {roles.map((r) => (
              <button
                type="button"
                key={r.id}
                className={"role-option" + (role === r.id ? " selected" : "")}
                onClick={() => setRole(r.id)}
              >
                <strong>{r.label}</strong>
                <small>{r.description}</small>
              </button>
            ))}
          </div>
        </label>

        <div className="field">
          <span>Resume</span>
          <div className="tabs">
            <button
              type="button"
              className={mode === "file" ? "active" : ""}
              onClick={() => setMode("file")}
            >
              Upload PDF
            </button>
            <button
              type="button"
              className={mode === "text" ? "active" : ""}
              onClick={() => setMode("text")}
            >
              Paste text
            </button>
          </div>

          {mode === "file" ? (
            <label className="dropzone">
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={(e) => setResumeFile(e.target.files[0] || null)}
              />
              {resumeFile ? (
                <span className="file-name">📄 {resumeFile.name}</span>
              ) : (
                <span className="muted">Click to select a PDF or .txt resume</span>
              )}
            </label>
          ) : (
            <textarea
              rows={8}
              placeholder="Paste the resume text here..."
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
            />
          )}
        </div>

        {error && <div className="error">{error}</div>}

        <button className="primary" disabled={!canSubmit || loading}>
          {loading ? "Analysing resume & building interview…" : "Begin interview"}
        </button>
      </form>
    </div>
  );
}
