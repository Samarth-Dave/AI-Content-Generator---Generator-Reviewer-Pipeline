from __future__ import annotations

from llm import LLMResponseError, call_groq_structured
from prompts.generator_v2_prompt import build_generator_prompt
from schemas_v2 import FeedbackItem, GeneratorOutputV2
from settings import get_settings


def _normalize_feedback(feedback: list[FeedbackItem] | list[str] | None) -> list[str] | None:
    if not feedback:
        return None

    normalized: list[str] = []
    for item in feedback:
        if isinstance(item, str):
            normalized.append(item)
        else:
            normalized.append(f"{item.field}: {item.issue}")
    return normalized


def generate_content(grade: int, topic: str, feedback: list[FeedbackItem] | list[str] | None = None) -> GeneratorOutputV2:
    system_prompt, user_prompt = build_generator_prompt(grade=grade, topic=topic, feedback=_normalize_feedback(feedback))
    settings = get_settings()

    last_error: Exception | None = None
    for _ in range(2):
        try:
            return call_groq_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=GeneratorOutputV2,
                temperature=settings.generator_temperature,
                max_tokens=1400,
            )
        except LLMResponseError as exc:
            last_error = exc

    raise LLMResponseError(f"Generator failed schema validation after one retry: {last_error}")


def refine_content(grade: int, topic: str, feedback: list[FeedbackItem]) -> GeneratorOutputV2:
    return generate_content(grade=grade, topic=topic, feedback=feedback)