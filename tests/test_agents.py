from __future__ import annotations

from unittest.mock import patch

from agents.generator import generate
from agents.reviewer import review
from schemas import GeneratorOutput, GeneratorRequest, MCQItem, ReviewStatus, ReviewerOutput, ReviewerRequest


FAKE_GENERATOR_OUTPUT = GeneratorOutput(
    explanation="An angle is formed when two rays meet at a point.",
    mcqs=[
        MCQItem(
            question="Which angle is less than 90 degrees?",
            options=["Acute", "Right", "Obtuse", "Straight"],
            answer="Acute",
        )
    ],
)


def test_generator_uses_feedback_in_prompt():
    with patch("agents.generator.call_groq_structured", return_value=FAKE_GENERATOR_OUTPUT) as mock_call:
        generate(GeneratorRequest(grade=4, topic="Types of angles", feedback=["Use simpler words"]))

    assert mock_call.call_count == 1
    kwargs = mock_call.call_args.kwargs
    assert "Use simpler words" in kwargs["system_prompt"]


def test_reviewer_uses_grade_and_topic():
    with patch("agents.reviewer.call_groq_structured", return_value=ReviewerOutput(status=ReviewStatus.PASS, feedback=[])) as mock_call:
        review(ReviewerRequest(content=FAKE_GENERATOR_OUTPUT, grade=4, topic="Types of angles"))

    assert mock_call.call_count == 1
    kwargs = mock_call.call_args.kwargs
    assert kwargs["temperature"] == 0.0
    assert "Types of angles" in kwargs["user_prompt"]
