"""Independent e2e acceptance: PREPROD_SUPERVISED Goal → Delivery path."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.runtime.preprod import (
    SupervisedMissionError,
    cancel_mission,
    deliver_mission,
    pause_mission,
    resume_mission,
    start_mission,
    status_mission,
)
from global_os.runtime.preprod.supervised_mission import start_mission as start_raw
from global_os.verification.completion_gate import CompletionStatus


def _goal(goal_id: str = "goal_preprod_e2e_001") -> dict:
    return {
        "schema_version": "0.1.0",
        "goal_id": goal_id,
        "version": 1,
        "tenant_id": "tenant_local",
        "workspace_id": "ws_preprod",
        "objective": {
            "text": "Produce a verified read-only engineering audit report for the workspace."
        },
        "success_criteria": [
            {"id": "sc_01", "description": "verified engineering report with evidence"}
        ],
        "invariants": ["read_only_target_repo", "no_binding_external_commitments"],
        "non_goals": ["modify_code", "push_commits"],
        "forbidden_outcomes": ["write_to_target_repo"],
        "risk": {"tolerance": "low", "maximum_irreversibility": "none"},
        "authority": {
            "delegation_depth_max": 3,
            "capabilities": ["filesystem.read", "git.read", "web.read"],
        },
        "evidence_requirements": {"major_finding": {"verification_tier": 2}},
        "termination": ["success_criteria_met", "user_cancelled"],
        "created_at": "2026-10-13T00:00:00+00:00",
    }


def test_supervised_mission_end_to_end_delivery(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal(),
        target_path=target,
        gos_root=gos,
        budget_usd=5.0,
        budget_tokens=1000,
    )
    assert delivery["profile"] == "PREPROD_SUPERVISED"
    assert delivery["terminal_status"] == "SUCCEEDED"
    assert delivery["completion"]["status"] == CompletionStatus.ACHIEVED.value
    assert delivery["artifact_digest"]
    assert delivery["evidence"]["effect_receipt_ids"]
    assert delivery["budget"]["spent_usd"] > 0
    assert delivery["honesty"]["production_proven"] == 0
    assert delivery["limits"]["challenge_ga"] == "NOT_STARTED"

    st = status_mission(gos_root=gos, run_id=delivery["run_id"])
    assert st["status"] == "SUCCEEDED"
    assert st["delivery_available"] is True
    assert deliver_mission(gos_root=gos, run_id=delivery["run_id"])["run_id"] == delivery["run_id"]


def test_crash_resume_does_not_silently_replay_tool(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    interrupted = start_raw(
        _goal("goal_preprod_kill_001"),
        target_path=target,
        gos_root=gos,
        kill_after_step="gateway_observe",
    )
    assert interrupted["status"] in {"PAUSED", "RUNNING"}
    run_id = interrupted["run_id"]
    calls_path = gos / "missions" / run_id / "tool_calls.json"
    assert calls_path.exists()
    assert json.loads(calls_path.read_text())["repo.audit"] == 1

    delivery = resume_mission(gos_root=gos, run_id=run_id)
    assert delivery["terminal_status"] == "SUCCEEDED"
    assert json.loads(calls_path.read_text())["repo.audit"] == 1


def test_pause_cancel_operator_controls(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    start_raw(
        _goal("goal_preprod_pause_001"),
        target_path=target,
        gos_root=gos,
        kill_after_step="gateway_observe",
    )
    paused = pause_mission(gos_root=gos)
    assert paused["status"] == "PAUSED"
    assert paused["human_action_required"] is True
    cancelled = cancel_mission(gos_root=gos, run_id=paused["run_id"])
    assert cancelled["status"] == "CANCELLED"
    with pytest.raises(SupervisedMissionError):
        resume_mission(gos_root=gos, run_id=paused["run_id"])


def test_cli_mission_start_status(tmp_path: Path) -> None:
    from global_os.cli import main

    gos = tmp_path / ".gos"
    goal_path = tmp_path / "goal.json"
    goal_path.write_text(json.dumps(_goal("goal_cli_001")), encoding="utf-8")
    target = Path(__file__).resolve().parents[1]
    rc = main(
        [
            "--root",
            str(gos),
            "mission",
            "start",
            "--goal",
            str(goal_path),
            "--target",
            str(target),
            "--budget-usd",
            "3",
        ]
    )
    assert rc == 0
    rc2 = main(["--root", str(gos), "mission", "status"])
    assert rc2 == 0


def test_mid_progress_without_receipts_is_not_success(tmp_path: Path) -> None:
    """Completion Gate honesty: empty receipts must not yield ACHIEVED."""
    from global_os.verification.completion_gate import evaluate_goal_completion

    decision = evaluate_goal_completion(goal=_goal(), effect_receipts=[])
    assert decision.status != CompletionStatus.ACHIEVED
