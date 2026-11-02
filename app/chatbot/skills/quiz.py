import json
import random
import re
from typing import ClassVar

from pydantic import ValidationError

from app.config import Settings
from app.llm import LLMError
from app.schemas import ActiveQuiz, Quiz, QuizQuestion

from ..json_utils import extract_json_object
from .base import Skill, SkillContext

LETTERS = "ABCD"

_ANSWER_RE = re.compile(r"^(?:(?:my\s+)?(?:answer|option|choice)\s*(?:is\s*)?)?\(?([a-d1-4])\)?[.)!:]?$")
_STOP_RE = re.compile(r"^(?:stop|quit|exit|end|cancel)(?:\s+(?:the\s+)?(?:quiz|test))?\s*[.!]?$")

QUIZ_SYSTEM = """You write multiple-choice quizzes for students. Return ONLY a JSON object, no prose and no code fences:
{{"title": str, "questions": [{{"question": str, "options": [exactly 4 distinct strings, without letter prefixes], "correct_index": 0-3, "explanation": str (1-2 sentences)}}]}}
Rules:
- Number of questions: what the student asks for, otherwise {default}; never more than {maximum}.
- Use the student's topic and level (and recent conversation if they say "what we just covered").
- Exactly one option is correct, distractors are plausible, questions are unambiguous and factually correct.
- Mix difficulty unless the student specifies one."""


def parse_choice(text: str, question: QuizQuestion) -> int | None:
    """Map a student's reply ('b', 'option c', '2', or the option text) to an option index."""
    t = text.strip().lower()
    if m := _ANSWER_RE.match(t):
        c = m.group(1)
        return "abcd".index(c) if c.isalpha() else int(c) - 1
    for i, opt in enumerate(question.options):
        if t == opt.strip().lower():
            return i
    return None


def render_question(active: ActiveQuiz) -> str:
    q = active.current_question
    options = "\n".join(f"{LETTERS[i]}) {o}" for i, o in enumerate(q.options))
    return f"**Question {active.answered + 1}/{active.total}**\n\n{q.question}\n\n{options}"


def render_summary(active: ActiveQuiz, stopped: bool = False) -> str:
    answered, score = active.answered, active.score
    if stopped and answered == 0:
        return "Quiz stopped. Ask me for a new one any time!"
    pct = round(100 * score / answered)
    verdict = ("Outstanding!" if pct >= 90 else "Great work!" if pct >= 70
               else "Good effort, a bit more practice will help." if pct >= 50
               else "Keep going, review the topics below and try again.")
    head = "Quiz stopped." if stopped else "**Quiz complete!**"
    lines = [f"{head} You scored **{score}/{answered} ({pct}%)**. {verdict}"]
    missed = [(i, q) for i, (a, q) in enumerate(zip(active.answers, active.quiz.questions))
              if a != q.correct_index]
    if missed:
        lines.append("\n**Review**")
        lines += [f"- Q{i + 1}: {q.question} -> **{q.options[q.correct_index]}**" for i, q in missed]
    lines.append("\nWant a study plan for the weak spots, or another quiz?")
    return "\n".join(lines)


class QuizSkill(Skill):
    name = "quiz"
    description = (
        "The student wants to be quizzed or tested: create a quiz / practice test / MCQs on a topic "
        "and run it interactively, one question at a time."
    )

    def __init__(self, settings: Settings, rng: random.Random | None = None):
        self._default = settings.quiz_default_questions
        self._max = settings.quiz_max_questions
        self._rng = rng or random.Random()

    async def handle(self, ctx: SkillContext) -> str:
        quiz = await self._generate(ctx)
        quiz = quiz.limited(self._max)
        quiz = quiz.model_copy(update={"questions": [q.shuffled(self._rng) for q in quiz.questions]})
        active = ActiveQuiz(quiz=quiz)
        ctx.state.quiz = active
        intro = (f"**{quiz.title}**: {active.total} question{'s' if active.total != 1 else ''}. "
                 "Reply with the letter of your answer (A-D), or say \"stop quiz\" to end.")
        return f"{intro}\n\n{render_question(active)}"

    async def _generate(self, ctx: SkillContext) -> Quiz:
        payload = {
            "request": ctx.message,
            "student": ctx.state.profile.model_dump(),
            "recent_turns": ctx.state.llm_history(last=6),
        }
        messages = [
            {"role": "system", "content": QUIZ_SYSTEM.format(default=self._default, maximum=self._max)},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]
        error = ""
        for _ in range(2):  # one retry with the validation error as feedback
            raw = await ctx.llm.chat(messages, model=ctx.model, temperature=0.3)
            try:
                return Quiz.model_validate_json(extract_json_object(raw) or "")
            except ValidationError as e:
                error = str(e)[:500]
                messages = [*messages, {"role": "assistant", "content": raw},
                            {"role": "user", "content": f"That JSON was invalid: {error}\nReturn the corrected JSON only."}]
        raise LLMError(f"Could not generate a valid quiz: {error}")


class QuizAnswerSkill(Skill):
    """Grades answers deterministically while a quiz is active (no LLM call)."""

    name = "quiz_answer"
    description = "Answer to the current quiz question."
    routable: ClassVar[bool] = False

    def intercepts(self, ctx: SkillContext) -> bool:
        quiz = ctx.state.quiz
        if quiz is None or quiz.finished:
            return False
        t = ctx.message.strip().lower()
        return bool(_STOP_RE.match(t)) or parse_choice(t, quiz.current_question) is not None

    async def handle(self, ctx: SkillContext) -> str:
        active = ctx.state.quiz
        if _STOP_RE.match(ctx.message.strip().lower()):
            ctx.state.quiz = None
            return render_summary(active, stopped=True)

        q = active.current_question
        choice = parse_choice(ctx.message, q)
        if active.submit(choice):
            feedback = "✅ **Correct!**"
        else:
            feedback = f"❌ **Not quite.** The correct answer is **{LETTERS[q.correct_index]}) {q.options[q.correct_index]}**."
        if q.explanation:
            feedback += f" {q.explanation}"

        if active.finished:
            ctx.state.quiz = None
            return f"{feedback}\n\n---\n\n{render_summary(active)}"
        return f"{feedback}\n\n---\n\n{render_question(active)}"
