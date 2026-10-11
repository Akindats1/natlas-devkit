/**
 * natlas — TypeScript SDK for N-ATLAS, Nigeria's multilingual LLM.
 *
 * N-ATLaS is an initiative of the Federal Ministry of Communications,
 * Innovation and Digital Economy, and powered by Awarri Technologies.
 */

export type Language = "en" | "ha" | "ig" | "yo";
export type Role = "system" | "user" | "assistant";

export interface ChatMessage {
  role: Role;
  content: string;
}

export interface ChatOptions {
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  stop?: string | string[];
  /** Force the reply language, whatever language the user wrote in. */
  replyIn?: Language;
  signal?: AbortSignal;
}

export interface Usage {
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
}

export interface ChatResult {
  text: string;
  usage: Usage;
  raw: unknown;
}

export interface TranslateResult {
  translation: string;
  source: Language | null;
  target: Language;
  usage: Usage;
}

export interface DetectResult {
  language: Language;
  name: string;
  confidence: number;
}

export interface NAtlasConfig {
  /** e.g. "http://localhost:8000" or your ngrok / cloud URL. Defaults to NATLAS_BASE_URL env. */
  baseUrl?: string;
  apiKey?: string;
  /** Sent as X-Client-Name so the server's usage log can tell testers/apps apart. */
  clientName?: string;
  timeoutMs?: number;
  fetch?: typeof fetch;
}

export const LANGUAGES: Record<Language, string> = {
  en: "English",
  ha: "Hausa",
  ig: "Igbo",
  yo: "Yoruba",
};

export const ATTRIBUTION =
  "N-ATLaS is an initiative of the Federal Ministry of Communications, Innovation and Digital Economy, and powered by Awarri Technologies.";

export class NAtlasError extends Error {
  constructor(message: string, public status?: number, public body?: unknown) {
    super(message);
    this.name = "NAtlasError";
  }
}

const env = (k: string): string | undefined =>
  typeof process !== "undefined" ? process.env?.[k] : undefined;

export class NAtlas {
  readonly baseUrl: string;
  private apiKey?: string;
  private clientName?: string;
  private timeoutMs: number;
  private _fetch: typeof fetch;

  constructor(config: NAtlasConfig = {}) {
    const url = config.baseUrl ?? env("NATLAS_BASE_URL") ?? "http://localhost:8000";
    this.baseUrl = url.replace(/\/+$/, "").replace(/\/v1$/, "");
    this.apiKey = config.apiKey ?? env("NATLAS_API_KEY");
    this.clientName = config.clientName ?? env("NATLAS_CLIENT_NAME");
    this.timeoutMs = config.timeoutMs ?? 120_000;
    this._fetch = config.fetch ?? globalThis.fetch.bind(globalThis);
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (this.apiKey) h.Authorization = `Bearer ${this.apiKey}`;
    if (this.clientName) h["X-Client-Name"] = this.clientName;
    return h;
  }

  private async request(path: string, init: RequestInit & { signal?: AbortSignal } = {}): Promise<Response> {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), this.timeoutMs);
    init.signal?.addEventListener("abort", () => ctrl.abort());
    let res: Response;
    try {
      res = await this._fetch(this.baseUrl + path, { ...init, headers: this.headers(), signal: ctrl.signal });
    } catch (e) {
      clearTimeout(timer);
      throw new NAtlasError(
        `Could not reach N-ATLAS server at ${this.baseUrl}. Is it running? (${(e as Error).message})`
      );
    }
    clearTimeout(timer);
    if (!res.ok) {
      let body: unknown;
      try { body = await res.json(); } catch { body = await res.text().catch(() => undefined); }
      const detail = (body as { detail?: string })?.detail ?? res.statusText;
      throw new NAtlasError(`N-ATLAS ${res.status}: ${detail}`, res.status, body);
    }
    return res;
  }

  private body(messages: ChatMessage[] | string, opts: ChatOptions, stream: boolean) {
    const msgs = typeof messages === "string" ? [{ role: "user", content: messages }] : messages;
    return JSON.stringify({
      model: "n-atlas",
      messages: msgs,
      stream,
      max_tokens: opts.maxTokens ?? 512,
      temperature: opts.temperature ?? 0.1,
      top_p: opts.topP ?? 0.95,
      stop: opts.stop,
      reply_language: opts.replyIn,
    });
  }

  /** Full chat completion. Accepts a message list or a single prompt string. */
  async chat(messages: ChatMessage[] | string, opts: ChatOptions = {}): Promise<ChatResult> {
    const res = await this.request("/v1/chat/completions", {
      method: "POST",
      body: this.body(messages, opts, false),
      signal: opts.signal,
    });
    const raw = (await res.json()) as {
      choices: { message: { content: string } }[];
      usage: Usage;
    };
    return { text: raw.choices[0]?.message?.content ?? "", usage: raw.usage ?? {}, raw };
  }

  /** Shortcut: one prompt in, text out. */
  async ask(prompt: string, opts: ChatOptions = {}): Promise<string> {
    return (await this.chat(prompt, opts)).text;
  }

  /** Stream tokens as they are generated. `for await (const t of natlas.stream(...))` */
  async *stream(messages: ChatMessage[] | string, opts: ChatOptions = {}): AsyncGenerator<string> {
    const res = await this.request("/v1/chat/completions", {
      method: "POST",
      body: this.body(messages, opts, true),
      signal: opts.signal,
    });
    if (!res.body) throw new NAtlasError("Streaming not supported by this runtime");
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const events = buf.split("\n\n");
      buf = events.pop() ?? "";
      for (const ev of events) {
        const line = ev.trim();
        if (!line.startsWith("data:")) continue;
        const data = line.slice(5).trim();
        if (data === "[DONE]") return;
        const piece = JSON.parse(data)?.choices?.[0]?.delta?.content;
        if (piece) yield piece;
      }
    }
  }

  /** Translate between English, Hausa, Igbo and Yoruba. */
  async translate(text: string, target: Language, source?: Language): Promise<TranslateResult> {
    const res = await this.request("/v1/translate", {
      method: "POST",
      body: JSON.stringify({ text, target, source }),
    });
    return (await res.json()) as TranslateResult;
  }

  /** Quick, offline-style language guess (en | ha | ig | yo). */
  async detectLanguage(text: string): Promise<DetectResult> {
    const res = await this.request("/v1/detect-language", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    return (await res.json()) as DetectResult;
  }

  async health(): Promise<{ status: string; backend: string }> {
    return (await (await this.request("/health")).json()) as { status: string; backend: string };
  }

  async stats(): Promise<Record<string, unknown>> {
    return (await (await this.request("/v1/stats")).json()) as Record<string, unknown>;
  }
}

/** Ready-made system prompts for common Nigerian use cases. */
export const prompts = {
  replyIn: (lang: Language) =>
    `You are a friendly assistant built on N-ATLAS. Always reply in ${LANGUAGES[lang]}.`,
  customerSupport: (business: string, lang: Language = "en") =>
    `You are a polite customer support agent for ${business}. Keep answers short and clear. Reply in ${LANGUAGES[lang]}.`,
  explainSimply: (lang: Language = "en") =>
    `Explain things simply, like to a secondary school student. Use everyday Nigerian examples. Reply in ${LANGUAGES[lang]}.`,
};

export default NAtlas;
