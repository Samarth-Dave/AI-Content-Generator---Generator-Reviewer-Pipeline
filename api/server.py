from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from llm import LLMConfigurationError, LLMResponseError
from orchestrator import run_pipeline


app = FastAPI(title="Eklavya AI Content Pipeline API")


class PipelineRequest(BaseModel):
    grade: int
    topic: str
    re_review_refinement: bool = True


@app.post("/generate")
def generate_content(request: PipelineRequest):
    try:
        result = run_pipeline(
            grade=request.grade,
            topic=request.topic,
            re_review_refinement=request.re_review_refinement,
        )
        return result.model_dump(mode="json")
    except (LLMConfigurationError, LLMResponseError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
