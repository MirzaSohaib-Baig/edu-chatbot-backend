import hmac

from fastapi import Header, HTTPException, Request

from app.chatbot import ChatService
from app.sessions import SessionStore


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service


def get_store(request: Request) -> SessionStore:
    return request.app.state.store


def require_api_key(request: Request, x_api_key: str | None = Header(default=None)) -> None:
    expected = request.app.state.settings.service_api_key
    if expected and not (x_api_key and hmac.compare_digest(x_api_key.encode(), expected.encode())):
        raise HTTPException(401, "Invalid or missing X-API-Key")
