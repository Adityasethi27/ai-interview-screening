import { useEffect, useState } from "react";
import { api } from "../api.js";
import ProfilePanel from "./ProfilePanel.jsx";

export default function InterviewScreen({ session, onFinished }) {
  const sessionId = session.session_id;
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState("");
  const [remaining, setRemaining] = useState(session.total_questions);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [lastEval, setLastEval] = useState(null);
  const [showSources, setShowSources] = useState(false);
  const [error, setError] = useState("");

  const total = session.total_questions;
  const answered = total - remaining;

  const loadNext = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.nextQuestion(sessionId);
      setRemaining(res.remaining);
      if (res.finished || !res.question) {
        onFinished();
        return;
      }
      setQuestion(res.question);
      setAnswer("");
      setLastEval(null);
      setShowSources(false);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNext();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const submit = async () => {
    if (answer.trim().length < 1) return;
    setSubmitting(true);
    setError("");
    try {
      const res = await api.submitAnswer(sessionId, question.id, answer.trim());
      setLastEval(res.evaluation);
      setRemaining(res.remaining);
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="interview-layout">
      <ProfilePanel session={session} answered={answered} total={total} />

      <div className="card interview-main">
        <div className="progress-row">
          <span className="pill">
            Question {Math.min(answered + 1, total)} / {total}
          </span>
          <div className="progressbar">
            <div
              className="progressbar-fill"
              style={{ width: `${(answered / total) * 100}%` }}
            />
          </div>
        </div>

        {loading && <div className="loading">Generating a grounded question…</div>}

        {!loading && question && (
          <>
            <div className="question-meta">
              <span className="topic-tag">{question.topic}</span>
              <span className={"diff-tag " + question.difficulty}>
                {question.difficulty}
              </span>
            </div>
            <h2 className="question-text">{question.text}</h2>

            {question.context_sources?.length > 0 && (
              <div className="sources">
                <button
                  className="link"
                  onClick={() => setShowSources((v) => !v)}
                >
                  {showSources ? "▾" : "▸"} Retrieved context ·{" "}
                  {question.context_sources.length} chunks (traceability)
                </button>
                {showSources && (
                  <ul className="source-list">
                    {question.context_sources.map((c, i) => (
                      <li key={i}>
                        <div className="source-head">
                          <span className="source-name">{c.source}</span>
                          <span className="source-score">
                            score {c.score.toFixed(3)}
                          </span>
                        </div>
                        <p className="source-snippet">{c.snippet.slice(0, 240)}…</p>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {!lastEval ? (
              <>
                <textarea
                  className="answer-box"
                  rows={7}
                  placeholder="Type your answer…"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  disabled={submitting}
                />
                <div className="actions">
                  <span className="muted small">
                    {answer.trim().length} chars
                  </span>
                  <button
                    className="primary"
                    onClick={submit}
                    disabled={submitting || answer.trim().length < 1}
                  >
                    {submitting ? "Evaluating…" : "Submit answer"}
                  </button>
                </div>
              </>
            ) : (
              <div className="eval">
                <div className="eval-score">
                  <div className="score-circle">{lastEval.score}</div>
                  <div>
                    <strong>Answer evaluated</strong>
                    <p className="muted">{lastEval.feedback}</p>
                  </div>
                </div>
                <button className="primary" onClick={loadNext}>
                  {remaining > 0 ? "Next question →" : "See summary →"}
                </button>
              </div>
            )}
          </>
        )}

        {error && <div className="error">{error}</div>}
      </div>
    </div>
  );
}
