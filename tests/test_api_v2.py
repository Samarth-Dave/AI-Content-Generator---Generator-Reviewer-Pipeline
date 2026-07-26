from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient

from api.server import app
from persistence import load_artifacts, persist_artifact
from schemas_v2 import AttemptRecord, FinalResult, GeneratorOutputV2, ReviewScores, ReviewerOutputV2, RunArtifact, RunInput, Timestamps


def build_artifact(run_id: str, user_id: str, status: str) -> RunArtifact:
    draft = GeneratorOutputV2(
        explanation={"text": "Fractions split a whole into equal parts for classroom learning.", "grade": 5},
        mcqs=[
            {
                "question": "What does 1/4 mean?",
                "options": ["One of four equal parts", "Four of one equal part", "One whole", "Two equal parts"],
                "correct_index": 0,
            }
        ],
        teacher_notes={
            "learning_objective": "Students identify fractions as equal parts of a whole.",
            "common_misconceptions": ["Thinking the denominator is the number shaded."],
        },
    )
    review = ReviewerOutputV2(
        scores=ReviewScores(age_appropriateness=4, correctness=4, clarity=4, coverage=4),
        pass_=True,
        feedback=[],
    )

    return RunArtifact(
        run_id=run_id,
        input=RunInput(grade=5, topic="Fractions", user_id=user_id),
        attempts=[AttemptRecord(attempt=1, draft=draft, review=review, refined=None)],
        final=FinalResult(status=status, content=draft, tags=None),
        timestamps=Timestamps(started_at=datetime.utcnow(), finished_at=datetime.utcnow()),
    )


def test_history_endpoint_filters_by_user_id(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'runs.db'}")
    first = build_artifact("run-1", "alice", "approved")
    second = build_artifact("run-2", "bob", "rejected")
    persist_artifact(first)
    persist_artifact(second)

    client = TestClient(app)
    response = client.get("/history", params={"user_id": "alice"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["input"]["user_id"] == "alice"
    assert load_artifacts("alice")[0].run_id == "run-1"