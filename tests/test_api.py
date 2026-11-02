from .conftest import say


def test_new_session_id_is_generated_and_reusable(make_client):
    c = make_client()
    r = c.post("/chat", json={"message": "hello"}).json()
    assert len(r["session_id"]) == 32
    assert c.get(f"/sessions/{r['session_id']}").status_code == 200


def test_rasa_compatible_webhook(make_client):
    c = make_client()
    out = c.post("/webhooks/rest/webhook", json={"sender": "u1", "message": "hello"}).json()
    assert out == [{"recipient_id": "u1", "text": "history=0"}]


def test_snapshot_never_leaks_quiz_answers(make_client):
    c = make_client()
    say(c, "quiz me")
    body = c.get("/sessions/A").json()
    assert body["quiz"] == {"title": "Algebra Basics", "current": 1, "total": 3, "score": 0}
    assert "correct_index" not in c.get("/sessions/A").text


def test_validation(make_client):
    c = make_client()
    assert c.post("/chat", json={"message": ""}).status_code == 422
    assert c.post("/chat", json={"message": "hi", "session_id": "bad id!"}).status_code == 422
    assert c.get("/sessions/bad id!").status_code in (404, 422)


def test_api_key_and_delete(make_client):
    c = make_client(service_api_key="secret")
    h = {"X-API-Key": "secret"}
    assert c.post("/chat", json={"message": "hello"}).status_code == 401
    assert c.get("/health").status_code == 200  # health stays open
    c.post("/chat", json={"message": "hello", "session_id": "A"}, headers=h)
    assert c.delete("/sessions/A", headers=h).status_code == 200
    assert c.get("/sessions/A", headers=h).status_code == 404
