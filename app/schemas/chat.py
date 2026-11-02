from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from .quiz import QuizProgress
from .session import LearnerProfile

ID_PATTERN = r"^[A-Za-z0-9_\-:.@]{1,128}$"
SessionId = Annotated[str, StringConstraints(pattern=ID_PATTERN)]
MessageText = Annotated[str, StringConstraints(min_length=1, max_length=4000)]


class ChatRequest(BaseModel):
    message: MessageText
    session_id: SessionId | None = Field(default=None, description="Omit to start a new session")


class ChatResponse(BaseModel):
    session_id: str
    reply: str  # Markdown
    skill: str
    profile: LearnerProfile
    quiz: QuizProgress | None = None


class BotReply(BaseModel):
    """Internal result of the chatbot engine for one turn."""

    text: str
    skill: str


# Rasa REST channel compatibility, so existing frontends keep working
class RasaRequest(BaseModel):
    sender: SessionId
    message: MessageText


class RasaReply(BaseModel):
    recipient_id: str
    text: str
