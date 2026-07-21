import { useState } from "react";
import Setup from "./components/Setup.jsx";
import Chat from "./components/Chat.jsx";
import Summary from "./components/Summary.jsx";

// Minimal state machine: setup -> chat -> summary
export default function App() {
  const [stage, setStage] = useState("setup");
  const [session, setSession] = useState(null);

  return (
    <div className="shell">
      {stage === "setup" && (
        <Setup
          onStart={(s) => {
            setSession(s);
            setStage("chat");
          }}
        />
      )}
      {stage === "chat" && session && (
        <Chat session={session} onFinish={() => setStage("summary")} />
      )}
      {stage === "summary" && session && (
        <Summary
          sessionId={session.session_id}
          onRestart={() => {
            setSession(null);
            setStage("setup");
          }}
        />
      )}
    </div>
  );
}
