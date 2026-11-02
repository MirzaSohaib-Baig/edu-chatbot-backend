import json

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

QUIZ_JSON = json.dumps({
    "title": "Algebra Basics",
    "questions": [
        {"question": f"Question {i}?", "options": ["A) one", "two", "three", "four"],
         "correct_index": 0, "explanation": f"Because {i}."}
        for i in (1, 2, 3)
    ],
})


class FakeLLM:
    """Stands in for OpenRouter. Routes by keyword; other calls echo the history size."""

    def __init__(self):
        self.quiz_replies = [QUIZ_JSON]
        self.calls = []

    async def chat(self, messages, **kw):
        self.calls.append(messages)
        system = messages[0]["content"]
        if system.startswith("You are the router"):
            msg = json.loads(messages[-1]["content"])["message"].lower()
            skill = next((s for k, s in [
                ("quiz", "quiz"), ("plan", "study_plan"), ("syllabus", "curriculum"),
                ("solve", "solve"), ("explain", "explain"), ("universit", "guidance"),
                ("hello", "chat"), ("custom", "custom")] if k in msg), None)
            if skill is None:
                return "total nonsense"
            return json.dumps({"skill": skill,
                               "topic": "algebra" if "algebra" in msg else None,
                               "level": "beginner" if "beginner" in msg else None})
        if system.startswith("You write multiple-choice"):
            return self.quiz_replies.pop(0)
        return f"history={len(messages) - 2}"


@pytest.fixture
def llm():
    return FakeLLM()


@pytest.fixture
def make_client(llm):
    clients = []

    def _make(**settings):
        c = TestClient(create_app(Settings(openrouter_api_key="x", **settings), llm=llm))
        clients.append(c)
        return c.__enter__()

    yield _make
    for c in clients:
        c.__exit__(None, None, None)


def say(client, message, sid="A"):
    r = client.post("/chat", json={"message": message, "session_id": sid})
    assert r.status_code == 200, r.text
    return r.json()


def correct_letter(client, sid="A"):
    return "ABCD"[client.app.state.store.peek(sid).quiz.current_question.correct_index]


def wrong_letter(client, sid="A"):
    return "ABCD"[(client.app.state.store.peek(sid).quiz.current_question.correct_index + 1) % 4]
