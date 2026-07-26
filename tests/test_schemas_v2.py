from __future__ import annotations

from schemas_v2 import ReviewScores, ReviewerOutputV2


def test_reviewer_output_uses_pass_alias():
    review = ReviewerOutputV2(
        scores=ReviewScores(age_appropriateness=4, correctness=4, clarity=4, coverage=4),
        pass_=True,
        feedback=[],
    )

    assert "pass" in review.model_dump(by_alias=True)


def test_compute_pass_requires_correctness_at_least_four():
    scores = ReviewScores(age_appropriateness=5, correctness=3, clarity=5, coverage=5)

    assert ReviewerOutputV2.compute_pass(scores) is False