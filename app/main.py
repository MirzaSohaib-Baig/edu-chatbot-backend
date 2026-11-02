from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.routes import api_router
from app.chatbot import ChatService, create_chatbot
from app.config import Settings, get_settings
from app.llm import LLMClient, OpenRouterClient
from app.sessions import InMemorySessionStore, SessionStore


def create_app(settings: Settings | None = None, llm: LLMClient | None = None,
               store: SessionStore | None = None) -> FastAPI:
    """App factory. Pass `llm` / `store` to swap implementations (tests, Redis, ...)."""
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        client = llm or OpenRouterClient(settings)
        app.state.store = store or InMemorySessionStore(
            ttl=settings.session_ttl_minutes * 60,
            purge_after=settings.session_purge_hours * 3600,
            max_sessions=settings.max_sessions,
        )
        app.state.chat_service = ChatService(app.state.store, create_chatbot(client, settings))
        yield
        if llm is None:
            await client.aclose()

    app = FastAPI(title="AI Genius Edu Chatbot", lifespan=lifespan)
    app.state.settings = settings
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list,
                       allow_methods=["*"], allow_headers=["*"])
    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=5005, log_level="info")