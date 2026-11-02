# EDU-Chatbot Backend

An AI tutor backend for education / e-learning apps, powered by an LLM through
**OpenRouter** (official `openai` Python SDK, same setup as Jarvis). It answers from the
model's own knowledge. There is no training step and no data files.

**What it can do**

| Skill | Examples |
|---|---|
| `explain` | "Explain recursion", "what is entropy?" |
| `solve` | "Solve 2x + 3 = 7", "why does this code throw an error?" |
| `curriculum` | "Give me a syllabus to learn data science" |
| `study_plan` | "Plan 6 weeks for my SAT, 1 hour a day" |
| `quiz` | "Quiz me on photosynthesis": interactive multiple-choice, graded deterministically, with score and review |
| `guidance` | "Top universities for CS?", "which course should I take?" |
| `chat` | Greetings, who are you, off-topic redirects |

Every session has its own isolated history, learner profile (topic and level) and quiz state.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env          # set OPENROUTER_API_KEY / OPENROUTER_MODEL (same as Jarvis)
uvicorn app.main:app --reload --port 5005
pytest                        # fake LLM, no key needed
```

## API

| Method | Path | |
|---|---|---|
| POST | `/chat` | `{"message": "...", "session_id": "optional"}` -> `{session_id, reply (Markdown), skill, profile, quiz}` |
| POST | `/webhooks/rest/webhook` | Rasa-compatible `{sender, message}` -> `[{recipient_id, text}]` |
| GET / DELETE | `/sessions/{id}` | Inspect (never exposes quiz answers) / clear a session |
| GET | `/health` | Liveness |

Replies are **Markdown**. If your frontend rendered the old HTML replies, render Markdown instead.
Set `SERVICE_API_KEY` to require an `X-API-Key` header.

## Project layout

```
app/
  config/      settings.py       all settings, loaded from .env (pydantic-settings)
  schemas/     chat, session, quiz, routing   ALL pydantic models live here
  llm/         LLMClient protocol, OpenRouterClient (openai SDK), LLMError
  sessions/    SessionStore interface + in-memory implementation
  chatbot/
    engine.py    runs one turn
    router.py    LLM picks a skill (prompt is built from the registry)
    service.py   sessions + engine, used by every route
    prompts.py   persona + system prompt builder
    skills/      base.py, registry.py, general.py, learning.py, quiz.py
  api/         routes/ (chat, sessions, health), deps.py, errors.py
  main.py      create_app() factory
tests/
```

Dependencies only point inward: `api -> chatbot -> (llm, sessions, schemas, config)`.
The chatbot depends on the `LLMClient` protocol and the `SessionStore` interface, never on
OpenRouter or memory storage directly, so both can be swapped without touching skills.

## How a turn works

1. The session's state is locked (messages of one session run in order; different sessions run in parallel).
2. If a skill **intercepts** the message (e.g. an answer while a quiz is active), it handles it directly with no routing call.
3. Otherwise the **router** (one low-temperature call) picks a skill and extracts the student's topic and level.
4. The skill replies, and the turn is saved to the session.

Quiz answers (`B`, `option c`, `2`, or the option text) are graded in code, not by the LLM. Questions come
from the LLM as validated JSON (`schemas/quiz.py`, with one automatic retry), options are shuffled in code,
and any other message mid-quiz is handled normally while the quiz stays open. "stop quiz" ends it.

## Add a skill

```python
# app/chatbot/skills/learning.py
class FlashcardSkill(PromptSkill):
    name = "flashcards"
    description = "Create flashcards (term/definition pairs) for a topic."   # shown to the router
    instructions = "Make 10 flashcards as a Markdown table: Term | Definition."
```

Then add `FlashcardSkill()` to `default_registry()` in `skills/__init__.py`. The router prompt is generated
from the registry, so there is nothing else to change. For custom logic, subclass `Skill` and implement
`handle()` (see `skills/quiz.py`).

## Sessions

- `SESSION_TTL_MINUTES` idle -> new conversation (history and quiz cleared, learner profile kept).
- Idle sessions are purged after `SESSION_PURGE_HOURS`, and `MAX_SESSIONS` evicts the oldest.
- The in-memory store needs a single worker. For several workers/servers, implement `SessionStore`
  (`sessions/base.py`) with Redis. `SessionState` is plain pydantic, so it serialises with `model_dump_json()`.
