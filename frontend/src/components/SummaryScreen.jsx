import { useEffect, useState } from "react";
import { api } from "../api.js";

const VERDICT_CLASS = {
  "strong hire": "verdict-strong",
  hire: "verdict-hire",
  borderline: "verdict-borderline",
  "no hire": "verdict-no",
};

export default function SummaryScreen({ sessionId, onRestart }) {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getSummary(sessionId).then(setSummary).catch((e) => setError(e.message));
  }, [sessionId]);

  if (error) return <div className="card error">{error}</div>;
  if (!summary) return <div className="card loading">Compiling assessment…</div>;

  const scored = summary.transcript.filter((t) => t.score != null);

  return (
    <div className="summary">
      <div className="card summary-head">
        <div>
          <h2>Interview summary</h2>
          <p className="muted">
            {summary.candidate_name} · {summary.role}
          </p>
        </div>
        <div className="score-block">
          <div className="big-score">
            {summary.overall_score != null ? summary.overall_score : "—"}
            <small>/10</small>
          </div>
          <span className={"verdict " + (VERDICT_CLASS[summary.verdict] || "")}>
            {summary.verdict}
          </span>
        </div>
      </div>

      {summary.narrative && (
        <div className="card">
          <h3>Assessment</h3>
          <p className="narrative">{summary.narrative}</p>
        </div>
      )}

      <div className="two-col">
        <div className="card">
          <h3>Strengths</h3>
          <ul className="bullets good">
            {summary.strengths.length ? (
              summary.strengths.map((s, i) => <li key={i}>{s}</li>)
            ) : (
              <li className="muted">None recorded</li>
            )}
          </ul>
        </div>
        <div className="card">
          <h3>Areas to improve</h3>
          <ul className="bullets bad">
            {summary.areas_to_improve.length ? (
              summary.areas_to_improve.map((s, i) => <li key={i}>{s}</li>)
            ) : (
              <li className="muted">None recorded</li>
            )}
          </ul>
        </div>
      </div>

      <div className="card">
        <h3>Transcript ({scored.length}/{summary.transcript.length} answered)</h3>
        <div className="transcript">
          {summary.transcript.map((t) => (
            <div className="qa" key={t.order_index}>
              <div className="qa-head">
                <span className="topic-tag">{t.topic}</span>
                <span className={"diff-tag " + t.difficulty}>{t.difficulty}</span>
                {t.score != null && (
                  <span className="qa-score">{t.score}/10</span>
                )}
              </div>
              <p className="qa-q">
                <strong>Q{t.order_index + 1}.</strong> {t.question}
              </p>
              <p className="qa-a">
                <strong>A.</strong> {t.answer || <em className="muted">No answer</em>}
              </p>
              {t.feedback && <p className="qa-feedback">💬 {t.feedback}</p>}
              {t.context_sources?.length > 0 && (
                <p className="qa-sources muted small">
                  Grounded in: {[...new Set(t.context_sources.map((c) => c.source))].join(", ")}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="center">
        <button className="primary" onClick={onRestart}>
          Run another interview
        </button>
      </div>
    </div>
  );
}
