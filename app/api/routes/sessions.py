from fastapi import APIRouter, Depends, HTTPException, Path

from app.api.deps import get_store, require_api_key
from app.schemas import ID_PATTERN, SessionSnapshot
from app.sessions import SessionStore

router = APIRouter(prefix="/sessions", tags=["sessions"], dependencies=[Depends(require_api_key)])


@router.get("/{session_id}", response_model=SessionSnapshot)
async def get_session(session_id: str = Path(pattern=ID_PATTERN), store: SessionStore = Depends(get_store)):
    state = store.peek(session_id)
    if state is None:
        raise HTTPException(404, "Session not found")
    return SessionSnapshot.from_state(state)


@router.delete("/{session_id}")
async def delete_session(session_id: str = Path(pattern=ID_PATTERN), store: SessionStore = Depends(get_store)):
    if not store.delete(session_id):
        raise HTTPException(404, "Session not found")
    return {"deleted": session_id}
