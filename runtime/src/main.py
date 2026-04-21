from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .orchestrator import run_pipeline

app = FastAPI(title="Agent Runtime", version="0.1.0")


class RunRequest(BaseModel):
    chapter_id: str = Field(..., description="章节唯一ID")
    brief: str = Field(..., description="本章创作需求")
    target_words: int = Field(default=2000, ge=500, le=6000)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/chapters/run")
def run_chapter(payload: RunRequest) -> dict:
    try:
        return run_pipeline(payload.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
