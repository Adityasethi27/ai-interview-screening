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

export default function Summary({ sessionId, onRestart }) {
  const [s, setS] = useState(null);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    api.getSummary(sessionId).then(setS).catch((e) => setError(e.message));
  }, [sessionId]);

  if (error) return <div className="report"><div className="err">{error}</div></div>;
  if (!s) return <div className="report loading">Compiling your assessment…</div>;

  return (
    <div className="report">
      <div className="report-top">
        <div>
          <div className="eyebrow">Assessment · {s.role}</div>
          <h1>{s.candidate_name}</h1>
          {s.headline && <p className="headline">{s.headline}</p>}
        </div>
        <div className={"band " + (BAND[s.overall_rating] || "b-mid")}>
          {s.overall_rating}
        </div>
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
            {s.strengths.length ? s.strengths.map((x, i) => <li key={i}>{x}</li>) : <li className="dim">—</li>}
          </ul>
        </section>
        <section>
          <h3>Areas to improve</h3>
          <ul className="work">
            {s.areas_to_improve.length ? s.areas_to_improve.map((x, i) => <li key={i}>{x}</li>) : <li className="dim">—</li>}
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
          {s.transcript.map((t) => (
            <div className="tx" key={t.order_index}>
              <div className="tx-meta">
                <span className="tx-topic">{t.topic}</span>
                {t.kind === "follow_up" && <span className="tx-follow">follow-up</span>}
                {t.quality && <span className="tx-q">{t.quality}</span>}
              </div>
              <p className="tx-ava"><b>Ava</b> {t.question}</p>
              {t.answer && <p className="tx-you"><b>You</b> {t.answer}</p>}
              {t.context_sources?.length > 0 && (
                <p className="tx-src">grounded in {[...new Set(t.context_sources.map((c) => c.source))].join(", ")}</p>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="report-foot">
        <button className="restart" onClick={onRestart}>Run another interview</button>
      </div>
    </div>
  );
}
