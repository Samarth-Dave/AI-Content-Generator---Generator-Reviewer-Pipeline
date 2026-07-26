from __future__ import annotations


def build_tagger_prompt(grade: int, topic: str, content_json: str) -> tuple[str, str]:
    system_prompt = f"""You classify approved educational content for indexing.

Return only valid JSON with this exact shape:
{{
  "subject": "Mathematics",
  "topic": "{topic}",
  "grade": {grade},
  "difficulty": "Medium",
  "content_type": ["Explanation", "Quiz"],
  "blooms_level": "Understanding"
}}

Rules:
- Only classify content that has already been approved.
- Use one subject, one topic, one grade, one difficulty, a list of content types, and a single Bloom's level.
- Keep the labels concise and educationally sensible.
"""
    user_prompt = f"Classify the approved content below for Grade {grade} on the topic {topic}.\n\n{content_json}"
    return system_prompt, user_prompt