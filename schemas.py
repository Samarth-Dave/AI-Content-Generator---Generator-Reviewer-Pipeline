from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class GeneratorRequest(BaseModel):
    grade: int = Field(..., ge=1, le=12)
    topic: str = Field(..., min_length=2)
    feedback: Optional[list[str]] = Field(default=None)
    mcq_count: int = Field(default=3, ge=3, le=8)


class MCQItem(BaseModel):
    question: str = Field(..., min_length=5)
    options: list[str] = Field(..., min_length=4, max_length=4)
    answer: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_answer(self):
        if self.answer not in self.options:
            raise ValueError("answer must exactly match one of the provided options")
        return self


class GeneratorOutput(BaseModel):
    explanation: str = Field(..., min_length=20)
    mcqs: list[MCQItem] = Field(..., min_length=1)


class ReviewerRequest(BaseModel):
    content: GeneratorOutput
    grade: int = Field(..., ge=1, le=12)
    topic: str = Field(..., min_length=2)


class ReviewStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"


class ReviewerOutput(BaseModel):
    status: ReviewStatus
    feedback: list[str] = Field(default_factory=list)


class PipelineResult(BaseModel):
    original_output: GeneratorOutput
    review: ReviewerOutput
    refined_output: Optional[GeneratorOutput] = None
    refined_review: Optional[ReviewerOutput] = None
