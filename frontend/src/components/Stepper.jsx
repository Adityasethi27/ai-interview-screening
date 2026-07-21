const STEPS = [
  { id: "setup", label: "Candidate & Role" },
  { id: "interview", label: "Interview" },
  { id: "summary", label: "Summary" },
];

export default function Stepper({ stage }) {
  const activeIndex = STEPS.findIndex((s) => s.id === stage);
  return (
    <nav className="stepper">
      {STEPS.map((s, i) => (
        <div
          key={s.id}
          className={
            "step" +
            (i === activeIndex ? " active" : "") +
            (i < activeIndex ? " done" : "")
          }
        >
          <span className="step-dot">{i < activeIndex ? "✓" : i + 1}</span>
          <span className="step-label">{s.label}</span>
        </div>
      ))}
    </nav>
  );
}
