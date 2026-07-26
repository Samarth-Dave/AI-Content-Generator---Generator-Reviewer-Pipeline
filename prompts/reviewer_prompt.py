from __future__ import annotations


def build_reviewer_prompt(grade: int, topic: str, content_json: str) -> str:
    return f"""You are reviewing educational content written for Grade {grade} students on the topic \"{topic}\".

Evaluate the content against exactly these criteria:
1. Age appropriateness - is the vocabulary and sentence complexity right for Grade {grade}?
2. Conceptual correctness - is every fact correct and is the MCQ answer actually correct?
3. Clarity - is anything ambiguous or could more than one answer be defended?

Return status \"fail\" if any criterion is violated anywhere in the content.
If status is \"pass\", return an empty feedback list.

Return ONLY valid JSON with this exact shape:
{{
  "status": "pass" | "fail",
  "feedback": ["string"]
}}

Content to review:
{content_json}
"""
