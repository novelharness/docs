from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / "agents"

PIPELINE = [
    "director",
    "payoff_designer",
    "protagonist",
    "supporting_cast",
    "world_guardian",
    "quality_gate",
]


def _read_scalar(text: str, key: str, default: str = "") -> str:
    prefix = f"{key}:"
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith(prefix):
            return line[len(prefix) :].strip().strip('"')
    return default


def _load_agent(agent_name: str) -> dict:
    config_path = AGENTS_DIR / agent_name / "agent.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing agent config: {config_path}")
    text = config_path.read_text(encoding="utf-8")
    return {
        "agent_id": _read_scalar(text, "agent_id", agent_name),
        "version": _read_scalar(text, "version", "unknown"),
    }


def run_pipeline(input_data: dict) -> dict:
    steps: list[dict] = []
    working_context = {
        "chapter_id": input_data["chapter_id"],
        "brief": input_data["brief"],
        "target_words": input_data["target_words"],
    }

    for name in PIPELINE:
        cfg = _load_agent(name)
        step_output = {
            "agent_id": cfg["agent_id"],
            "version": cfg["version"],
            "summary": f"{name} completed for chapter {working_context['chapter_id']}",
        }
        steps.append(step_output)

    return {
        "status": "PASS",
        "chapter_id": working_context["chapter_id"],
        "pipeline": PIPELINE,
        "steps": steps,
        "draft_excerpt": "这是一个用于联调的草稿占位文本，可替换为真实LLM生成结果。",
    }
