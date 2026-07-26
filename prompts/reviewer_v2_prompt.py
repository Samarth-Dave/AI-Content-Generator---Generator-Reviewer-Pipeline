from __future__ import annotations


def build_reviewer_prompt(grade: int, topic: str, content_json: str) -> str:
    return f"""You are reviewing educational content written for Grade {grade} students on the topic \"{topic}\".

Evaluate the content against exactly these criteria:
1. Age appropriateness - is the vocabulary and sentence complexity right for Grade {grade}?
2. Correctness - are the explanation, MCQ answer, and teacher notes factually correct?
3. Clarity - is the content easy to understand and unambiguous?
4. Coverage - does it cover the topic enough for a basic classroom artifact?

Return only valid JSON with this exact shape:
{{
  "scores": {{
    "age_appropriateness": 1,
    "correctness": 1,
    "clarity": 1,
    "coverage": 1
  }},
  "pass": true,
  "feedback": [
    {{ "field": "explanation.text", "issue": "Sentence too complex" }}
  ]
}}

Feedback rules:
- Every feedback field must point to a real dotted path into the content.
- Use paths like explanation.text, mcqs[0].question, mcqs[0].options, mcqs[0].correct_index, teacher_notes.learning_objective, or teacher_notes.common_misconceptions.
- Return an empty feedback list only when the content satisfies every criterion.

Content to review:
{content_json}
"""