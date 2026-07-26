from __future__ import annotations

from unittest.mock import patch

from llm import LLMResponseError
from orchestrator_v2 import run_pipeline
from schemas_v2 import FeedbackItem, GeneratorOutputV2, ReviewScores, ReviewerOutputV2, TaggerOutput


def build_draft(topic: str = "Fractions") -> GeneratorOutputV2:
    return GeneratorOutputV2(
        explanation={"text": f"Fractions show how a whole can be split into equal parts for {topic}.", "grade": 5},
        mcqs=[
            {
                "question": "What does 1/2 mean?",
                "options": ["One of two equal parts", "Two of one equal part", "A whole", "Three equal parts"],
                "correct_index": 0,
            }
        ],
        teacher_notes={
            "learning_objective": "Students will identify fractions as equal parts of a whole.",
            "common_misconceptions": ["Thinking the denominator shows how many parts are shaded."],
        },
    )


def build_review(pass_value: bool, issue: str = "Use simpler language") -> ReviewerOutputV2:
    return ReviewerOutputV2(
        scores=ReviewScores(age_appropriateness=3, correctness=4, clarity=3, coverage=3),
        pass_=pass_value,
        feedback=[] if pass_value else [FeedbackItem(field="explanation.text", issue=issue)],
    )


def build_tag() -> TaggerOutput:
    return TaggerOutput(
        subject="Mathematics",
        topic="Fractions",
        grade=5,
        difficulty="Medium",
        content_type=["Explanation", "Quiz"],
        blooms_level="Understanding",
    )


def test_schema_validation_failure_returns_generation_failed_artifact():
    with patch("agents.generator_v2.call_groq_structured", side_effect=LLMResponseError("bad json")), patch(
        "orchestrator_v2.persist_artifact"
    ):
        artifact = run_pipeline(grade=5, topic="Fractions", user_id="alice")

    assert artifact.final.status == "generation_failed"
    assert artifact.attempts == []
    assert artifact.final.content is None
    assert artifact.final.tags is None


def test_fail_refine_pass_runs_tagger_once():
    draft = build_draft()
    refined = build_draft(topic="Fractions refined")

    with patch("orchestrator_v2.generate_content", return_value=draft), patch(
        "orchestrator_v2.review_content", side_effect=[build_review(False), build_review(True)]
    ) as mock_review, patch("orchestrator_v2.refine_content", return_value=refined) as mock_refine, patch(
        "orchestrator_v2.tag_content", return_value=build_tag()
    ) as mock_tag, patch("orchestrator_v2.persist_artifact"):
        artifact = run_pipeline(grade=5, topic="Fractions", user_id="alice")

    assert mock_review.call_count == 2
    assert mock_refine.call_count == 1
    assert mock_tag.call_count == 1
    assert artifact.final.status == "approved"
    assert artifact.final.tags is not None
    assert len(artifact.attempts) == 2
    assert artifact.attempts[0].refined == refined


def test_fail_refine_fail_rejects_after_full_cap():
    draft = build_draft()
    refined_1 = build_draft(topic="Fractions refined 1")
    refined_2 = build_draft(topic="Fractions refined 2")

    with patch("orchestrator_v2.generate_content", return_value=draft), patch(
        "orchestrator_v2.review_content",
        side_effect=[build_review(False, "First issue"), build_review(False, "Second issue"), build_review(False, "Third issue")],
    ) as mock_review, patch("orchestrator_v2.refine_content", side_effect=[refined_1, refined_2]) as mock_refine, patch(
        "orchestrator_v2.tag_content"
    ) as mock_tag, patch("orchestrator_v2.persist_artifact"):
        artifact = run_pipeline(grade=5, topic="Fractions", user_id="alice")

    assert mock_review.call_count == 3
    assert mock_refine.call_count == 2
    assert mock_tag.call_count == 0
    assert artifact.final.status == "rejected"
    assert artifact.final.tags is None
    assert len(artifact.attempts) == 3
    assert artifact.attempts[-1].refined is None
