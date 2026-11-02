from fastapi import APIRouter, Depends

from app.api.deps import get_chat_service, require_api_key
from app.chatbot import ChatService
from app.schemas import ChatRequest, ChatResponse, RasaReply, RasaRequest

router = APIRouter(tags=["chat"], dependencies=[Depends(require_api_key)])


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, service: ChatService = Depends(get_chat_service)):
    return await service.chat(body.session_id, body.message)


@router.post("/webhooks/rest/webhook", response_model=list[RasaReply])
async def rasa_compatible(body: RasaRequest, service: ChatService = Depends(get_chat_service)):
    """Drop-in for Rasa's REST channel so existing frontends keep working."""
    result = await service.chat(body.sender, body.message)
    return [RasaReply(recipient_id=body.sender, text=result.reply)]
