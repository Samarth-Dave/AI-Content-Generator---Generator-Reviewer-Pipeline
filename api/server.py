from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from orchestrator_v2 import run_pipeline
from persistence import load_artifacts, init_db


app = FastAPI(title="Eklavya AI Content Pipeline API")


@app.on_event("startup")
def startup_event() -> None:
    init_db()


class PipelineRequest(BaseModel):
    grade: int = Field(..., ge=1, le=12)
    topic: str = Field(..., min_length=2)
    user_id: str | None = None


@app.post("/generate")
def generate_content(request: PipelineRequest):
    try:
        result = run_pipeline(
            grade=request.grade,
            topic=request.topic,
            user_id=request.user_id or "default_user",
        )
        return result.model_dump(mode="json", by_alias=True)
    except Exception as exc:  # pragma: no cover - FastAPI safety net
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/history")
def history(user_id: str | None = None):
    artifacts = load_artifacts(user_id=user_id)
    return [artifact.model_dump(mode="json", by_alias=True) for artifact in artifacts]
