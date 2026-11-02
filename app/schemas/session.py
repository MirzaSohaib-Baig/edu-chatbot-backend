import time
from typing import Literal

from pydantic import BaseModel, Field

from .quiz import ActiveQuiz, QuizProgress


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class LearnerProfile(BaseModel):
    """What we've learned about the student so far; shared with every skill."""

    topic: str | None = None
    level: str | None = None

    def merge(self, topic: str | None, level: str | None) -> None:
        self.topic = topic or self.topic
        self.level = level or self.level


class SessionState(BaseModel):
    """Everything remembered for one user session. Plain data, so it can be stored anywhere."""

    id: str
    created_at: float = Field(default_factory=time.time)
    last_active: float = Field(default_factory=time.time)
    profile: LearnerProfile = Field(default_factory=LearnerProfile)
    history: list[Message] = Field(default_factory=list)
    quiz: ActiveQuiz | None = None

    def add_turn(self, user_text: str, bot_text: str, max_history: int) -> None:
        self.history += [Message(role="user", content=user_text), Message(role="assistant", content=bot_text)]
        self.history = self.history[-max_history:]

    def reset_conversation(self) -> None:
        """New conversation: drop history and quiz, keep the learner profile."""
        self.history = []
        self.quiz = None

    def llm_history(self, last: int | None = None) -> list[dict]:
        msgs = self.history[-last:] if last else self.history
        return [m.model_dump() for m in msgs]

    def quiz_progress(self) -> QuizProgress | None:
        return self.quiz.progress() if self.quiz else None


class SessionSnapshot(BaseModel):
    session_id: str
    profile: LearnerProfile
    history: list[Message]
    quiz: QuizProgress | None
    created_at: float
    last_active: float

    @classmethod
    def from_state(cls, s: SessionState) -> "SessionSnapshot":
        return cls(session_id=s.id, profile=s.profile, history=s.history, quiz=s.quiz_progress(),
                   created_at=s.created_at, last_active=s.last_active)
