from __future__ import annotations

from llm import call_groq_structured
from prompts.generator_prompt import build_generator_prompt
from schemas import GeneratorOutput, GeneratorRequest
from settings import get_settings


def generate(request: GeneratorRequest) -> GeneratorOutput:
    system_prompt, user_prompt = build_generator_prompt(
        grade=request.grade,
        topic=request.topic,
        feedback=request.feedback,
        mcq_count=request.mcq_count,
    )
    settings = get_settings()
    return call_groq_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=GeneratorOutput,
        temperature=settings.generator_temperature,
        max_tokens=1400,
    )
