from pydantic import BaseModel, field_validator


class RouteDecision(BaseModel):
    """The router LLM's choice of skill, plus anything it learned about the student."""

    skill: str
    topic: str | None = None
    level: str | None = None

    @field_validator("topic", "level", mode="before")
    @classmethod
    def _blank_to_none(cls, v):
        return v.strip() or None if isinstance(v, str) else None
