"""Durable workflow runner — Temporal-shaped, domain-owned (no Temporal types)."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, cast


class WorkflowAborted(Exception):
    """Injected failure (e.g. process kill simulation)."""


class CorruptedCheckpointError(Exception):
    """Checkpoint bytes are unusable — fail closed; never invent state (GOS-I29)."""


@dataclass
class WorkflowStep:
    name: str
    fn: Callable[[dict[str, Any]], dict[str, Any]]


@dataclass
class WorkflowDefinition:
    name: str
    steps: list[WorkflowStep] = field(default_factory=list)


class DurableRunner:
    """Checkpoint after each step; resume skips completed steps (GOS-I15)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def start_or_resume(
        self,
        run_id: str,
        definition: WorkflowDefinition,
        initial_state: dict[str, Any],
        *,
        kill_after_step: str | None = None,
    ) -> dict[str, Any]:
        state = deepcopy(initial_state)
        start_index = self._completed_count(run_id)
        for index, step in enumerate(definition.steps):
            if index < start_index:
                # restore latest checkpoint state
                state = self._load_state(run_id, index)
                continue
            state = step.fn(deepcopy(state))
            self._checkpoint(run_id, index, step.name, state, status="COMPLETED")
            if kill_after_step is not None and step.name == kill_after_step:
                self._checkpoint(run_id, index, step.name, state, status="KILLED")
                raise WorkflowAborted(f"simulated kill after {step.name}")
        self._checkpoint(
            run_id,
            len(definition.steps) - 1,
            definition.steps[-1].name if definition.steps else "done",
            state,
            status="SUCCEEDED",
        )
        return state

    def _completed_count(self, run_id: str) -> int:
        rows = self._conn.execute(
            """
            SELECT step_index, status FROM workflow_checkpoints
            WHERE run_id = ? AND status = 'COMPLETED'
            ORDER BY step_index
            """,
            (run_id,),
        ).fetchall()
        return len(rows)

    def _load_state(self, run_id: str, step_index: int) -> dict[str, Any]:
        row = self._conn.execute(
            """
            SELECT state_json FROM workflow_checkpoints
            WHERE run_id = ? AND step_index = ? AND status = 'COMPLETED'
            """,
            (run_id, step_index),
        ).fetchone()
        if row is None:
            return {}
        try:
            raw = json.loads(row["state_json"])
        except json.JSONDecodeError as exc:
            raise CorruptedCheckpointError(
                f"corrupted checkpoint run_id={run_id} step={step_index}: invalid JSON"
            ) from exc
        if not isinstance(raw, dict):
            raise CorruptedCheckpointError(
                f"corrupted checkpoint run_id={run_id} step={step_index}: state must be object"
            )
        return cast(dict[str, Any], raw)

    def _checkpoint(
        self,
        run_id: str,
        step_index: int,
        step_name: str,
        state: dict[str, Any],
        *,
        status: str,
    ) -> None:
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            INSERT INTO workflow_checkpoints (run_id, step_index, step_name, state_json, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id, step_index) DO UPDATE SET
                step_name=excluded.step_name,
                state_json=excluded.state_json,
                status=excluded.status,
                updated_at=excluded.updated_at
            """,
            (run_id, step_index, step_name, json.dumps(state), status, now),
        )
        self._conn.commit()


def goal_execution_workflow() -> WorkflowDefinition:
    """Domain Goal workflow: plan → organize → execute tasks → report."""

    def plan(state: dict[str, Any]) -> dict[str, Any]:
        state["phase"] = "planned"
        state["tasks"] = state.get("tasks") or ["architecture", "verification", "report"]
        return state

    def organize(state: dict[str, Any]) -> dict[str, Any]:
        state["phase"] = "organized"
        state["org"] = "manager_workers"
        return state

    def execute_tasks(state: dict[str, Any]) -> dict[str, Any]:
        state["phase"] = "executing"
        done = list(state.get("completed_tasks", []))
        for task in state.get("tasks", []):
            if task not in done:
                done.append(task)
                state["completed_tasks"] = done
                state["last_task"] = task
        state["phase"] = "executed"
        return state

    def report(state: dict[str, Any]) -> dict[str, Any]:
        state["phase"] = "reported"
        state["report"] = {
            "tasks_done": state.get("completed_tasks", []),
            "org": state.get("org"),
        }
        return state

    return WorkflowDefinition(
        name="goal_execution",
        steps=[
            WorkflowStep("plan", plan),
            WorkflowStep("organize", organize),
            WorkflowStep("execute_tasks", execute_tasks),
            WorkflowStep("report", report),
        ],
    )
