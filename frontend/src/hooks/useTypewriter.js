import { useEffect, useState } from "react";

// Reveals `text` progressively for a live "typing" feel. Speed adapts so long
// messages don't drag: total reveal time is capped.
export function useTypewriter(text, { enabled = true, maxMs = 1400 } = {}) {
  const [shown, setShown] = useState(enabled ? "" : text);
  const [done, setDone] = useState(!enabled);

  useEffect(() => {
    if (!enabled || !text) {
      setShown(text || "");
      setDone(true);
      return;
    }
    setShown("");
    setDone(false);
    const step = Math.max(1, Math.ceil(text.length / (maxMs / 16)));
    let i = 0;
    const id = setInterval(() => {
      i = Math.min(text.length, i + step);
      setShown(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(id);
        setDone(true);
      }
    }, 16);
    return () => clearInterval(id);
  }, [text, enabled, maxMs]);

  return { shown, done };
}
