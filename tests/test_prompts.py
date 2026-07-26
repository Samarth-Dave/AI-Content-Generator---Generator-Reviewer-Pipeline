from __future__ import annotations

from prompts.generator_prompt import build_generator_prompt, grade_band_text
from prompts.reviewer_prompt import build_reviewer_prompt


def test_grade_band_text_changes_by_grade():
    assert "Very short" in grade_band_text(2)
    assert "technical" in grade_band_text(12).lower()


def test_generator_prompt_embeds_feedback():
    system_prompt, user_prompt = build_generator_prompt(4, "Types of angles", ["Too complex", "Fix answer text"])
    assert "Grade 4" in system_prompt
    assert "Too complex" in system_prompt
    assert "Types of angles" in system_prompt
    assert "Generate the educational content" in user_prompt


def test_reviewer_prompt_mentions_required_criteria():
    prompt = build_reviewer_prompt(4, "Types of angles", '{"explanation": "..."}')
    assert "Age appropriateness" in prompt
    assert "Conceptual correctness" in prompt
    assert "Clarity" in prompt
