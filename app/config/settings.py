from functools import lru_cache
from os import getenv
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):

    # OpenRouter
    openrouter_api_key: str = getenv("OPENROUTER_API_KEY")  # or set in .env file
    openrouter_base_url: str = getenv("OPENROUTER_BASE_URL")
    openrouter_model: str = getenv("OPENROUTER_MODEL")  # default model
    # openrouter_fallback_model: str = getenv("OPENROUTER_FALLBACK_MODEL")  # fallback model
    openrouter_timeout: float = getenv("OPENROUTER_TIMEOUT")
    openrouter_max_retries: int = getenv("OPENROUTER_MAX_RETRIES")
    openrouter_router_model: str = ""  # optional router model
    app_referer: str = getenv("APP_REFERER")
    app_title: str = "AI Genius Edu Chatbot"

    # Chatbot
    chat_temperature: float = getenv("CHAT_TEMPERATURE")
    max_history_messages: int = getenv("MAX_HISTORY_MESSAGES")
    quiz_default_questions: int = getenv("QUIZ_DEFAULT_QUESTIONS")
    quiz_max_questions: int = getenv("QUIZ_MAX_QUESTIONS")

    # Sessions
    session_ttl_minutes: int = getenv("SESSION_TTL_MINUTES", 60)
    session_purge_hours: int = getenv("SESSION_PURGE_HOURS", 24)
    max_sessions: int = getenv("MAX_SESSIONS", 10000)

    # API
    service_api_key: str = getenv("SERVICE_API_KEY", "")
    cors_origins: str = getenv("CORS_ORIGINS", "*")

    @property
    def router_model(self) -> str:
        return self.openrouter_router_model or self.openrouter_model

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
