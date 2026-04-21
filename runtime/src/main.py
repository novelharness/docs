from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .kernel import runtime_kernel
from .orchestrator import run_pipeline

app = FastAPI(title="Agent Runtime", version="0.3.0")


class RunRequest(BaseModel):
    chapter_id: str = Field(..., description="章节唯一ID")
    brief: str = Field(..., description="本章创作需求")
    target_words: int = Field(default=2000, ge=500, le=6000)
    shared_state: dict[str, Any] | None = Field(default=None, description="可选：外部注入状态快照")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/chapters/run")
def run_chapter(payload: RunRequest) -> dict:
    return run_pipeline(payload.model_dump())


@app.post("/api/v1/runs")
def create_run(payload: RunRequest) -> dict:
    run = runtime_kernel.create_run(payload.model_dump())
    return {"run_id": run.run_id, "status": run.status, "tasks": len(run.tasks)}


@app.post("/api/v1/runs/{run_id}/execute")
def execute_run(run_id: str) -> dict:
    try:
        run = runtime_kernel.execute_all(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "run_id": run.run_id,
        "status": run.status,
        "events": run.events,
        "steps": [
            {
                "task_id": task.task_id,
                "agent_id": task.agent_id,
                "status": task.status,
                "attempts": task.attempts,
            }
            for task in run.tasks
        ],
    }


@app.get("/api/v1/runs/{run_id}")
def get_run(run_id: str) -> dict:
    try:
        run = runtime_kernel.get_run(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "run_id": run.run_id,
        "status": run.status,
        "chapter_id": run.chapter_id,
        "events": run.events,
        "steps": [
            {
                "task_id": task.task_id,
                "agent_id": task.agent_id,
                "status": task.status,
                "attempts": task.attempts,
            }
            for task in run.tasks
        ],
    }
