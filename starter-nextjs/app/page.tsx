"use client";

import { useRef, useState } from "react";

type Lang = "en" | "ha" | "ig" | "yo";
type Msg = { role: "user" | "assistant"; content: string };

const LANGS: { code: Lang; label: string }[] = [
  { code: "en", label: "English" },
  { code: "ha", label: "Hausa" },
  { code: "ig", label: "Igbo" },
  { code: "yo", label: "Yorùbá" },
];

const SUGGESTIONS = [
  "Explain mobile money safety tips",
  "Write a short welcome message for new customers",
  "What should I check before signing a rent agreement?",
];

export default function Home() {
  const [lang, setLang] = useState<Lang>("en");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  async function send(text: string) {
    if (!text.trim() || busy) return;
    const next: Msg[] = [...messages, { role: "user", content: text }];
    setMessages([...next, { role: "assistant", content: "" }]);
    setInput("");
    setBusy(true);

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: next, replyIn: lang }),
    });
    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let reply = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      reply += decoder.decode(value, { stream: true });
      setMessages([...next, { role: "assistant", content: reply }]);
      endRef.current?.scrollIntoView({ behavior: "smooth" });
    }
    setBusy(false);
  }

  return (
    <>
      <main className="wrap">
        <header>
          <div>
            <h1>N-ATLAS Chat</h1>
            <p className="sub">Ask in any language. Pick the language for replies.</p>
          </div>
          <div className="langs" role="group" aria-label="Reply language">
            {LANGS.map((l) => (
              <button key={l.code} aria-pressed={lang === l.code} onClick={() => setLang(l.code)}>
                {l.label}
              </button>
            ))}
          </div>
        </header>

        {messages.length === 0 ? (
          <div className="empty">
            Start a conversation
            <div className="chips">
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => send(s)}>{s}</button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>{m.content || "…"}</div>
          ))
        )}
        <div ref={endRef} />
      </main>

      <form onSubmit={(e) => { e.preventDefault(); send(input); }}>
        <div className="bar">
          <input value={input} onChange={(e) => setInput(e.target.value)}
                 placeholder="Type a message…" aria-label="Message" />
          <button disabled={busy || !input.trim()}>{busy ? "…" : "Send"}</button>
        </div>
        <footer>
          N-ATLaS is an initiative of the Federal Ministry of Communications, Innovation and Digital Economy,
          and powered by Awarri Technologies.
        </footer>
      </form>
    </>
  );
}
