import { useState } from "react";
import SetupScreen from "./components/SetupScreen.jsx";
import InterviewScreen from "./components/InterviewScreen.jsx";
import SummaryScreen from "./components/SummaryScreen.jsx";
import Stepper from "./components/Stepper.jsx";

// Top-level state machine for the interview lifecycle.
// stages: "setup" -> "interview" -> "summary"
export default function App() {
  const [stage, setStage] = useState("setup");
  const [session, setSession] = useState(null); // StartSessionResponse

  const reset = () => {
    setSession(null);
    setStage("setup");
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <span className="logo">◆</span>
          <div>
            <h1>AI Interview Screening</h1>
            <p className="tagline">
              Resume-aware, RAG-grounded technical interviews
            </p>
          </div>
        </div>
        {session && (
          <button className="ghost" onClick={reset}>
            New interview
          </button>
        )}
      </header>

      <Stepper stage={stage} />

      <main className="app-main">
        {stage === "setup" && (
          <SetupScreen
            onStarted={(s) => {
              setSession(s);
              setStage("interview");
            }}
          />
        )}
        {stage === "interview" && session && (
          <InterviewScreen
            session={session}
            onFinished={() => setStage("summary")}
          />
        )}
        {stage === "summary" && session && (
          <SummaryScreen sessionId={session.session_id} onRestart={reset} />
        )}
      </main>

      <footer className="app-footer">
        <span>FastAPI · Chroma · Gemini · SQLite · React</span>
      </footer>
    </div>
  );
}
