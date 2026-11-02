import uuid

from app.schemas import ChatResponse
from app.sessions import SessionStore

from .engine import EduChatbot


class ChatService:
    """Glue between sessions and the chatbot; used by every API route."""

    def __init__(self, store: SessionStore, bot: EduChatbot):
        self._store = store
        self._bot = bot

    async def chat(self, session_id: str | None, message: str) -> ChatResponse:
        sid = session_id or uuid.uuid4().hex
        async with self._store.session(sid) as state:
            result = await self._bot.reply(state, message)
            return ChatResponse(
                session_id=sid,
                reply=result.text,
                skill=result.skill,
                profile=state.profile.model_copy(),
                quiz=state.quiz_progress(),
            )
