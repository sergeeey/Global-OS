"""Temporal workflow bridge — domain steps as activities (ADR-0002).

Requires temporalio. Never silently falls back to LocalDurableAdapter.
Workflow/activity classes are module-level (Temporal forbids local classes).
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from temporalio import activity, workflow
from temporalio.common import RetryPolicy

from global_os.adapters.workflows.port import TemporalAdapterUnavailable
from global_os.runtime.workflows.durable import WorkflowDefinition


@dataclass
class SideEffectLedger:
    """Records material effects for duplicate detection across retries/restarts."""

    effects: list[str] = field(default_factory=list)

    def record_once(self, name: str) -> bool:
        if name in self.effects:
            return False
        self.effects.append(name)
        return True


_STEP_FNS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}
_SIDE_EFFECTS: SideEffectLedger = SideEffectLedger()
_KILL_AFTER: str | None = None
_KILLED: bool = False


def reset_temporal_harness() -> None:
    global _STEP_FNS, _SIDE_EFFECTS, _KILL_AFTER, _KILLED
    _STEP_FNS = {}
    _SIDE_EFFECTS = SideEffectLedger()
    _KILL_AFTER = None
    _KILLED = False


def register_steps(definition: WorkflowDefinition) -> None:
    for step in definition.steps:
        _STEP_FNS[step.name] = step.fn


def configure_kill_after(step_name: str | None) -> None:
    global _KILL_AFTER, _KILLED
    _KILL_AFTER = step_name
    _KILLED = False


def side_effects() -> list[str]:
    return list(_SIDE_EFFECTS.effects)


@activity.defn(name="gos_run_step")
async def run_step_activity(step_name: str, state: dict[str, Any]) -> dict[str, Any]:
    global _KILLED
    from global_os.observability import activity_span

    goal_id = str(state.get("goal_id", ""))
    run_id = str(state.get("_gos_run_id", ""))
    with activity_span(goal_id=goal_id, run_id=run_id, step_name=step_name):
        _SIDE_EFFECTS.record_once(f"effect:{step_name}")
        if _KILL_AFTER is not None and step_name == _KILL_AFTER and not _KILLED:
            _KILLED = True
            raise RuntimeError(f"simulated worker kill after {step_name}")
        fn = _STEP_FNS[step_name]
        return fn(dict(state))


@workflow.defn(name="GosGoalExecution")
class GosGoalExecution:
    @workflow.run
    async def run(self, initial_state: dict[str, Any], step_names: list[str]) -> dict[str, Any]:
        state = dict(initial_state)
        for name in step_names:
            state = await workflow.execute_activity(
                run_step_activity,
                args=[name, state],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=8,
                    initial_interval=timedelta(milliseconds=50),
                ),
            )
        return state


class TemporalBridge:
    """Runs a WorkflowDefinition on Temporal (time-skipping env or TEMPORAL_ADDRESS)."""

    backend = "temporal"

    def __init__(self, address: str | None = None) -> None:
        self._address = address if address is not None else os.environ.get("TEMPORAL_ADDRESS", "")

    async def run_definition(
        self,
        run_id: str,
        definition: WorkflowDefinition,
        initial_state: dict[str, Any],
        *,
        kill_after_step: str | None = None,
        use_time_skipping: bool = True,
    ) -> dict[str, Any]:
        try:
            from temporalio.client import Client
            from temporalio.testing import WorkflowEnvironment
            from temporalio.worker import Worker
        except ImportError as exc:
            raise TemporalAdapterUnavailable(
                "temporalio not installed; refusing silent LocalDurable fallback"
            ) from exc

        reset_temporal_harness()
        register_steps(definition)
        configure_kill_after(kill_after_step)
        step_names = [s.name for s in definition.steps]
        goal_id = str(initial_state.get("goal_id", ""))
        state_with_run = {**initial_state, "_gos_run_id": run_id}

        async def _execute(client: Client) -> dict[str, Any]:
            from global_os.observability import configure_tracing, workflow_span

            configure_tracing()
            task_queue = f"gos-{run_id}"
            with workflow_span(
                goal_id=goal_id, run_id=run_id, workflow_name=definition.name
            ):
                async with Worker(
                    client,
                    task_queue=task_queue,
                    workflows=[GosGoalExecution],
                    activities=[run_step_activity],
                ):
                    return await client.execute_workflow(
                        GosGoalExecution.run,
                        args=[state_with_run, step_names],
                        id=run_id,
                        task_queue=task_queue,
                    )

        if use_time_skipping or not self._address:
            async with await WorkflowEnvironment.start_time_skipping() as env:
                return await _execute(env.client)

        client = await Client.connect(self._address)
        return await _execute(client)

    async def run_with_worker_restart(
        self,
        run_id: str,
        definition: WorkflowDefinition,
        initial_state: dict[str, Any],
        *,
        kill_after_step: str,
        address: str | None = None,
    ) -> dict[str, Any]:
        """Live Temporal: start workflow, drop worker after kill step, resume with new worker."""
        try:
            from temporalio.client import Client
            from temporalio.worker import Worker
        except ImportError as exc:
            raise TemporalAdapterUnavailable(
                "temporalio not installed; refusing silent LocalDurable fallback"
            ) from exc

        target = address if address is not None else self._address
        if not target:
            raise TemporalAdapterUnavailable(
                "TEMPORAL_ADDRESS unset for multi-worker restart; "
                "refusing silent LocalDurable fallback"
            )

        reset_temporal_harness()
        register_steps(definition)
        configure_kill_after(kill_after_step)
        step_names = [s.name for s in definition.steps]
        goal_id = str(initial_state.get("goal_id", ""))
        state_with_run = {**initial_state, "_gos_run_id": run_id}
        task_queue = f"gos-live-restart-{run_id}"

        client = await Client.connect(target)
        handle = None
        worker1 = Worker(
            client,
            task_queue=task_queue,
            workflows=[GosGoalExecution],
            activities=[run_step_activity],
        )
        await worker1.__aenter__()
        try:
            handle = await client.start_workflow(
                GosGoalExecution.run,
                args=[state_with_run, step_names],
                id=run_id,
                task_queue=task_queue,
            )
            for _ in range(200):
                if _KILLED:
                    break
                await asyncio.sleep(0.05)
            if not _KILLED:
                raise TemporalAdapterUnavailable("kill step was not reached before timeout")
        finally:
            await worker1.__aexit__(None, None, None)

        configure_kill_after(None)
        async with Worker(
            client,
            task_queue=task_queue,
            workflows=[GosGoalExecution],
            activities=[run_step_activity],
        ):
            assert handle is not None
            return await handle.result()

    def start_or_resume(
        self,
        run_id: str,
        definition: WorkflowDefinition,
        initial_state: dict[str, Any],
        *,
        kill_after_step: str | None = None,
    ) -> dict[str, Any]:
        return asyncio.run(
            self.run_definition(
                run_id,
                definition,
                initial_state,
                kill_after_step=kill_after_step,
                use_time_skipping=True,
            )
        )
