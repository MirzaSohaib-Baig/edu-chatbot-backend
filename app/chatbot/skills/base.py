from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from app.llm import LLMClient
from app.schemas import SessionState

from ..prompts import build_system_prompt


@dataclass
class SkillContext:
    """What a skill gets for one turn."""

    state: SessionState
    message: str
    llm: LLMClient
    model: str


class Skill(ABC):
    """One capability of the tutor. Subclass, register it, and the router can use it.

    `description` is shown to the router LLM, so write it as "use this when ...".
    Set `routable = False` for skills that are only reached via `intercepts`.
    """

    name: ClassVar[str]
    description: ClassVar[str]
    routable: ClassVar[bool] = True

    def intercepts(self, ctx: SkillContext) -> bool:
        """Claim the message before routing (e.g. an answer to a quiz question)."""
        return False

    @abstractmethod
    async def handle(self, ctx: SkillContext) -> str: ...


class PromptSkill(Skill):
    """A skill that is just instructions + the conversation. Most skills are this."""

    instructions: ClassVar[str]
    temperature: ClassVar[float] = 0.4

    async def handle(self, ctx: SkillContext) -> str:
        messages = [
            {"role": "system", "content": build_system_prompt(self.instructions, ctx.state.profile)},
            *ctx.state.llm_history(),
            {"role": "user", "content": ctx.message},
        ]
        return await ctx.llm.chat(messages, model=ctx.model, temperature=self.temperature)
