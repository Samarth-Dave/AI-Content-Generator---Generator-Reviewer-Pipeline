from __future__ import annotations

import pytest
from pydantic import ValidationError

from schemas import GeneratorOutput, MCQItem, ReviewStatus, ReviewerOutput


def test_mcq_answer_must_match_option():
    with pytest.raises(ValidationError):
        MCQItem(
            question="What is an acute angle?",
            options=["Less than 90 degrees", "Exactly 90 degrees", "More than 90 degrees", "A line"],
            answer="Not an option",
        )


def test_mcq_requires_four_options():
    with pytest.raises(ValidationError):
        MCQItem(
            question="What is an acute angle?",
            options=["Less than 90 degrees"],
            answer="Less than 90 degrees",
        )


def test_generator_output_requires_mcq():
    with pytest.raises(ValidationError):
        GeneratorOutput(explanation="This is a valid explanation that is long enough.", mcqs=[])


def test_reviewer_output_allows_pass_and_fail():
    assert ReviewerOutput(status=ReviewStatus.PASS, feedback=[]).status == ReviewStatus.PASS
    assert ReviewerOutput(status=ReviewStatus.FAIL, feedback=["Needs revision"]).status == ReviewStatus.FAIL
