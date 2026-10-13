"""Contrastive Failure Miner — analyze only."""

from __future__ import annotations

import pytest

from global_os.evals.mission_learning.contrastive import mine_contrastive_failures


def test_requires_two_trajectories() -> None:
    with pytest.raises(ValueError):
        mine_contrastive_failures([{"terminal": "SUCCESS"}])


def test_mines_wrong_tool_and_premature_stop() -> None:
    trajectories = [
        {
            "goal_id": "g1",
            "terminal": "SUCCESS",
            "steps": [{"tool": "read_file"}, {"tool": "write_file"}],
        },
        {
            "goal_id": "g1",
            "terminal": "FAILED",
            "steps": [{"tool": "bash_wildcard"}],
            "stop_reason": "gave_up",
            "premature_stop": True,
        },
        {
            "goal_id": "g1",
            "terminal": "FAILED",
            "steps": [{"tool": "bash_wildcard"}],
            "context_loss": True,
            "dropped_requirement": "acceptance_tests",
        },
    ]
    out = mine_contrastive_failures(trajectories, goal_id="g1")
    assert out["mutates_runtime"] is False
    assert out["n_success"] == 1
    assert out["n_failure"] == 2
    classes = {f["failure_class"] for f in out["findings"]}
    assert "wrong_tool_selection" in classes
    assert "premature_stop" in classes
    assert "context_loss" in classes
    assert all(p["mutates_runtime"] is False for p in out["proposals"])


def test_no_findings_without_contrast() -> None:
    out = mine_contrastive_failures(
        [
            {"terminal": "FAILED", "steps": []},
            {"terminal": "FAILED", "steps": []},
        ]
    )
    assert out["findings"] == []
    assert out["reason"] == "need_both_success_and_failure_trajectories"
