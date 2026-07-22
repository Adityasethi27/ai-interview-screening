import { useEffect, useRef, useState } from "react";
import { api } from "../api.js";
import Message from "./Message.jsx";

export default function Chat({ session, onFinish }) {
  const [messages, setMessages] = useState([
    { id: 0, role: "ava", text: session.opening, animate: true },
  ]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  const scrollRef = useRef();
  const taRef = useRef();
  const idRef = useRef(1);

  const scrollDown = () => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  };

  useEffect(scrollDown, [messages, pending]);

  const send = async () => {
    const text = input.trim();
    if (!text || pending || done) return;
    setError("");
    setInput("");
    if (taRef.current) taRef.current.style.height = "auto";
    setMessages((m) => [...m, { id: idRef.current++, role: "you", text }]);
    setPending(true);
    try {
      const res = await api.sendMessage(session.session_id, text);
      setMessages((m) => [
        ...m,
        { id: idRef.current++, role: "ava", text: res.reply, animate: true },
      ]);
      if (res.done) setDone(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setPending(false);
    }
  };

  const onKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const grow = (e) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 160) + "px";
  };

  return (
    <div className="chat">
      <header className="chat-head">
        <div className="ava-id">
          <span className="mark-dot" />
          Ava
        </div>
        <div className="who-info">
          {session.candidate_name} · {session.role.replace(/_/g, " ")}
        </div>
      </header>

      <div className="stream" ref={scrollRef}>
        <div className="stream-inner">
          {messages.map((m) => (
            <Message
              key={m.id}
              role={m.role}
              text={m.text}
              animate={m.animate}
              onReveal={scrollDown}
            />
          ))}
          {pending && (
            <div className="msg ava">
              <div className="who">Ava</div>
              <div className="bubble typing">
                <span /><span /><span />
              </div>
            </div>
          )}
          {error && <div className="err inline">{error}</div>}
        </div>
      </div>

      <div className="composer">
        {done ? (
          <button className="finish" onClick={onFinish}>
            View your results
          </button>
        ) : (
          <div className="input-row">
            <textarea
              ref={taRef}
              rows={1}
              placeholder="Type your response"
              value={input}
              onChange={grow}
              onKeyDown={onKey}
              disabled={pending}
            />
            <button
              className="send"
              onClick={send}
              disabled={pending || !input.trim()}
              aria-label="Send"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="19" x2="12" y2="5" />
                <polyline points="6 11 12 5 18 11" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
