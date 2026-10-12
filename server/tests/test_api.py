import os
os.environ["NATLAS_BACKEND"] = "mock"
os.environ["NATLAS_LOG"] = "/tmp/natlas_test_usage.jsonl"

from fastapi.testclient import TestClient
from natlas_server.app import app
from natlas_server.prompts import detect_language


def client():
    return TestClient(app)


def test_health_and_models():
    with client() as c:
        assert c.get("/health").json()["status"] == "ok"
        assert c.get("/v1/models").json()["data"][0]["id"] == "n-atlas"


def test_playground_and_root():
    with client() as c:
        page = c.get("/playground")
        assert page.status_code == 200 and "N-ATLAS Playground" in page.text
        assert "N-ATLAS Playground" in c.get("/", headers={"Accept": "text/html"}).text
        assert c.get("/", headers={"Accept": "application/json"}).json()["docs"] == "/docs"


def test_chat_openai_shape():
    with client() as c:
        r = c.post("/v1/chat/completions", json={"messages": [{"role": "user", "content": "Sannu"}]})
        body = r.json()
        assert r.status_code == 200
        assert body["object"] == "chat.completion"
        assert "Sannu" in body["choices"][0]["message"]["content"]
        assert r.headers["X-Powered-By"].startswith("N-ATLaS")


def test_stream():
    with client() as c:
        with c.stream("POST", "/v1/chat/completions",
                      json={"stream": True, "messages": [{"role": "user", "content": "hi"}]}) as r:
            text = "".join(r.iter_text())
        assert "data: [DONE]" in text and "chat.completion.chunk" in text


def test_stream_disconnect_frees_model():
    """A client that leaves mid-answer (Stop button, closed tab) must not keep the model
    busy. Uses a real server: the in-process TestClient never signals a disconnect."""
    import json
    import socket
    import threading
    import time

    import httpx
    import uvicorn
    from natlas_server import app as appmod

    def endless(messages, **kw):  # an answer that never ends on its own
        while True:
            time.sleep(0.02)
            yield "word "

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(appmod.app, port=port, log_level="error"))
    threading.Thread(target=server.run, daemon=True).start()
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            try:
                if httpx.get(base + "/health").status_code == 200:
                    break
            except httpx.TransportError:
                time.sleep(0.05)
        appmod.backend.stream = endless
        with httpx.stream("POST", base + "/v1/chat/completions", timeout=5,
                          json={"stream": True, "messages": [{"role": "user", "content": "hi"}]}) as r:
            next(r.iter_lines())
        del appmod.backend.stream
        r = httpx.post(base + "/v1/chat/completions", timeout=10,
                       json={"messages": [{"role": "user", "content": "Sannu"}]})
        assert r.status_code == 200

        # Behind a proxy the disconnect may never arrive: the Stop button cancels by id.
        appmod.backend.stream = endless
        with httpx.stream("POST", base + "/v1/chat/completions", timeout=10,
                          json={"stream": True, "messages": [{"role": "user", "content": "hi"}]}) as r:
            lines = r.iter_lines()
            first = json.loads(next(lines).removeprefix("data: "))
            assert httpx.post(f"{base}/v1/chat/cancel/{first['id']}").json()["cancelled"] is True
            assert any(line == "data: [DONE]" for line in lines)  # the answer ends
        del appmod.backend.stream
        r = httpx.post(base + "/v1/chat/completions", timeout=10,
                       json={"messages": [{"role": "user", "content": "Sannu"}]})
        assert r.status_code == 200
        assert httpx.post(base + "/v1/chat/cancel/unknown-id").json()["cancelled"] is False
    finally:
        server.should_exit = True


def test_reply_language_validation():
    with client() as c:
        bad = c.post("/v1/chat/completions",
                     json={"reply_language": "fr", "messages": [{"role": "user", "content": "x"}]})
        assert bad.status_code == 400


def test_reply_language_reminds_latest_message():
    # After English turns the model ignores the system prompt alone, so the
    # latest user message carries the reminder too (the mock echoes it back).
    with client() as c:
        r = c.post("/v1/chat/completions", json={"reply_language": "yo", "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"},
            {"role": "user", "content": "Explain inflation"}]})
        text = r.json()["choices"][0]["message"]["content"]
        assert text.endswith("Explain inflation\n\n(Reply only in Yoruba.)")


def test_translate_and_stats():
    with client() as c:
        r = c.post("/v1/translate", json={"text": "Good morning", "target": "ha"})
        assert r.status_code == 200 and "translation" in r.json()
        assert c.get("/v1/stats").json()["total_requests"] >= 1


def test_detect_language():
    assert detect_language("Kedu ka ị mere?")["language"] == "ig"
    assert detect_language("Ẹ kú àárọ̀, ṣé dáadáa ni?")["language"] == "yo"
    assert detect_language("Menene sunanka? Na gode")["language"] == "ha"
    assert detect_language("How are you today?")["language"] == "en"
