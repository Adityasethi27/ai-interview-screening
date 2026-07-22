import { useEffect, useState } from "react";
import { api } from "../api.js";

// Map qualitative bands to a subtle color accent.
const BAND = {
  "Needs Work": "b-low",
  Developing: "b-low",
  Satisfactory: "b-mid",
  Strong: "b-high",
  Exceptional: "b-top",
};

// Per-answer quality → badge tone (green / amber / red).
const QUALITY = {
  strong: "q-good",
  good: "q-good",
  solid: "q-good",
  partial: "q-mid",
  developing: "q-mid",
  mixed: "q-mid",
  weak: "q-low",
  confused: "q-low",
  "off-topic": "q-low",
  off_topic: "q-low",
};

// Bold the short "Label: detail" lead-in so recruiters can scan.
function Bullet({ text }) {
  const i = text.indexOf(":");
  if (i > 1 && i <= 42) {
    return (
      <li>
        <strong>{text.slice(0, i)}</strong>
        {text.slice(i + 1)}
      </li>
    );
  }
  return <li>{text}</li>;
}

export default function Summary({ sessionId, onRestart }) {
  const [s, setS] = useState(null);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    api.getSummary(sessionId).then(setS).catch((e) => setError(e.message));
  }, [sessionId]);

  if (error) return <div className="report"><div className="err">{error}</div></div>;
  if (!s) return <div className="report loading">Compiling your assessment…</div>;

  const initial = (s.candidate_name || "You").trim().charAt(0).toUpperCase() || "Y";

  return (
    <div className="report">
      <div className="report-top">
        <div className="report-head-row">
          <div className="eyebrow">Assessment · {s.role}</div>
          <div className={"band " + (BAND[s.overall_rating] || "b-mid")}>
            {s.overall_rating}
          </div>
        </div>
        <h1>{s.candidate_name}</h1>
        {s.headline && <p className="headline">{s.headline}</p>}
      </div>

      {s.topic_ratings?.length > 0 && (
        <div className="ratings">
          {s.topic_ratings.map((t, i) => (
            <div className="rating-row" key={i}>
              <span className="rt-topic">{t.topic}</span>
              <span className={"rt-band " + (BAND[t.rating] || "b-mid")}>{t.rating}</span>
            </div>
          ))}
        </div>
      )}

      <div className="cols">
        <section>
          <h3>Strengths</h3>
          <ul className="good">
            {s.strengths.length
              ? s.strengths.map((x, i) => <Bullet key={i} text={x} />)
              : <li className="dim">—</li>}
          </ul>
        </section>
        <section>
          <h3>Areas to improve</h3>
          <ul className="work">
            {s.areas_to_improve.length
              ? s.areas_to_improve.map((x, i) => <Bullet key={i} text={x} />)
              : <li className="dim">—</li>}
          </ul>
        </section>
      </div>

      {s.narrative && (
        <section className="narr">
          <h3>Panel note</h3>
          <p>{s.narrative}</p>
        </section>
      )}

      <button className="toggle" onClick={() => setOpen((v) => !v)}>
        {open ? "Hide" : "Show"} full transcript ({s.transcript.length})
      </button>

      {open && (
        <div className="transcript">
          {s.transcript.map((t) => {
            const q = (t.quality || "").toLowerCase();
            const sources = t.context_sources?.length
              ? [...new Set(t.context_sources.map((c) => c.source))]
              : [];
            return (
              <div className="tx" key={t.order_index}>
                <div className="tx-meta">
                  {t.quality && (
                    <span className={"tx-q " + (QUALITY[q] || "q-mid")}>{t.quality}</span>
                  )}
                  <span className="tx-topic">{t.topic}</span>
                  {t.kind === "follow_up" && <span className="tx-follow">follow-up</span>}
                </div>

                <div className="tx-turn">
                  <span className="tx-avatar ava">A</span>
                  <p className="tx-text"><span className="tx-name">Ava</span>{t.question}</p>
                </div>

                {t.answer && (
                  <div className="tx-turn you">
                    <span className="tx-avatar you">{initial}</span>
                    <p className="tx-text"><span className="tx-name">{s.candidate_name || "You"}</span>{t.answer}</p>
                  </div>
                )}

                {sources.length > 0 && (
                  <p className="tx-src">Grounded in {sources.join(", ")}</p>
                )}
              </div>
            );
          })}
        </div>
      )}

      <div className="report-foot">
        <button className="restart" onClick={onRestart}>Run another interview</button>
      </div>
    </div>
  );
}
