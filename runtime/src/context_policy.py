from __future__ import annotations

from typing import Any


DEFAULT_LOOKBACK = 6


def _is_visible(targets: list[str], agent_id: str) -> bool:
    return "*" in targets or agent_id in targets


def filter_visible_events(events: list[dict[str, Any]], agent_id: str, lookback: int = DEFAULT_LOOKBACK) -> list[dict[str, Any]]:
    visible = []
    for item in events:
        targets = item.get("visible_to", ["*"])
        if _is_visible(targets, agent_id):
            visible.append(item)
    return visible[-lookback:]


def filter_known_facts(facts: list[dict[str, Any]], agent_id: str) -> list[dict[str, Any]]:
    result = []
    for item in facts:
        known_by = item.get("known_by", ["*"])
        if _is_visible(known_by, agent_id):
            result.append(item)
    return result


def build_agent_packet(agent_id: str, run_input: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    events = state.get("events", [])
    facts = state.get("facts", [])
    role_core = state.get("role_core", {}).get(agent_id, [])

    return {
        "chapter_id": run_input["chapter_id"],
        "task_goal": run_input["brief"],
        "target_words": run_input["target_words"],
        "recent_events": filter_visible_events(events, agent_id),
        "known_facts": filter_known_facts(facts, agent_id),
        "role_core": role_core,
    }


def validate_role_output(agent_id: str, output: dict[str, Any], packet: dict[str, Any]) -> tuple[bool, str]:
    role_core = packet.get("role_core", [])
    if not role_core:
        return True, "ok"

    narrative = str(output.get("summary", ""))
    for keyword in role_core:
        if keyword not in narrative:
            return False, f"missing role-core keyword '{keyword}' for {agent_id}"
    return True, "ok"
