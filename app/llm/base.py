from typing import Protocol


class LLMClient(Protocol):
    """Anything that can complete a chat. The chatbot depends only on this."""

    async def chat(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float = 0.4,
        max_tokens: int | None = None,
    ) -> str: ...
