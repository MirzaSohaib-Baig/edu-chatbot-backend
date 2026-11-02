import json

from pydantic import ValidationError

from app.llm import LLMClient
from app.schemas import RouteDecision, SessionState

from .json_utils import extract_json_object
from .skills import SkillRegistry

DEFAULT_SKILL = "explain"


class SkillRouter:
    """One cheap, deterministic LLM call that picks which skill handles the message.

    The prompt is generated from the registry, so new skills are routable automatically.
    """

    def __init__(self, llm: LLMClient, registry: SkillRegistry, model: str):
        self._llm = llm
        self._model = model
        self._names = {s.name for s in registry.routable()}
        skills = "\n".join(f"- {s.name}: {s.description}" for s in registry.routable())
        self._prompt = (
            "You are the router of an education chatbot. Choose the skill that should handle the "
            "student's latest message.\n"
            f"Skills:\n{skills}\n\n"
            'Return ONLY a JSON object: {"skill": <skill name>, "topic": string|null, "level": string|null}\n'
            "- topic: the subject being studied, if stated or implied by the conversation.\n"
            "- level: the student's stated level (e.g. 'beginner', 'grade 9', 'college'); null if not stated.\n"
            "- Use the recent turns to resolve follow-ups such as 'and for 3 weeks?' or 'explain that again'.\n"
            f"- When unsure, choose '{DEFAULT_SKILL}'. Never invent a topic or level."
        )

    async def route(self, state: SessionState, message: str) -> RouteDecision:
        payload = {
            "recent_turns": state.llm_history(last=6),
            "student": state.profile.model_dump(),
            "quiz_in_progress": state.quiz is not None,
            "message": message,
        }
        raw = await self._llm.chat(
            [{"role": "system", "content": self._prompt},
             {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
            model=self._model, temperature=0.0, max_tokens=150,
        )
        try:
            decision = RouteDecision.model_validate_json(extract_json_object(raw) or "")
        except ValidationError:
            return RouteDecision(skill=DEFAULT_SKILL)
        if decision.skill not in self._names:
            decision.skill = DEFAULT_SKILL
        return decision
