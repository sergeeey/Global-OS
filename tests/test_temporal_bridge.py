from __future__ import annotations

import asyncio

import pytest

from global_os.adapters.workflows.temporal_bridge import (
    TemporalBridge,
    side_effects,
)
from global_os.runtime.workflows.durable import (
    WorkflowDefinition,
    WorkflowStep,
    goal_execution_workflow,
)

pytest.importorskip("temporalio")


def test_temporal_bridge_completes_goal_workflow():
    bridge = TemporalBridge()
    result = bridge.start_or_resume(
        "temporal_ok_1",
        goal_execution_workflow(),
        {"goal_id": "goal_t"},
    )
    assert result["phase"] == "reported"
    effects = side_effects()
    assert effects == [
        "effect:plan",
        "effect:organize",
        "effect:execute_tasks",
        "effect:report",
    ]


def test_temporal_bridge_kill_retry_no_duplicate_effects():
    """Simulated activity failure + Temporal retry must not double material effects."""
    bridge = TemporalBridge()
    result = bridge.start_or_resume(
        "temporal_kill_retry_1",
        goal_execution_workflow(),
        {"goal_id": "goal_t"},
        kill_after_step="organize",
    )
    assert result["phase"] == "reported"
    effects = side_effects()
    assert effects.count("effect:organize") == 1
    assert effects == [
        "effect:plan",
        "effect:organize",
        "effect:execute_tasks",
        "effect:report",
    ]


def test_temporal_bridge_is_not_local_durable():
    assert TemporalBridge().backend == "temporal"
    definition = WorkflowDefinition(
        name="tiny",
        steps=[WorkflowStep("only", lambda s: {**s, "ok": True})],
    )
    out = TemporalBridge().start_or_resume("temporal_tiny", definition, {})
    assert out["ok"] is True


def test_temporal_otel_workflow_activity_spans():
    from global_os.observability import clear_spans, configure_tracing, exported_spans

    configure_tracing()
    clear_spans()
    TemporalBridge().start_or_resume(
        "temporal_otel_1",
        goal_execution_workflow(),
        {"goal_id": "goal_otel"},
    )
    kinds = {s.attributes.get("gos.span.kind") for s in exported_spans() if s.attributes}
    assert "Workflow" in kinds
    assert "Activity" in kinds
    activities = [
        s.attributes.get("activity.step")
        for s in exported_spans()
        if s.attributes and s.attributes.get("gos.span.kind") == "Activity"
    ]
    assert "plan" in activities
    assert "report" in activities


def test_temporal_live_worker_restart_no_duplicate_effects():
    """Requires live TEMPORAL_ADDRESS (e.g. temporal server start-dev)."""
    import os
    import uuid

    addr = os.environ.get("TEMPORAL_ADDRESS")
    if not addr:
        pytest.skip("TEMPORAL_ADDRESS not set")
    bridge = TemporalBridge(address=addr)
    run_id = f"temporal_live_restart_{uuid.uuid4().hex[:12]}"
    result = asyncio.run(
        bridge.run_with_worker_restart(
            run_id,
            goal_execution_workflow(),
            {"goal_id": "goal_live"},
            kill_after_step="organize",
            address=addr,
        )
    )
    assert result["phase"] == "reported"
    effects = side_effects()
    assert effects.count("effect:organize") == 1
    assert "effect:report" in effects
