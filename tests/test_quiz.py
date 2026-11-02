import json

from .conftest import QUIZ_JSON, correct_letter, say, wrong_letter


def test_full_quiz_flow_with_deterministic_grading(make_client, llm):
    c = make_client()
    r = say(c, "quiz me on algebra")
    assert r["skill"] == "quiz" and "Question 1/3" in r["reply"]
    assert r["quiz"] == {"title": "Algebra Basics", "current": 1, "total": 3, "score": 0}
    assert "A) A)" not in r["reply"]  # letter prefixes from the model are stripped

    calls_before = len(llm.calls)
    r = say(c, correct_letter(c).lower())
    assert r["skill"] == "quiz_answer" and "✅" in r["reply"] and "Question 2/3" in r["reply"]
    r = say(c, wrong_letter(c))
    assert "❌" in r["reply"] and "Question 3/3" in r["reply"]
    assert len(llm.calls) == calls_before  # grading never calls the LLM

    r = say(c, f"my answer is {correct_letter(c)}")
    assert "Quiz complete" in r["reply"] and "2/3 (67%)" in r["reply"] and "Review" in r["reply"]
    assert r["quiz"] is None
    assert say(c, "A")["skill"] != "quiz_answer"  # no quiz active any more


def test_answer_can_be_option_number_or_text(make_client):
    c = make_client()
    say(c, "quiz me")
    q = c.app.state.store.peek("A").quiz.current_question
    r = say(c, q.options[q.correct_index])  # by text
    assert "✅" in r["reply"]
    q = c.app.state.store.peek("A").quiz.current_question
    r = say(c, str(q.correct_index + 1))  # by number
    assert "✅" in r["reply"]


def test_non_answer_mid_quiz_is_routed_normally_and_quiz_stays(make_client):
    c = make_client()
    say(c, "quiz me")
    r = say(c, "explain what a variable is")
    assert r["skill"] == "explain" and r["quiz"]["current"] == 1


def test_stop_quiz(make_client):
    c = make_client()
    say(c, "quiz me")
    say(c, correct_letter(c))
    r = say(c, "stop quiz")
    assert "Quiz stopped" in r["reply"] and "1/1 (100%)" in r["reply"] and r["quiz"] is None


def test_invalid_json_is_retried_once_then_502(make_client, llm):
    c = make_client()
    llm.quiz_replies = ["not json", QUIZ_JSON]
    assert say(c, "quiz me")["quiz"]["total"] == 3

    llm.quiz_replies = ["bad", json.dumps({"title": "x", "questions": [{"question": "q", "options": ["a", "a", "b", "c"], "correct_index": 0}]})]
    r = c.post("/chat", json={"message": "quiz me", "session_id": "B"})
    assert r.status_code == 502 and "valid quiz" in r.json()["detail"]


def test_question_count_is_capped(make_client):
    c = make_client(quiz_max_questions=2)
    assert say(c, "quiz me")["quiz"]["total"] == 2


def test_new_quiz_replaces_old_one(make_client, llm):
    c = make_client()
    say(c, "quiz me")
    say(c, correct_letter(c))
    llm.quiz_replies = [QUIZ_JSON]
    assert say(c, "give me another quiz")["quiz"]["current"] == 1
