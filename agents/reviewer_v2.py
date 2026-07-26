from __future__ import annotations

import re

from llm import LLMResponseError, call_groq_structured
from prompts.reviewer_v2_prompt import build_reviewer_prompt
from schemas_v2 import FeedbackItem, GeneratorOutputV2, ReviewScores, ReviewerOutputV2
from settings import get_settings


FEEDBACK_FIELD_PATTERN = re.compile(
    r"^(?:explanation\.text|teacher_notes\.(?:learning_objective|common_misconceptions)|mcqs\[(?:0|[1-9]\d*)\]\.(?:question|options|correct_index))$"
)


def _feedback_paths_are_valid(feedback: list[FeedbackItem]) -> bool:
    return all(FEEDBACK_FIELD_PATTERN.fullmatch(item.field) for item in feedback)


def review_content(content: GeneratorOutputV2, grade: int, topic: str) -> ReviewerOutputV2:
    prompt = build_reviewer_prompt(
        grade=grade,
        topic=topic,
        content_json=content.model_dump_json(indent=2, by_alias=True),
    )
    settings = get_settings()

    last_error: Exception | None = None
    for _ in range(2):
        try:
            raw_review = call_groq_structured(
                system_prompt="You are a strict educational content reviewer.",
                user_prompt=prompt,
                response_model=ReviewerOutputV2,
                temperature=settings.reviewer_temperature,
                max_tokens=900,
            )
            if not _feedback_paths_are_valid(raw_review.feedback):
                raise LLMResponseError("Reviewer returned feedback with invalid field paths.")

            return ReviewerOutputV2(
                scores=raw_review.scores,
                pass_=ReviewerOutputV2.compute_pass(raw_review.scores),
                feedback=raw_review.feedback,
            )
        except LLMResponseError as exc:
            last_error = exc

    raise LLMResponseError(f"Reviewer failed validation after retry: {last_error}")


def review_scores_pass(scores: ReviewScores) -> bool:
    return ReviewerOutputV2.compute_pass(scores)