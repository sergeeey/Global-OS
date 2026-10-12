"""P0a: Temporal heartbeats / approval signals / continue-as-new bound (ADR-0013)."""

from __future__ import annotations

import pytest

from global_os.adapters.workflows.temporal_patterns import (
    TemporalPatternBridge,
    heartbeats,
)
from global_os.runtime.workflows.durable import WorkflowDefinition, WorkflowStep

pytest.importorskip("temporalio")


def _tiny_def() -> WorkflowDefinition:
    return WorkflowDefinition(
        name="tiny_pat",
        steps=[
            WorkflowStep("a", lambda s: {**s, "phase": "a"}),
            WorkflowStep("b", lambda s: {**s, "phase": "b"}),
            WorkflowStep("c", lambda s: {**s, "phase": "c"}),
        ],
    )


def test_heartbeats_emitted_during_steps() -> None:
    bridge = TemporalPatternBridge()
    out = bridge.start_or_resume("pat_hb_1", _tiny_def(), {"goal_id": "g"})
    assert out["phase"] == "c"
    hb = heartbeats()
    assert len(hb) >= 3
    assert any(h["step"] == "a" for h in hb)


def test_approval_signal_gate() -> None:
    bridge = TemporalPatternBridge()
    out = bridge.start_or_resume(
        "pat_appr_1",
        _tiny_def(),
        {"goal_id": "g"},
        approval_gates={"b"},
        auto_approve=True,
    )
    assert out["phase"] == "c"
    assert out.get("last_approver") == "harness"


def test_continue_as_new_real_chain() -> None:
    """RUN-004: real workflow.continue_as_new — final result completes remaining steps."""
    bridge = TemporalPatternBridge()
    out = bridge.start_or_resume(
        "pat_can_1",
        _tiny_def(),
        {"goal_id": "g"},
        continue_as_new_after=2,
    )
    assert out["phase"] == "c"
    assert int(out.get("continue_as_new_epochs") or 0) >= 1
    hb = heartbeats("pat_can_1")
    assert any(h["step"] == "c" for h in hb)


def test_approval_gate_after_continue_as_new() -> None:
    """RUN-004b: gated step after CAN must complete under harness auto_approve (no hang)."""
    bridge = TemporalPatternBridge()
    out = bridge.start_or_resume(
        "pat_can_appr_1",
        _tiny_def(),
        {"goal_id": "g"},
        continue_as_new_after=1,
        approval_gates={"b"},
        auto_approve=True,
    )
    assert out["phase"] == "c"
    assert out.get("last_approver") == "harness"
    assert int(out.get("continue_as_new_epochs") or 0) >= 1


def test_harness_registry_isolated_by_run_id() -> None:
    """RUN-005: step/heartbeat registries are keyed by run_id (not a single global bag)."""
    from global_os.adapters.workflows.temporal_patterns import (
        _STEP_FNS,
        register_pattern_steps,
        reset_pattern_harness,
    )

    reset_pattern_harness()
    register_pattern_steps("run_a", _tiny_def())
    register_pattern_steps("run_b", _tiny_def())
    assert "run_a" in _STEP_FNS and "run_b" in _STEP_FNS
    assert set(_STEP_FNS["run_a"]) == {"a", "b", "c"}
    reset_pattern_harness("run_a")
    assert "run_a" not in _STEP_FNS
    assert "run_b" in _STEP_FNS
    reset_pattern_harness()
