from __future__ import annotations

from unittest.mock import patch

from orchestrator import run_pipeline
from schemas import GeneratorOutput, MCQItem, ReviewStatus, ReviewerOutput


FAKE_OUTPUT = GeneratorOutput(
    explanation="An angle is formed when two rays meet at a point.",
    mcqs=[
        MCQItem(
            question="Which angle is less than 90 degrees?",
            options=["Acute", "Right", "Obtuse", "Straight"],
            answer="Acute",
        )
    ],
)


def test_pipeline_stops_after_pass():
    with patch("orchestrator.generate", return_value=FAKE_OUTPUT) as mock_generate, patch(
        "orchestrator.review", return_value=ReviewerOutput(status=ReviewStatus.PASS, feedback=[])
    ) as mock_review:
        result = run_pipeline(grade=4, topic="Types of angles")

    assert mock_generate.call_count == 1
    assert mock_review.call_count == 1
    assert result.refined_output is None
    assert result.refined_review is None


def test_pipeline_refines_exactly_once_on_fail():
    with patch("orchestrator.generate", return_value=FAKE_OUTPUT) as mock_generate, patch(
        "orchestrator.review",
        side_effect=[
            ReviewerOutput(status=ReviewStatus.FAIL, feedback=["Use simpler words"]),
            ReviewerOutput(status=ReviewStatus.PASS, feedback=[]),
        ],
    ) as mock_review:
        result = run_pipeline(grade=4, topic="Types of angles")

    assert mock_generate.call_count == 2
    assert mock_review.call_count == 2
    assert result.refined_output is not None
    assert result.refined_review is not None


def test_pipeline_can_skip_refinement_rereview():
    with patch("orchestrator.generate", return_value=FAKE_OUTPUT) as mock_generate, patch(
        "orchestrator.review", return_value=ReviewerOutput(status=ReviewStatus.FAIL, feedback=["Fix it"])
    ) as mock_review:
        result = run_pipeline(grade=4, topic="Types of angles", re_review_refinement=False)

    assert mock_generate.call_count == 2
    assert mock_review.call_count == 1
    assert result.refined_output is not None
    assert result.refined_review is None
