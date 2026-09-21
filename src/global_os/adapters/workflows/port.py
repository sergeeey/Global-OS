"""Workflow runner port — Temporal is one future adapter (ADR-0002). Domain never imports Temporal types."""

from __future__ import annotations

from typing import Any, Protocol

from global_os.runtime.workflows.durable import DurableRunner, WorkflowDefinition


class WorkflowRunnerPort(Protocol):
    """Stable port for durable execution. Implementations: LocalDurableAdapter, later Temporal."""

    def start_or_resume(
        self,
        run_id: str,
        definition: WorkflowDefinition,
        initial_state: dict[str, Any],
        *,
        kill_after_step: str | None = None,
    ) -> dict[str, Any]: ...


class LocalDurableAdapter:
    """Wraps DurableRunner. This is NOT Temporal fulfillment (capability remains CONTRACTED)."""

    def __init__(self, runner: DurableRunner) -> None:
        self._runner = runner
        self.backend = "local_durable_runner"

    def start_or_resume(
        self,
        run_id: str,
        definition: WorkflowDefinition,
        initial_state: dict[str, Any],
        *,
        kill_after_step: str | None = None,
    ) -> dict[str, Any]:
        return self._runner.start_or_resume(
            run_id,
            definition,
            initial_state,
            kill_after_step=kill_after_step,
        )


class TemporalAdapterUnavailable(Exception):
    """Raised when Temporal SDK/server is not configured — never silent fallback to allow."""


class TemporalWorkflowAdapter:
    """Placeholder adapter. Calling execute without Temporal configured fails closed."""

    backend = "temporal"

    def start_or_resume(
        self,
        run_id: str,
        definition: WorkflowDefinition,
        initial_state: dict[str, Any],
        *,
        kill_after_step: str | None = None,
    ) -> dict[str, Any]:
        raise TemporalAdapterUnavailable(
            "Temporal adapter not configured; LocalDurableAdapter ≠ Temporal (ADR-0002)"
        )
