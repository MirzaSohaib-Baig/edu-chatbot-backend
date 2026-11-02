from openai import AsyncOpenAI, OpenAIError

from app.config import Settings

from .errors import LLMError


class OpenRouterClient:
    """The official OpenAI SDK pointed at OpenRouter (retries/backoff handled by the SDK)."""

    def __init__(self, settings: Settings):
        key = settings.openrouter_api_key
        if not key:
            raise LLMError("OPENROUTER_API_KEY is not set")
        self._default_model = settings.openrouter_model
        self._client = AsyncOpenAI(
            api_key=key,
            base_url=settings.openrouter_base_url,
            timeout=settings.openrouter_timeout,
            max_retries=settings.openrouter_max_retries,
            default_headers={"HTTP-Referer": settings.app_referer, "X-Title": settings.app_title},
        )

    async def chat(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float = 0.4,
        max_tokens: int | None = None,
    ) -> str:
        kwargs: dict = {"model": model or self._default_model, "messages": messages, "temperature": temperature}
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        try:
            resp = await self._client.chat.completions.create(**kwargs)
        except OpenAIError as e:
            raise LLMError(f"OpenRouter request failed: {e}") from e
        content = resp.choices[0].message.content if resp.choices else None
        if not content:
            raise LLMError("OpenRouter returned an empty reply")
        return content.strip()

    async def aclose(self) -> None:
        await self._client.close()
