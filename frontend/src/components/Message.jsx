import { useEffect } from "react";
import { useTypewriter } from "../hooks/useTypewriter.js";

export default function Message({ role, text, animate, onReveal }) {
  const isAva = role === "ava";
  const { shown } = useTypewriter(text, { enabled: isAva && animate });

  // Keep the view pinned to the bottom as the text reveals.
  useEffect(() => {
    if (isAva && animate && onReveal) onReveal();
  }, [shown, isAva, animate, onReveal]);

  return (
    <div className={"msg " + (isAva ? "ava" : "you")}>
      {isAva && <div className="who">Ava</div>}
      <div className="bubble">{isAva && animate ? shown : text}</div>
    </div>
  );
}
