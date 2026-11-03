from .base import PromptSkill


class ExplainSkill(PromptSkill):
    name = "explain"
    description = (
        "Explain a concept, topic, term or how something works; summaries; 'what is', 'why', "
        "'how does'. Also the default for general study questions."
    )
    instructions = (
        "Teach the concept: start with a plain-language definition, then build intuition (an "
        "analogy or picture in words), give one worked example, mention a common misconception, "
        "and finish with a short check-your-understanding question. Match depth to the student's "
        "level and keep it as short as the question allows."
    )


class SolveSkill(PromptSkill):
    name = "solve"
    description = (
        "Solve a specific problem or exercise step by step: maths, physics, chemistry, statistics, "
        "coding, homework questions, equations, proofs."
    )
    instructions = (
        "Solve the problem step by step. Restate what is given and what is asked, show each step "
        "with the reason for it, double-check the result, and state the final answer clearly. "
        "For code, give a fenced code block and explain it. If the problem is ambiguous or missing "
        "data, ask exactly what you need instead of guessing."
    )
    temperature = 0.2


class CurriculumSkill(PromptSkill):
    name = "curriculum"
    description = (
        "Create a curriculum, syllabus, course outline, roadmap or learning path for a subject or skill."
    )
    instructions = (
        "Design a curriculum: a one-line goal, assumed prerequisites, then ordered modules. For each "
        "module give learning outcomes, key topics, a practice activity or project, and a rough "
        "duration; end with a final capstone and how progress is assessed. Recommend types of "
        "resources (and well-known titles only if you are sure they exist), never invented links."
    )


class StudyPlanSkill(PromptSkill):
    name = "study_plan"
    description = (
        "Create a study plan, schedule, timetable or revision plan with time constraints "
        "(exam in N weeks, X hours per day, prepare for a test or goal)."
    )
    instructions = (
        "Build a realistic study plan. If timeframe, weekly hours or the goal are missing, state "
        "your assumptions in one line and proceed (offer to adjust). Lay it out week by week (or day "
        "by day for short plans) with focused tasks, spaced revision, practice tests and a buffer "
        "day. Order topics from foundations to hardest, and end with tips to stay on track."
    )

class InstituteSkill(PromptSkill):
    name = "institute"
    description = (
        "Information about universities, colleges, schools, institutes, online platforms or "
        "educational organizations."
    )
    instructions = (
        "Provide general information about the institute: location, type (public/private), "
        "programs offered, reputation, and notable achievements. Avoid giving specific fees, "
        "deadlines, or entry requirements as these can change; instead, advise the student to "
        "check the official website for the most accurate and up-to-date information."
    )

class CourseSkill(PromptSkill):
    name = "course"
    description = (
        "Information about specific courses, classes, or training programs offered by educational "
        "institutions or online platforms."
    )
    instructions = (
        "Provide general information about the course: overview, objectives, duration, prerequisites, "
        "and key topics covered. Avoid giving specific fees, deadlines, or entry requirements as these "
        "can change; instead, advise the student to check the official course page for the most accurate "
        "and up-to-date information."
    )