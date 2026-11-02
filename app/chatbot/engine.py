from app.llm import LLMClient
from app.schemas import BotReply, SessionState

from .router import SkillRouter
from .skills import SkillContext, SkillRegistry


class EduChatbot:
    """Runs one turn: let a skill claim the message, otherwise route, then reply."""

    def __init__(self, llm: LLMClient, registry: SkillRegistry, router: SkillRouter,
                 model: str, max_history: int):
        self._llm = llm
        self._registry = registry
        self._router = router
        self._model = model
        self._max_history = max_history

    async def reply(self, state: SessionState, message: str) -> BotReply:
        ctx = SkillContext(state=state, message=message, llm=self._llm, model=self._model)

        skill = self._registry.find_interceptor(ctx)  # e.g. a quiz answer: no routing call needed
        if skill is None:
            decision = await self._router.route(state, message)
            state.profile.merge(decision.topic, decision.level)
            skill = self._registry.get(decision.skill)

        text = await skill.handle(ctx)
        state.add_turn(message, text, self._max_history)
        return BotReply(text=text, skill=skill.name)
