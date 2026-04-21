from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from .context_policy import build_agent_packet, validate_role_output

PIPELINE = [
    "director",
    "payoff_designer",
    "protagonist",
    "supporting_cast",
    "world_guardian",
    "quality_gate",
]


@dataclass
class TaskResult:
    agent_id: str
    summary: str
    received_events: int
    received_facts: int
    role_core_check: dict[str, Any]
    attempt: int


@dataclass
class AgentTask:
    task_id: str
    agent_id: str
    packet: dict[str, Any]
    status: str = "PENDING"
    attempts: int = 0
    result: TaskResult | None = None


@dataclass
class Run:
    run_id: str
    chapter_id: str
    brief: str
    target_words: int
    status: str = "PENDING"
    tasks: list[AgentTask] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)


class ClaudeCodeLikeRuntime:
    """In-memory runtime kernel inspired by ClaudeCode execution loops."""

    def __init__(self) -> None:
        self.runs: dict[str, Run] = {}

    def create_run(self, payload: dict[str, Any]) -> Run:
        run_id = f"run_{uuid4().hex[:10]}"
        state = payload.get("shared_state") or self._default_state()
        tasks = [
            AgentTask(
                task_id=f"task_{idx+1}_{name}",
                agent_id=name,
                packet=build_agent_packet(name, payload, state),
            )
            for idx, name in enumerate(PIPELINE)
        ]

        run = Run(
            run_id=run_id,
            chapter_id=payload["chapter_id"],
            brief=payload["brief"],
            target_words=payload["target_words"],
            tasks=tasks,
        )
        self.runs[run_id] = run
        return run

    def execute_all(self, run_id: str, max_rounds: int = 2) -> Run:
        run = self.get_run(run_id)
        run.status = "RUNNING"

        for _ in range(max_rounds):
            pending = [task for task in run.tasks if task.status != "DONE"]
            if not pending:
                run.status = "PASS"
                return run

            for task in pending:
                self._execute_task(run, task)

            rewrite_targets = [
                task for task in run.tasks if task.status == "REWRITE_REQUIRED" and task.attempts < max_rounds
            ]
            if not rewrite_targets:
                break

            for task in rewrite_targets:
                task.status = "PENDING"

        failed = [task for task in run.tasks if task.status != "DONE"]
        run.status = "REWRITE" if failed else "PASS"
        return run

    def _execute_task(self, run: Run, task: AgentTask) -> None:
        task.attempts += 1
        simulated_summary = (
            f"{task.agent_id} completed for {run.chapter_id}. "
            f"Role core: {'/'.join(task.packet.get('role_core', []))}"
        )
        result_payload = {
            "summary": simulated_summary,
        }
        ok, reason = validate_role_output(task.agent_id, result_payload, task.packet)

        result = TaskResult(
            agent_id=task.agent_id,
            summary=simulated_summary,
            received_events=len(task.packet.get("recent_events", [])),
            received_facts=len(task.packet.get("known_facts", [])),
            role_core_check={"ok": ok, "reason": reason},
            attempt=task.attempts,
        )

        task.result = result
        task.status = "DONE" if ok else "REWRITE_REQUIRED"
        run.events.append(
            {
                "task_id": task.task_id,
                "agent_id": task.agent_id,
                "status": task.status,
                "attempt": task.attempts,
                "reason": reason,
            }
        )

    def get_run(self, run_id: str) -> Run:
        if run_id not in self.runs:
            raise KeyError(f"run not found: {run_id}")
        return self.runs[run_id]

    @staticmethod
    def _default_state() -> dict[str, Any]:
        return {
            "events": [
                {"id": "e1", "text": "主角在黑市听到流言", "visible_to": ["protagonist", "director"]},
                {"id": "e2", "text": "皇城密令已下发", "visible_to": ["director", "world_guardian"]},
                {"id": "e3", "text": "配角误判敌方意图", "visible_to": ["supporting_cast", "director"]},
            ],
            "facts": [
                {"id": "f1", "text": "主角尚未知晓皇城密令", "known_by": ["director", "world_guardian"]},
                {"id": "f2", "text": "配角与黑市组织有旧交", "known_by": ["supporting_cast", "director"]},
                {"id": "f3", "text": "本章核心冲突是信息差", "known_by": ["*"]},
            ],
            "role_core": {
                "director": ["冲突", "节奏"],
                "protagonist": ["成长", "抉择"],
                "supporting_cast": ["误判", "张力"],
            },
        }


runtime_kernel = ClaudeCodeLikeRuntime()
