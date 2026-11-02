def extract_json_object(text: str) -> str | None:
    """Return the outermost {...} in an LLM reply (tolerates prose and code fences)."""
    start, end = text.find("{"), text.rfind("}")
    return text[start : end + 1] if 0 <= start < end else None
