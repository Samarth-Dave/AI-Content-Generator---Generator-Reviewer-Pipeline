from __future__ import annotations


GRADE_BAND_GUIDANCE = {
    range(1, 3): "Very short sentences, everyday words only, and concrete examples.",
    range(3, 6): "Short to medium sentences, simple subject terms, and friendly examples.",
    range(6, 9): "Medium sentences, subject vocabulary with brief definitions, and clear cause-and-effect.",
    range(9, 11): "Medium-long sentences, standard subject vocabulary, and more analytical phrasing.",
    range(11, 13): "Full technical vocabulary, precise definitions, and exam-oriented clarity.",
}


def grade_band_text(grade: int) -> str:
    for band, text in GRADE_BAND_GUIDANCE.items():
        if grade in band:
            return text
    return "Use age-appropriate language."


def build_generator_prompt(
    grade: int,
    topic: str,
    feedback: list[str] | None = None,
) -> tuple[str, str]:
    system_prompt = f"""You are an educational content writer for Grade {grade} students.

Create content about \"{topic}\" that fits this grade band:
{grade_band_text(grade)}

Return ONLY valid JSON with this exact shape:
{{
  "explanation": {{
    "text": "string",
    "grade": {grade}
  }},
  "mcqs": [
    {{
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "correct_index": 0
    }}
  ],
  "teacher_notes": {{
    "learning_objective": "string",
    "common_misconceptions": ["string"]
  }}
}}

Rules:
- Keep the language age-appropriate for Grade {grade}.
- Every MCQ must have exactly 4 plausible options.
- correct_index must point to the correct option using a 0-indexed integer.
- Do not include markdown fences or commentary.
- Every fact must be correct and limited to the topic.
"""

    if feedback:
        feedback_lines = "\n".join(f"- {item}" for item in feedback)
        system_prompt += f"""

Revision feedback from the reviewer:
{feedback_lines}

Fix every issue above and do not reintroduce them.
"""

    user_prompt = f"Generate the educational content for Grade {grade} on the topic {topic}."
    return system_prompt, user_prompt