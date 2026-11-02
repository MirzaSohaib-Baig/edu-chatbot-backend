from app.config import Settings
from app.llm import LLMClient

from .engine import EduChatbot
from .router import SkillRouter
from .service import ChatService
from .skills import SkillRegistry, default_registry


def create_chatbot(llm: LLMClient, settings: Settings, registry: SkillRegistry | None = None) -> EduChatbot:
    registry = registry or default_registry(settings)
    router = SkillRouter(llm, registry, settings.router_model)
    return EduChatbot(llm, registry, router, settings.openrouter_model, settings.max_history_messages)


__all__ = ["ChatService", "EduChatbot", "SkillRegistry", "SkillRouter", "create_chatbot", "default_registry"]
