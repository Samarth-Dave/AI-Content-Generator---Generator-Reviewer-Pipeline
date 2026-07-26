from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from agents.generator_v2 import generate_content, refine_content
from agents.reviewer_v2 import review_content
from agents.tagger_v2 import tag_content
from llm import LLMResponseError
from persistence import persist_artifact
from schemas_v2 import AttemptRecord, FinalResult, RunArtifact, RunInput, Timestamps


MAX_REFINEMENTS = 2


def build_generation_failed_artifact(run_id: str, grade: int, topic: str, user_id: str, started_at: datetime) -> RunArtifact:
    artifact = RunArtifact(
        run_id=run_id,
        input=RunInput(grade=grade, topic=topic, user_id=user_id),
        attempts=[],
        final=FinalResult(status="generation_failed", content=None, tags=None),
        timestamps=Timestamps(started_at=started_at, finished_at=datetime.utcnow()),
    )
    persist_artifact(artifact)
    return artifact


def run_pipeline(grade: int, topic: str, user_id: str = "default_user") -> RunArtifact:
    run_id = str(uuid4())
    started_at = datetime.utcnow()

    try:
        content = generate_content(grade, topic)
    except LLMResponseError:
        return build_generation_failed_artifact(run_id, grade, topic, user_id, started_at)

    attempts: list[AttemptRecord] = []
    refinements_used = 0

    for attempt_num in range(1, MAX_REFINEMENTS + 2):
        review = review_content(content, grade, topic)
        record = AttemptRecord(attempt=attempt_num, draft=content, review=review, refined=None)

        if review.pass_:
            attempts.append(record)
            final_status = "approved"
            final_content = content
            break

        if refinements_used >= MAX_REFINEMENTS:
            attempts.append(record)
            final_status = "rejected"
            final_content = content
            break

        try:
            refined = refine_content(grade, topic, review.feedback)
        except LLMResponseError:
            attempts.append(record)
            final_status = "rejected"
            final_content = content
            break

        record.refined = refined
        attempts.append(record)
        refinements_used += 1
        content = refined
    else:
        final_status = "rejected"
        final_content = content

    tags = tag_content(final_content, grade, topic) if final_status == "approved" else None
    artifact = RunArtifact(
        run_id=run_id,
        input=RunInput(grade=grade, topic=topic, user_id=user_id),
        attempts=attempts,
        final=FinalResult(status=final_status, content=final_content, tags=tags),
        timestamps=Timestamps(started_at=started_at, finished_at=datetime.utcnow()),
    )
    persist_artifact(artifact)
    return artifact