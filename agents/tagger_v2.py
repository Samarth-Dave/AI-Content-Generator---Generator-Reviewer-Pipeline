from __future__ import annotations

from llm import call_groq_structured
from prompts.tagger_prompt import build_tagger_prompt
from schemas_v2 import GeneratorOutputV2, TaggerOutput
from settings import get_settings


def tag_content(content: GeneratorOutputV2, grade: int, topic: str) -> TaggerOutput:
    system_prompt, user_prompt = build_tagger_prompt(
        grade=grade,
        topic=topic,
        content_json=content.model_dump_json(indent=2, by_alias=True),
    )
    settings = get_settings()
    return call_groq_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=TaggerOutput,
        temperature=settings.reviewer_temperature,
        max_tokens=500,
    )