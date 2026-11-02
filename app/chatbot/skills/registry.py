from collections.abc import Iterable

from .base import Skill, SkillContext


class SkillRegistry:
    def __init__(self, skills: Iterable[Skill] = ()):
        self._skills: dict[str, Skill] = {}
        for s in skills:
            self.register(s)

    def register(self, skill: Skill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' is already registered")
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        return self._skills[name]

    def routable(self) -> list[Skill]:
        return [s for s in self._skills.values() if s.routable]

    def find_interceptor(self, ctx: SkillContext) -> Skill | None:
        return next((s for s in self._skills.values() if s.intercepts(ctx)), None)
