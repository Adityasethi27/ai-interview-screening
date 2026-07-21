// Left rail during the interview: shows what the system extracted from the
// resume and the focus topics it chose — making the "resume influences the
// interview" behaviour visible to the user.
export default function ProfilePanel({ session, answered, total }) {
  const p = session.profile || {};
  return (
    <aside className="card profile-panel">
      <div className="candidate">
        <div className="avatar">{(session.candidate_name || "C")[0]}</div>
        <div>
          <strong>{session.candidate_name}</strong>
          <div className="muted small">{session.role.replace(/_/g, " ")}</div>
        </div>
      </div>

      <span className={"seniority " + (p.seniority || "mid")}>
        {p.seniority || "mid"} level
      </span>

      {p.summary && <p className="profile-summary">{p.summary}</p>}

      <Section title="Skills" items={p.skills} />
      <Section title="Technologies" items={p.technologies} />
      {p.domains?.length > 0 && <Section title="Domains" items={p.domains} />}

      <div className="focus">
        <h4>Focus topics</h4>
        <ol>
          {session.focus_topics.map((t, i) => (
            <li key={i} className={i < answered ? "done" : i === answered ? "current" : ""}>
              {t}
            </li>
          ))}
        </ol>
      </div>
    </aside>
  );
}

function Section({ title, items }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="chips-section">
      <h4>{title}</h4>
      <div className="chips">
        {items.map((s, i) => (
          <span className="chip" key={i}>
            {s}
          </span>
        ))}
      </div>
    </div>
  );
}
