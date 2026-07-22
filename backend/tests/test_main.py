# backend/tests/test_main.py
#
# Exercises all FastAPI endpoints via TestClient. Only the Groq call is
# mocked -- everything else (skills data, ChromaDB retrieval, the cache) is
# real and free to run.

from unittest.mock import MagicMock

import main


def _mock_groq_reply(monkeypatch, text: str) -> MagicMock:
    completion = MagicMock()
    completion.choices[0].message.content = text
    mock_create = MagicMock(return_value=completion)
    monkeypatch.setattr(main._groq_client.chat.completions, "create", mock_create)
    return mock_create


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_all_skills(client):
    response = client.get("/skills")
    assert response.status_code == 200
    assert len(response.json()) == len(main.SKILLS)


def test_get_skill_by_id(client):
    known_id = main.SKILLS[0]["id"]
    response = client.get(f"/skills/{known_id}")
    assert response.status_code == 200
    assert response.json()["id"] == known_id


def test_get_unknown_skill_returns_404(client):
    response = client.get("/skills/not-a-real-skill")
    assert response.status_code == 404


def test_search_endpoint(client):
    response = client.post("/search", json={"query": "backend web development", "top_k": 3})
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_chat_returns_grounded_response(client, monkeypatch):
    _mock_groq_reply(monkeypatch, "Learn Python and FastAPI.")

    response = client.post("/chat", json={"message": "what should I learn for backend jobs?"})

    assert response.status_code == 200
    body = response.json()
    assert body["response"] == "Learn Python and FastAPI."
    assert body["cached"] is False
    assert len(body["sources"]) > 0


def test_chat_cache_hit_skips_groq_on_repeat(client, monkeypatch):
    mock_create = _mock_groq_reply(monkeypatch, "Learn Python and FastAPI.")
    payload = {"message": "what should I learn for backend jobs?"}

    first = client.post("/chat", json=payload)
    second = client.post("/chat", json=payload)

    assert first.json()["cached"] is False
    assert second.json()["cached"] is True
    assert second.json()["response"] == first.json()["response"]
    mock_create.assert_called_once()
