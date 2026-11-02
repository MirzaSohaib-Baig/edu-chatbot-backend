from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager

from app.schemas import SessionState


class SessionStore(ABC):
    """Per-session storage. Implement this (e.g. with Redis) to scale beyond one process."""

    @abstractmethod
    def session(self, session_id: str) -> AbstractAsyncContextManager[SessionState]:
        """Exclusive access to one session's state (created if new).

        Turns of the same session are serialised; different sessions run concurrently.
        """

    @abstractmethod
    def peek(self, session_id: str) -> SessionState | None:
        """Read-only look at a session without creating it."""

    @abstractmethod
    def delete(self, session_id: str) -> bool: ...
