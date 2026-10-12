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


def test_continue_as_new_bound() -> None:
    bridge = TemporalPatternBridge()
    out = bridge.start_or_resume(
        "pat_can_1",
        _tiny_def(),
        {"goal_id": "g"},
        continue_as_new_after=2,
    )
    assert out.get("continued_as_new") is True
    assert out["steps_completed_before_can"] == 2
    assert out["remaining_steps"] == ["c"]
