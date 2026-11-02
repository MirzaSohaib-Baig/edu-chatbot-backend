import json
import random

import pytest

from app.chatbot import SkillRegistry, create_chatbot
from app.chatbot.skills import PromptSkill, default_registry
from app.config import Settings
from app.schemas import QuizQuestion, SessionState

from .conftest import FakeLLM, say


@pytest.mark.parametrize("message,skill", [
    ("hello there", "chat"),
    ("explain photosynthesis", "explain"),
    ("solve 2x + 3 = 7", "solve"),
    ("give me a syllabus for python", "curriculum"),
    ("make a study plan for my exam", "study_plan"),
    ("best universities for CS", "guidance"),
    ("quiz me on algebra", "quiz"),
])
def test_routes_to_each_skill(make_client, message, skill):
    assert say(make_client(), message)["skill"] == skill


def test_router_falls_back_to_explain_on_garbage(make_client):
    assert say(make_client(), "zzz qqq")["skill"] == "explain"


def test_profile_is_learned_and_survives_session_expiry(make_client):
    c = make_client()
    r = say(c, "explain algebra for a beginner")
    assert r["profile"] == {"topic": "algebra", "level": "beginner"}
    c.app.state.store.peek("A").last_active -= 3601
    r = say(c, "hello")
    assert r["profile"]["topic"] == "algebra"
    assert len(c.get("/sessions/A").json()["history"]) == 2  # history was reset


def test_sessions_are_isolated(make_client):
    c = make_client()
    say(c, "explain algebra", "A")
    say(c, "explain more", "A")
    assert say(c, "hello", "B")["reply"] == "history=0"
    assert say(c, "hello", "A")["reply"] == "history=4"
    assert say(c, "hello", "B")["profile"]["topic"] is None


def test_history_is_capped(make_client):
    c = make_client(max_history_messages=4)
    for _ in range(5):
        say(c, "hello")
    assert len(c.get("/sessions/A").json()["history"]) == 4


def test_new_skill_is_routable_without_touching_the_router(llm):
    class CustomSkill(PromptSkill):
        name = "custom"
        description = "Does custom things."
        instructions = "Be custom."

    settings = Settings(openrouter_api_key="x")
    registry = default_registry(settings)
    registry.register(CustomSkill())
    bot = create_chatbot(llm, settings, registry)

    import asyncio
    reply = asyncio.run(bot.reply(SessionState(id="s"), "custom please"))
    assert reply.skill == "custom"
    assert "custom: Does custom things." in llm.calls[0][0]["content"]
    with pytest.raises(ValueError):
        registry.register(CustomSkill())


def test_shuffle_keeps_the_correct_answer():
    q = QuizQuestion(question="?", options=["right", "x", "y", "z"], correct_index=0)
    for seed in range(20):
        s = q.shuffled(random.Random(seed))
        assert s.options[s.correct_index] == "right" and sorted(s.options) == sorted(q.options)


def test_registry_hides_non_routable_skills(llm):
    names = {s.name for s in default_registry(Settings(openrouter_api_key="x")).routable()}
    assert "quiz_answer" not in names and "quiz" in names


def test_concurrent_messages_in_one_session_are_serialised(llm):
    import asyncio

    from app.chatbot import ChatService
    from app.sessions import InMemorySessionStore

    settings = Settings(openrouter_api_key="x")
    store = InMemorySessionStore(ttl=3600, purge_after=86400, max_sessions=10)
    service = ChatService(store, create_chatbot(llm, settings))

    async def run():
        return await asyncio.gather(*(service.chat("S", "hello") for _ in range(5)))

    replies = [r.reply for r in asyncio.run(run())]
    assert sorted(replies) == [f"history={n}" for n in (0, 2, 4, 6, 8)]  # no lost updates
