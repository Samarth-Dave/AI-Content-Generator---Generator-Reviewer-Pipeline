from __future__ import annotations

import json
import re
from typing import TypeVar

from groq import Groq
from pydantic import BaseModel, ValidationError

from settings import get_settings


class LLMConfigurationError(RuntimeError):
    pass


class LLMResponseError(RuntimeError):
    pass


T = TypeVar("T", bound=BaseModel)


def get_groq_client() -> Groq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise LLMConfigurationError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your Groq key."
        )
    return Groq(api_key=settings.groq_api_key)


def get_model_name() -> str:
    return get_settings().groq_model


def _extract_json_payload(raw_content: str) -> str:
    stripped = raw_content.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped, count=1, flags=re.IGNORECASE).strip()
        stripped = re.sub(r"```$", "", stripped).strip()

    if stripped.startswith("{") or stripped.startswith("["):
        return stripped

    match = re.search(r"(\{.*\}|\[.*\])", stripped, flags=re.DOTALL)
    if match:
        return match.group(1)
    return stripped


def call_groq_structured(
    *,
    system_prompt: str,
    user_prompt: str,
    response_model: type[T],
    temperature: float,
    max_tokens: int,
) -> T:
    client = get_groq_client()
    model_name = get_model_name()

    response = client.chat.completions.create(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw_content = response.choices[0].message.content or ""
    try:
        payload = json.loads(_extract_json_payload(raw_content))
        return response_model.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise LLMResponseError(f"Unable to parse structured Groq response: {exc}") from exc
