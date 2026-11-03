from app.config import Settings

from .base import PromptSkill, Skill, SkillContext
from .general import ChatSkill, GuidanceSkill
from .learning import CurriculumSkill, ExplainSkill, SolveSkill, StudyPlanSkill, InstituteSkill, CourseSkill
from .quiz import QuizAnswerSkill, QuizSkill
from .registry import SkillRegistry


def default_registry(settings: Settings) -> SkillRegistry:
    """All built-in skills. To add one, write a Skill subclass and add it here."""
    return SkillRegistry(
        [
            ChatSkill(),
            ExplainSkill(),
            SolveSkill(),
            CurriculumSkill(),
            StudyPlanSkill(),
            GuidanceSkill(),
            QuizSkill(settings),
            QuizAnswerSkill(),
            InstituteSkill(),
            CourseSkill(),
        ]
    )


__all__ = ["PromptSkill", "Skill", "SkillContext", "SkillRegistry", "default_registry"]
