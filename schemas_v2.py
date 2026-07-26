from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExplanationBlock(BaseModel):
    text: str = Field(..., min_length=20)
    grade: int = Field(..., ge=1, le=12)


class MCQItemV2(BaseModel):
    question: str = Field(..., min_length=5)
    options: list[str] = Field(..., min_length=4, max_length=4)
    correct_index: int = Field(..., ge=0, le=3, description="0-indexed position in 'options'")

    @model_validator(mode="after")
    def index_in_range(self):
        if not (0 <= self.correct_index < len(self.options)):
            raise ValueError(f"correct_index {self.correct_index} out of range for {len(self.options)} options")
        return self


class TeacherNotes(BaseModel):
    learning_objective: str = Field(..., min_length=10)
    common_misconceptions: list[str] = Field(..., min_length=1)


class GeneratorOutputV2(BaseModel):
    explanation: ExplanationBlock
    mcqs: list[MCQItemV2] = Field(..., min_length=1)
    teacher_notes: TeacherNotes


class ReviewScores(BaseModel):
    age_appropriateness: int = Field(..., ge=1, le=5)
    correctness: int = Field(..., ge=1, le=5)
    clarity: int = Field(..., ge=1, le=5)
    coverage: int = Field(..., ge=1, le=5)


class FeedbackItem(BaseModel):
    field: str
    issue: str


class ReviewerOutputV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scores: ReviewScores
    pass_: bool = Field(alias="pass")
    feedback: list[FeedbackItem] = Field(default_factory=list)

    @staticmethod
    def compute_pass(scores: ReviewScores) -> bool:
        all_at_least_adequate = all(
            s >= 3 for s in (scores.age_appropriateness, scores.correctness, scores.clarity, scores.coverage)
        )
        correctness_is_strong = scores.correctness >= 4
        return all_at_least_adequate and correctness_is_strong


class TaggerOutput(BaseModel):
    subject: str
    topic: str
    grade: int = Field(..., ge=1, le=12)
    difficulty: Literal["Easy", "Medium", "Hard"]
    content_type: list[str] = Field(..., min_length=1)
    blooms_level: Literal["Remembering", "Understanding", "Applying", "Analyzing", "Evaluating", "Creating"]


class AttemptRecord(BaseModel):
    attempt: int
    draft: GeneratorOutputV2
    review: ReviewerOutputV2
    refined: Optional[GeneratorOutputV2] = None


class RunInput(BaseModel):
    grade: int = Field(..., ge=1, le=12)
    topic: str
    user_id: str = "default_user"


class FinalResult(BaseModel):
    status: Literal["approved", "rejected", "generation_failed"]
    content: Optional[GeneratorOutputV2] = None
    tags: Optional[TaggerOutput] = None


class Timestamps(BaseModel):
    started_at: datetime
    finished_at: Optional[datetime] = None


class RunArtifact(BaseModel):
    run_id: str
    input: RunInput
    attempts: list[AttemptRecord]
    final: FinalResult
    timestamps: Timestamps