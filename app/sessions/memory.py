import asyncio
import time
from contextlib import asynccontextmanager

from app.schemas import SessionState

from .base import SessionStore


class InMemorySessionStore(SessionStore):
    """Single-process store.

    - after `ttl` idle seconds a session starts a fresh conversation (history cleared,
      learner profile carried over)
    - sessions idle for `purge_after` seconds are deleted; `max_sessions` evicts the oldest
    """

    def __init__(self, ttl: float, purge_after: float, max_sessions: int):
        self._ttl = ttl
        self._purge_after = purge_after
        self._max_sessions = max_sessions
        self._states: dict[str, SessionState] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._last_purge = time.time()

    def __len__(self) -> int:
        return len(self._states)

    @asynccontextmanager
    async def session(self, session_id: str):
        self._purge()
        lock = self._locks.setdefault(session_id, asyncio.Lock())
        async with lock:
            state = self._states.get(session_id)
            if state is None:
                state = self._states[session_id] = SessionState(id=session_id)
            elif time.time() - state.last_active > self._ttl:
                state.reset_conversation()
                state.created_at = time.time()
            try:
                yield state
            finally:
                state.last_active = time.time()

    def peek(self, session_id: str) -> SessionState | None:
        return self._states.get(session_id)

    def delete(self, session_id: str) -> bool:
        self._locks.pop(session_id, None)
        return self._states.pop(session_id, None) is not None

    def _purge(self) -> None:
        now = time.time()
        if now - self._last_purge < 60 and len(self._states) <= self._max_sessions:
            return
        self._last_purge = now
        stale = [k for k, s in self._states.items() if now - s.last_active > self._purge_after]
        overflow = len(self._states) - len(stale) - self._max_sessions
        if overflow > 0:
            fresh = sorted((k for k in self._states if k not in stale), key=lambda k: self._states[k].last_active)
            stale += fresh[:overflow]
        for sid in stale:
            lock = self._locks.get(sid)
            if lock is None or not lock.locked():
                self.delete(sid)
