from __future__ import annotations

from agents.generator import generate
from agents.reviewer import review
from schemas import GeneratorRequest, PipelineResult, ReviewStatus, ReviewerRequest


def run_pipeline(grade: int, topic: str, re_review_refinement: bool = True, mcq_count: int = 3) -> PipelineResult:
    original_output = generate(GeneratorRequest(grade=grade, topic=topic, mcq_count=mcq_count))
    review_result = review(ReviewerRequest(content=original_output, grade=grade, topic=topic))

    if review_result.status == ReviewStatus.PASS:
        return PipelineResult(original_output=original_output, review=review_result)

    refined_output = generate(
        GeneratorRequest(grade=grade, topic=topic, feedback=review_result.feedback, mcq_count=mcq_count)
    )

    refined_review = None
    if re_review_refinement:
        refined_review = review(ReviewerRequest(content=refined_output, grade=grade, topic=topic))

    return PipelineResult(
        original_output=original_output,
        review=review_result,
        refined_output=refined_output,
        refined_review=refined_review,
    )
