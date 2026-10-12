"""N-ATLAS OpenAI-compatible server.

Any app built for the OpenAI API can use N-ATLAS by changing its base URL:

    base_url = "http://localhost:8000/v1"
"""

from __future__ import annotations

import asyncio
import json
import os
import threading
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

from . import __version__
from .backends import load_backend
from .prompts import (ATTRIBUTION, LANGUAGES, detect_language, reply_in_reminder,
                      reply_in_system_prompt, translate_messages)

MODEL_ID = "n-atlas"
API_KEY = os.environ.get("NATLAS_API_KEY")  # optional; if set, required as Bearer token
LOG_PATH = Path(os.environ.get("NATLAS_LOG", "usage.jsonl"))
PLAYGROUND = Path(__file__).parent / "static" / "playground.html"

backend = None
_model_lock = threading.Lock()  # one 8B model, one generation at a time
_streams: dict[str, threading.Event] = {}  # streaming answers in progress, by id
_log_lock = threading.Lock()


@asynccontextmanager
async def _lifespan(_app):
    global backend
    backend = load_backend()
    yield


app = FastAPI(
    title="N-ATLAS OpenAI-compatible API",
    version=__version__,
    description=ATTRIBUTION,
    lifespan=_lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def _attribution_header(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Powered-By"] = "N-ATLaS (Awarri Technologies / FMCIDE)"
    return resp


def _auth(authorization: Optional[str] = Header(default=None)):
    if not API_KEY:
        return
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def _log(event: dict):
    """Anonymous usage log (no message content). This is the evidence trail
    for real-world validation: who tested, when, which language, latency."""
    event["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with _log_lock, LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


# ---------- schemas ----------

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    model: str = MODEL_ID
    messages: list[Message]
    max_tokens: int = Field(512, ge=1, le=4096)
    temperature: float = Field(0.1, ge=0, le=2)
    top_p: float = Field(0.95, gt=0, le=1)
    stream: bool = False
    stop: Optional[list[str] | str] = None
    # N-ATLAS extension: force the reply language (en|ha|ig|yo)
    reply_language: Optional[str] = None


class TranslateRequest(BaseModel):
    text: str
    target: str
    source: Optional[str] = None
    max_tokens: int = 512


class DetectRequest(BaseModel):
    text: str


# ---------- helpers ----------

def _prepare(req: ChatRequest) -> list[dict]:
    msgs = [m.model_dump() for m in req.messages]
    if req.reply_language:
        try:
            sys_prompt = reply_in_system_prompt(req.reply_language)
        except ValueError as e:
            raise HTTPException(400, str(e))
        msgs = [m for m in msgs if m["role"] != "system"]
        msgs.insert(0, {"role": "system", "content": sys_prompt})
        last = max((i for i, m in enumerate(msgs) if m["role"] == "user"), default=None)
        if last is not None:
            msgs[last] = {**msgs[last],
                          "content": msgs[last]["content"] + reply_in_reminder(req.reply_language)}
    return msgs


def _stop(req) -> Optional[list[str]]:
    if req.stop is None:
        return None
    return [req.stop] if isinstance(req.stop, str) else req.stop


def _run(messages, req) -> tuple[str, dict]:
    with _model_lock:
        return backend.generate(messages, max_tokens=req.max_tokens, temperature=req.temperature,
                                top_p=req.top_p, stop=_stop(req))


# ---------- routes ----------

@app.get("/playground", response_class=HTMLResponse, include_in_schema=False)
def playground():
    """Browser playground: chat, translate, and copy-ready code for each request."""
    return HTMLResponse(PLAYGROUND.read_text(encoding="utf-8"))


@app.get("/")
def root(request: Request):
    # Browsers get the playground; API clients keep getting JSON.
    if "text/html" in request.headers.get("accept", ""):
        return playground()
    return {
        "name": "N-ATLAS OpenAI-compatible API",
        "version": __version__,
        "backend": getattr(backend, "name", None),
        "languages": LANGUAGES,
        "docs": "/docs",
        "attribution": ATTRIBUTION,
    }


@app.get("/health")
def health():
    return {"status": "ok", "backend": getattr(backend, "name", None)}


@app.get("/v1/models", dependencies=[Depends(_auth)])
def models():
    return {"object": "list", "data": [{
        "id": MODEL_ID, "object": "model", "created": 1727740800, "owned_by": "NCAIR1/Awarri",
    }]}


@app.post("/v1/chat/completions", dependencies=[Depends(_auth)])
async def chat(req: ChatRequest, x_client_name: Optional[str] = Header(default=None)):
    messages = _prepare(req)
    cid = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    lang = detect_language(last_user)["language"]
    t0 = time.time()

    if not req.stream:
        text, usage = await asyncio.to_thread(_run, messages, req)
        _log({"endpoint": "chat", "client": x_client_name, "input_lang": lang,
              "reply_lang": req.reply_language, "latency_ms": int((time.time() - t0) * 1000),
              "usage": usage})
        return {
            "id": cid, "object": "chat.completion", "created": created, "model": MODEL_ID,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": text},
                         "finish_reason": "stop"}],
            "usage": usage,
        }

    loop = asyncio.get_running_loop()
    pieces: asyncio.Queue = asyncio.Queue()
    cancelled = threading.Event()
    _streams[cid] = cancelled  # lets POST /v1/chat/cancel/{id} stop it
    done = object()

    def generate():
        # Runs on its own thread so the model lock is always released here, even
        # when the client disconnects mid-answer (Stop button, closed tab).
        try:
            with _model_lock:
                for piece in backend.stream(messages, max_tokens=req.max_tokens,
                                            temperature=req.temperature, top_p=req.top_p,
                                            stop=_stop(req)):
                    if cancelled.is_set():
                        break
                    loop.call_soon_threadsafe(pieces.put_nowait, piece)
        finally:
            loop.call_soon_threadsafe(pieces.put_nowait, done)

    def chunk(delta, finish=None):
        return "data: " + json.dumps({
            "id": cid, "object": "chat.completion.chunk", "created": created, "model": MODEL_ID,
            "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
        }, ensure_ascii=False) + "\n\n"

    async def sse():
        threading.Thread(target=generate, daemon=True).start()
        n, completed = 0, False
        try:
            yield chunk({"role": "assistant"})
            while (piece := await pieces.get()) is not done:
                n += 1
                yield chunk({"content": piece})
            yield chunk({}, "stop")
            yield "data: [DONE]\n\n"
            completed = True
        finally:
            cancelled.set()  # client gone: stop generating at the next token
            _streams.pop(cid, None)
            _log({"endpoint": "chat_stream", "client": x_client_name, "input_lang": lang,
                  "reply_lang": req.reply_language, "latency_ms": int((time.time() - t0) * 1000),
                  "chunks": n, "completed": completed})

    return StreamingResponse(sse(), media_type="text/event-stream")


@app.post("/v1/chat/cancel/{completion_id}", dependencies=[Depends(_auth)])
def cancel(completion_id: str):
    """Stop a streaming answer by its id (sent in every chunk). Proxies such as ngrok
    may not pass a client's disconnect on, so the Stop button calls this to free the
    model at once."""
    event = _streams.get(completion_id)
    if event:
        event.set()
    return {"id": completion_id, "cancelled": bool(event)}


@app.post("/v1/translate", dependencies=[Depends(_auth)])
async def translate(req: TranslateRequest, x_client_name: Optional[str] = Header(default=None)):
    try:
        messages = translate_messages(req.text, req.source, req.target)
    except ValueError as e:
        raise HTTPException(400, str(e))
    t0 = time.time()
    shim = ChatRequest(messages=[Message(**m) for m in messages], max_tokens=req.max_tokens,
                       temperature=0.1)
    text, usage = await asyncio.to_thread(_run, messages, shim)
    _log({"endpoint": "translate", "client": x_client_name, "source": req.source,
          "target": req.target, "latency_ms": int((time.time() - t0) * 1000), "usage": usage})
    return {"translation": text.strip().strip('"'), "source": req.source, "target": req.target,
            "usage": usage}


@app.post("/v1/detect-language", dependencies=[Depends(_auth)])
def detect(req: DetectRequest):
    return detect_language(req.text)


@app.get("/v1/stats", dependencies=[Depends(_auth)])
def stats():
    """Aggregated usage — handy for the validation section of a submission."""
    if not LOG_PATH.exists():
        return {"total_requests": 0}
    rows = [json.loads(l) for l in LOG_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    by = lambda k: {v: sum(1 for r in rows if r.get(k) == v) for v in {r.get(k) for r in rows}}
    lat = [r["latency_ms"] for r in rows if "latency_ms" in r]
    return {
        "total_requests": len(rows),
        "by_endpoint": by("endpoint"),
        "by_client": by("client"),
        "by_input_language": by("input_lang"),
        "avg_latency_ms": int(sum(lat) / len(lat)) if lat else None,
        "first": rows[0]["ts"] if rows else None,
        "last": rows[-1]["ts"] if rows else None,
    }
