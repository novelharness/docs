from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / "agents"
SKILLS_DIR = ROOT / "skills"

app = FastAPI(title="Agent MCP Adapter", version="0.1.0")


class ToolCall(BaseModel):
    name: str
    arguments: dict


def _read_scalar(text: str, key: str, default: str = "") -> str:
    prefix = f"{key}:"
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith(prefix):
            return line[len(prefix) :].strip().strip('"')
    return default


def _load_skill(skill_id: str) -> dict:
    skill_path = SKILLS_DIR / skill_id / "skill.yaml"
    if not skill_path.exists():
        raise HTTPException(status_code=404, detail=f"skill not found: {skill_id}")
    text = skill_path.read_text(encoding="utf-8")
    return {
        "skill_id": _read_scalar(text, "skill_id", skill_id),
        "version": _read_scalar(text, "version", "unknown"),
        "description": _read_scalar(text, "description", ""),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tools/list")
def list_tools() -> dict:
    return {
        "tools": [
            {"name": "list_agents", "description": "列出可用agents"},
            {"name": "load_skill", "description": "读取技能定义"},
        ]
    }


@app.post("/tools/call")
def call_tool(payload: ToolCall) -> dict:
    if payload.name == "list_agents":
        agents = sorted([p.name for p in AGENTS_DIR.iterdir() if (p / "agent.yaml").exists()])
        return {"agents": agents}

    if payload.name == "load_skill":
        skill_id = payload.arguments.get("skill_id")
        if not skill_id:
            raise HTTPException(status_code=400, detail="skill_id required")
        return {"skill": _load_skill(skill_id)}

    raise HTTPException(status_code=404, detail=f"tool not found: {payload.name}")
