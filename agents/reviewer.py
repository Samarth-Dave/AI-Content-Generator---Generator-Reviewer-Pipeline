from __future__ import annotations

from llm import call_groq_structured
from prompts.reviewer_prompt import build_reviewer_prompt
from schemas import ReviewerOutput, ReviewerRequest
from settings import get_settings


def review(request: ReviewerRequest) -> ReviewerOutput:
    prompt = build_reviewer_prompt(
        grade=request.grade,
        topic=request.topic,
        content_json=request.content.model_dump_json(indent=2),
    )
    settings = get_settings()
    return call_groq_structured(
        system_prompt="You are a strict educational content reviewer.",
        user_prompt=prompt,
        response_model=ReviewerOutput,
        temperature=settings.reviewer_temperature,
        max_tokens=900,
    )
