from fastapi import APIRouter

from . import chat, health, sessions

api_router = APIRouter()
for module in (health, chat, sessions):
    api_router.include_router(module.router)
