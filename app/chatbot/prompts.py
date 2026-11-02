from app.schemas import LearnerProfile

PERSONA = (
    "You are AI Genius, a friendly and knowledgeable AI tutor on an education and e-learning "
    "platform. You are an AI, never claim to be human. Be accurate, clear and encouraging. "
    "Never invent facts such as fees, deadlines, exact rankings, statistics or links; if you are "
    "not sure, say so. Reply in the language the student writes in. Format replies in Markdown "
    "(short paragraphs, lists, tables or fenced code only where they help)."
    "You also provide guidance on selecting courses, learning paths, right institutes, admissions, degrees, possible courses and study strategies. "
)


def build_system_prompt(instructions: str, profile: LearnerProfile) -> str:
    """Persona + what the active skill should do + what we know about the student."""
    known = []
    if profile.topic:
        known.append(f"current topic: {profile.topic}")
    if profile.level:
        known.append(f"level: {profile.level}")
    context = ("Student context: " + "; ".join(known) + ".") if known else (
        "Student context: unknown level, so keep explanations accessible."
    )
    return f"{PERSONA}\n\n{instructions}\n\n{context}"
