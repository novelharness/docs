from __future__ import annotations

from typing import Any

from .kernel import runtime_kernel


def run_pipeline(input_data: dict[str, Any]) -> dict[str, Any]:
    run = runtime_kernel.create_run(input_data)
    run = runtime_kernel.execute_all(run.run_id)

    return {
        "status": run.status,
        "run_id": run.run_id,
        "chapter_id": run.chapter_id,
        "pipeline": [task.agent_id for task in run.tasks],
        "steps": [
            {
                "task_id": task.task_id,
                "agent_id": task.agent_id,
                "status": task.status,
                "attempts": task.attempts,
                "summary": task.result.summary if task.result else "",
                "received_events": task.result.received_events if task.result else 0,
                "received_facts": task.result.received_facts if task.result else 0,
                "role_core_check": task.result.role_core_check if task.result else {"ok": False, "reason": "no result"},
            }
            for task in run.tasks
        ],
        "events": run.events,
    }
