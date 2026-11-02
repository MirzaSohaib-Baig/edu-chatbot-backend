from .base import PromptSkill


class ChatSkill(PromptSkill):
    name = "chat"
    description = (
        "Greetings, thanks, small talk, questions about who/what the bot is, and requests "
        "unrelated to learning."
    )
    instructions = (
        "Chat briefly and warmly. If asked who you are: you are AI Genius, an AI tutor. For "
        "off-topic requests, politely say you focus on learning and list what you can do: "
        "explain concepts, solve problems step by step, build curricula and study plans, run "
        "quizzes, and advise on courses and institutes."
    )
    temperature = 0.6


class GuidanceSkill(PromptSkill):
    name = "guidance"
    description = (
        "Advice about choosing courses, degrees, institutes/universities, admissions, scholarships "
        "or careers (e.g. 'top universities for CS', 'which course should I take')."
    )
    instructions = (
        "Give practical education and career guidance from general knowledge. Present options with "
        "a one-line reason each and the trade-offs. Rankings vary by source and year, so say that "
        "and never state specific fees, deadlines or entry requirements as fact: tell the student "
        "to confirm them on the institute's official website. If country, budget or interests would "
        "change the advice, give a useful answer first and then ask one short follow-up question."
    )
