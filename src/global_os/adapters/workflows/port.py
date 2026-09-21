"""Workflow runner port — Temporal is one future adapter (ADR-0002). Domain never imports Temporal types."""

from __future__ import annotations

import asyncio
import os
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
    """Temporal-backed runner. Fails closed without address/server; never falls back to LocalDurable."""

    backend = "temporal"

    def __init__(self, address: str | None = None, *, connect_timeout_s: float = 2.0) -> None:
        self._address = address if address is not None else os.environ.get("TEMPORAL_ADDRESS", "")
        self._connect_timeout_s = connect_timeout_s

    def probe_server(self) -> None:
        """Fail closed if Temporal cannot be reached. Does not start workflows."""
        if not self._address:
            raise TemporalAdapterUnavailable(
                "TEMPORAL_ADDRESS unset; LocalDurableAdapter ≠ Temporal (ADR-0002)"
            )
        try:
            from temporalio.client import Client
        except ImportError as exc:
            raise TemporalAdapterUnavailable(
                "temporalio not installed; refusing silent LocalDurable fallback"
            ) from exc

        async def _connect() -> None:
            await asyncio.wait_for(
                Client.connect(self._address),
                timeout=self._connect_timeout_s,
            )

        try:
            asyncio.run(_connect())
        except Exception as exc:
            raise TemporalAdapterUnavailable(
                f"Temporal unreachable ({exc}); refusing silent LocalDurable fallback"
            ) from exc

    def start_or_resume(
        self,
        run_id: str,
        definition: WorkflowDefinition,
        initial_state: dict[str, Any],
        *,
        kill_after_step: str | None = None,
    ) -> dict[str, Any]:
        # Probe first — still CONTRACTED for full workflow bridge / kill acceptance
        self.probe_server()
        raise TemporalAdapterUnavailable(
            "Temporal workflow bridge not RUNTIME_VERIFIED yet; "
            "refusing silent LocalDurable fallback (ADR-0002)"
        )
