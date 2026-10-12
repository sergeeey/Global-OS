"""Temporal pattern helpers — heartbeats, approval signals, continue-as-new (ADR-0013).

Authority approvals remain in ApprovalService; Temporal only waits on a signal.
Workflow/activity classes are module-level (Temporal requirement).
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from temporalio import activity, workflow
from temporalio.common import RetryPolicy

from global_os.adapters.workflows.port import TemporalAdapterUnavailable
from global_os.runtime.workflows.durable import WorkflowDefinition

_STEP_FNS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}
_HEARTBEATS: list[dict[str, Any]] = []


def reset_pattern_harness() -> None:
    global _STEP_FNS, _HEARTBEATS
    _STEP_FNS = {}
    _HEARTBEATS = []


def register_pattern_steps(definition: WorkflowDefinition) -> None:
    for step in definition.steps:
        _STEP_FNS[step.name] = step.fn


def heartbeats() -> list[dict[str, Any]]:
    return list(_HEARTBEATS)


@activity.defn(name="gos_run_step_heartbeat")
async def run_step_with_heartbeat(step_name: str, state: dict[str, Any]) -> dict[str, Any]:
    """Long-step activity: emit heartbeats then run domain fn."""
    for i in range(3):
        details = {"step": step_name, "progress": i, "goal_id": state.get("goal_id")}
        _HEARTBEATS.append(details)
        activity.heartbeat(details)
        await asyncio.sleep(0.01)
    fn = _STEP_FNS[step_name]
    return fn(dict(state))


@dataclass
class ApprovalSignal:
    approved: bool
    approver: str = "human"
    note: str = ""


@workflow.defn(name="GosGoalExecutionPatterns")
class GosGoalExecutionPatterns:
    def __init__(self) -> None:
        self._approval: ApprovalSignal | None = None

    @workflow.signal
    def human_approval(self, approved: bool, approver: str = "human", note: str = "") -> None:
        self._approval = ApprovalSignal(approved=approved, approver=approver, note=note)

    @workflow.run
    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """payload: state, step_names, approval_gates, continue_as_new_after."""
        state = dict(payload.get("state") or {})
        step_names: list[str] = list(payload.get("step_names") or [])
        gates = set(payload.get("approval_gates") or [])
        can_after = payload.get("continue_as_new_after")

        for completed, name in enumerate(step_names, start=1):
            if name in gates:
                await workflow.wait_condition(lambda: self._approval is not None)
                assert self._approval is not None
                if not self._approval.approved:
                    return {**state, "phase": "rejected", "rejected_step": name}
                state = {
                    **state,
                    "last_approver": self._approval.approver,
                    "approval_note": self._approval.note,
                }
                self._approval = None

            state = await workflow.execute_activity(
                run_step_with_heartbeat,
                args=[name, state],
                start_to_close_timeout=timedelta(seconds=60),
                heartbeat_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=4,
                    initial_interval=timedelta(milliseconds=50),
                ),
            )
            if can_after is not None and completed >= int(can_after):
                rest = step_names[step_names.index(name) + 1 :]
                return {
                    **state,
                    "continued_as_new": True,
                    "steps_completed_before_can": completed,
                    "remaining_steps": rest,
                }
        return state


class TemporalPatternBridge:
    """Runs pattern-enhanced workflows on Temporal time-skipping env."""

    backend = "temporal_patterns"

    def start_or_resume(
        self,
        run_id: str,
        definition: WorkflowDefinition,
        initial_state: dict[str, Any],
        *,
        approval_gates: set[str] | None = None,
        continue_as_new_after: int | None = None,
        auto_approve: bool = True,
    ) -> dict[str, Any]:
        return asyncio.run(
            self.run_definition(
                run_id,
                definition,
                initial_state,
                approval_gates=approval_gates,
                continue_as_new_after=continue_as_new_after,
                auto_approve=auto_approve,
            )
        )

    async def run_definition(
        self,
        run_id: str,
        definition: WorkflowDefinition,
        initial_state: dict[str, Any],
        *,
        approval_gates: set[str] | None = None,
        continue_as_new_after: int | None = None,
        auto_approve: bool = True,
    ) -> dict[str, Any]:
        try:
            from temporalio.client import Client
            from temporalio.testing import WorkflowEnvironment
            from temporalio.worker import Worker
        except ImportError as exc:
            raise TemporalAdapterUnavailable(
                "temporalio not installed; refusing silent LocalDurable fallback"
            ) from exc

        reset_pattern_harness()
        register_pattern_steps(definition)
        step_names = [s.name for s in definition.steps]
        gates = sorted(approval_gates or [])
        payload = {
            "state": {**initial_state, "_gos_run_id": run_id},
            "step_names": step_names,
            "approval_gates": gates,
            "continue_as_new_after": continue_as_new_after,
        }

        async with await WorkflowEnvironment.start_time_skipping() as env:
            client: Client = env.client
            task_queue = f"gos-pat-{run_id}"
            async with Worker(
                client,
                task_queue=task_queue,
                workflows=[GosGoalExecutionPatterns],
                activities=[run_step_with_heartbeat],
            ):
                handle = await client.start_workflow(
                    GosGoalExecutionPatterns.run,
                    payload,
                    id=run_id,
                    task_queue=task_queue,
                    execution_timeout=timedelta(seconds=30),
                )
                if gates and auto_approve:
                    # Signals are buffered; send after start so wait_condition unblocks.
                    # Avoid fire-and-forget tasks under time-skipping (racey).
                    for _ in range(50):
                        desc = await handle.describe()
                        status = str(getattr(desc, "status", "") or "")
                        if "RUNNING" in status or status.endswith("1"):
                            break
                        await asyncio.sleep(0.01)
                    await handle.signal(
                        GosGoalExecutionPatterns.human_approval,
                        args=[True, "harness", "auto"],
                    )
                return await handle.result()