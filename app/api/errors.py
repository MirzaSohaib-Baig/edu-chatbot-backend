from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.llm import LLMError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(LLMError)
    async def _llm_error(_: Request, exc: LLMError):
        return JSONResponse(status_code=502, content={"detail": f"LLM error: {exc}"})
