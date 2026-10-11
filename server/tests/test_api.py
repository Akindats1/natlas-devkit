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


def test_reply_language_validation():
    with client() as c:
        bad = c.post("/v1/chat/completions",
                     json={"reply_language": "fr", "messages": [{"role": "user", "content": "x"}]})
        assert bad.status_code == 400


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
