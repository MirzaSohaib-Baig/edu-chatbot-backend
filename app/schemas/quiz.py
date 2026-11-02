import random
import re

from pydantic import BaseModel, Field, field_validator, model_validator

_LETTER_PREFIX = re.compile(r"^\s*[A-Da-d][\).:]\s+")


class QuizQuestion(BaseModel):
    question: str = Field(min_length=1)
    options: list[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    explanation: str = ""

    @field_validator("options")
    @classmethod
    def _clean_options(cls, v: list[str]) -> list[str]:
        cleaned = [_LETTER_PREFIX.sub("", o).strip() for o in v]
        if any(not o for o in cleaned) or len({o.casefold() for o in cleaned}) != len(cleaned):
            raise ValueError("options must be non-empty and distinct")
        return cleaned

    def shuffled(self, rng: random.Random) -> "QuizQuestion":
        """Shuffle options (LLMs favour certain letters) while tracking the right answer."""
        order = list(range(len(self.options)))
        rng.shuffle(order)
        return self.model_copy(
            update={
                "options": [self.options[i] for i in order],
                "correct_index": order.index(self.correct_index),
            }
        )


class Quiz(BaseModel):
    title: str = "Quiz"
    questions: list[QuizQuestion] = Field(min_length=1)

    def limited(self, n: int) -> "Quiz":
        return self.model_copy(update={"questions": self.questions[:n]})


class QuizProgress(BaseModel):
    """Safe-to-expose view of a quiz in progress (never includes answers)."""

    title: str
    current: int  # 1-based number of the question being asked
    total: int
    score: int


class ActiveQuiz(BaseModel):
    quiz: Quiz
    answers: list[int] = Field(default_factory=list)  # chosen option index per answered question

    @property
    def total(self) -> int:
        return len(self.quiz.questions)

    @property
    def answered(self) -> int:
        return len(self.answers)

    @property
    def finished(self) -> bool:
        return self.answered >= self.total

    @property
    def current_question(self) -> QuizQuestion:
        return self.quiz.questions[self.answered]

    @property
    def score(self) -> int:
        return sum(a == q.correct_index for a, q in zip(self.answers, self.quiz.questions))

    def submit(self, choice: int) -> bool:
        """Record an answer for the current question; returns whether it was correct."""
        correct = choice == self.current_question.correct_index
        self.answers.append(choice)
        return correct

    def progress(self) -> QuizProgress:
        return QuizProgress(
            title=self.quiz.title,
            current=min(self.answered + 1, self.total),
            total=self.total,
            score=self.score,
        )

    @model_validator(mode="after")
    def _check(self) -> "ActiveQuiz":
        if len(self.answers) > len(self.quiz.questions):
            raise ValueError("more answers than questions")
        return self
