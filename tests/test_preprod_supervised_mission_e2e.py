"""Independent e2e acceptance: PREPROD_SUPERVISED Goal → Delivery path."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.runtime.preprod import (
    SupervisedMissionError,
    cancel_mission,
    criteria_supported_by_repo_audit,
    deliver_mission,
    pause_mission,
    registered_tool_ids,
    resolve_allowed_tool_ids,
    resume_mission,
    start_mission,
    status_mission,
    verify_repo_audit_report,
)
from global_os.runtime.preprod.supervised_mission import start_mission as start_raw
from global_os.runtime.preprod.tool_catalog import (
    ToolCatalogError,
    assert_tool_permitted,
    criteria_supported_by_tool,
    verify_tool_artifact,
)
from global_os.verification.completion_gate import CompletionStatus, evaluate_goal_completion
from global_os.world.tools.repo_inventory import verify_repo_inventory_report


def _goal(
    goal_id: str = "goal_preprod_e2e_001",
    *,
    extra_criteria: list[dict[str, str]] | None = None,
) -> dict:
    criteria = [
        {"id": "sc_01", "description": "verified engineering report with evidence"}
    ]
    if extra_criteria:
        criteria.extend(extra_criteria)
    return {
        "schema_version": "0.1.0",
        "goal_id": goal_id,
        "version": 1,
        "tenant_id": "tenant_local",
        "workspace_id": "ws_preprod",
        "objective": {
            "text": "Produce a verified read-only engineering audit report for the workspace."
        },
        "success_criteria": criteria,
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


def _inventory_goal(goal_id: str = "goal_inventory_e2e_001") -> dict:
    path = Path(__file__).resolve().parents[1] / "examples" / "goal_repo_inventory.json"
    draft = json.loads(path.read_text(encoding="utf-8"))
    draft["goal_id"] = goal_id
    return draft


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
    assert delivery["honesty"]["tool_selection"] == "brief_catalog_gateway_not_hardcoded"
    assert "repo.audit" in (delivery.get("executed_tools") or [])
    assert "repo.audit" in (delivery.get("allowed_tool_ids") or [])
    assert int(delivery.get("model_cycles") or 0) >= 2
    assert delivery["limits"]["live_llm"] == "NOT_USED_MOCK_SCRIPTED_ONLY"

    st = status_mission(gos_root=gos, run_id=delivery["run_id"])
    assert st["status"] == "SUCCEEDED"
    assert st["delivery_available"] is True
    assert deliver_mission(gos_root=gos, run_id=delivery["run_id"])["run_id"] == delivery["run_id"]


def test_inventory_goal_same_operator_path(tmp_path: Path) -> None:
    """Second Goal Contract: repo.inventory via identical Operator workflow."""
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _inventory_goal(),
        target_path=target,
        gos_root=gos,
        budget_usd=5.0,
        budget_tokens=1000,
    )
    assert delivery["terminal_status"] == "SUCCEEDED"
    assert delivery["completion"]["status"] == CompletionStatus.ACHIEVED.value
    assert delivery["executed_tools"] == ["repo.inventory"]
    assert "repo.inventory" in delivery["allowed_tool_ids"]
    assert "repo.audit" not in delivery["executed_tools"]
    assert int(delivery["model_cycles"]) >= 2
    assert delivery["tool_calls"].get("repo.inventory") == 1
    assert "sc_inv_01" in delivery["completion"]["criteria_met"]


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


def test_mid_progress_without_receipts_is_not_success() -> None:
    decision = evaluate_goal_completion(goal=_goal(), effect_receipts=[])
    assert decision.status != CompletionStatus.ACHIEVED


def test_nonempty_receipt_without_world_success_is_not_achieved() -> None:
    """P0 regression: presence of a receipt must not blanket criterion_checks=True."""
    goal = _goal("goal_false_receipt")
    receipt = {
        "receipt_id": "er_bad",
        "binds_criteria": ["sc_01"],
        "reconciliation_status": "DISCREPANCY",
        "world_success": False,
        "intended_effect": "repo_audit_report",
        "observed_effect": "repo_audit_failed",
        "tool_response": {"success": True},
    }
    decision = evaluate_goal_completion(goal=goal, effect_receipts=[receipt])
    assert decision.status != CompletionStatus.ACHIEVED
    assert "sc_01" in decision.criteria_unmet or decision.status in {
        CompletionStatus.FAILED,
        CompletionStatus.PARTIAL,
        CompletionStatus.UNKNOWN,
    }


def test_negative_inject_tool_failure_not_succeeded(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal("goal_tool_fail"),
        target_path=target,
        gos_root=gos,
        hooks={"inject_tool_failure": True},
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert delivery["completion"]["status"] != CompletionStatus.ACHIEVED.value


def test_negative_discrepancy_observation_not_succeeded(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal("goal_disc"),
        target_path=target,
        gos_root=gos,
        hooks={"inject_discrepancy_observation": True},
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert delivery["completion"]["status"] != CompletionStatus.ACHIEVED.value


def test_negative_corrupt_artifact_not_succeeded(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal("goal_corrupt"),
        target_path=target,
        gos_root=gos,
        hooks={"inject_corrupt_report": True},
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert verify_repo_audit_report({"findings": [], "modified_target": True})["ok"] is False


def test_negative_empty_artifact_not_succeeded(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal("goal_empty"),
        target_path=target,
        gos_root=gos,
        hooks={"inject_empty_report": True},
    )
    assert delivery["terminal_status"] != "SUCCEEDED"


def test_negative_partial_criteria_not_full_success(tmp_path: Path) -> None:
    """Unrelated criterion stays UNKNOWN — no binds_criteria_override required."""
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal(
            "goal_partial",
            extra_criteria=[
                {"id": "sc_02", "description": "second unmet criterion unrelated to audit"}
            ],
        ),
        target_path=target,
        gos_root=gos,
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert delivery["completion"]["status"] == CompletionStatus.PARTIAL.value
    assert "sc_02" in delivery["completion"]["criteria_unknown"]


def test_repo_audit_verifier_does_not_claim_all_goal_criteria() -> None:
    goal = _goal(
        "goal_support_set",
        extra_criteria=[
            {"id": "sc_integration_tests", "description": "интеграционные тесты прошли"}
        ],
    )
    supported = criteria_supported_by_repo_audit(goal)
    assert supported == ["sc_01"]
    assert "sc_integration_tests" not in supported


def test_sc_01_id_does_not_bypass_semantic_mismatch() -> None:
    """P0: id sc_01 with integration-test semantics must not be repo.audit-supported."""
    goal = _goal("goal_sc01_semantic_trap")
    goal["success_criteria"] = [
        {
            "id": "sc_01",
            "description": "интеграционные тесты прошли",
        }
    ]
    assert criteria_supported_by_repo_audit(goal) == []


def test_successful_audit_does_not_meet_sc01_integration_semantics(
    tmp_path: Path,
) -> None:
    """Successful audit must not ACHIEVE when sc_01 means integration tests."""
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    draft = _goal("goal_sc01_means_tests")
    draft["success_criteria"] = [
        {"id": "sc_01", "description": "интеграционные тесты прошли"}
    ]
    delivery = start_mission(draft, target_path=target, gos_root=gos)
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert delivery["completion"]["status"] != CompletionStatus.ACHIEVED.value
    assert "sc_01" in delivery["completion"]["criteria_unknown"]


def test_successful_audit_does_not_satisfy_unrelated_criterion(tmp_path: Path) -> None:
    """P0: one repo.audit receipt must not bind every Goal criterion by default."""
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal(
            "goal_unrelated_criterion",
            extra_criteria=[
                {
                    "id": "sc_integration_tests",
                    "description": "интеграционные тесты прошли",
                }
            ],
        ),
        target_path=target,
        gos_root=gos,
        # Explicitly no binds_criteria_override — default binding must stay narrow.
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert delivery["completion"]["status"] != CompletionStatus.ACHIEVED.value
    assert "sc_integration_tests" in delivery["completion"]["criteria_unknown"]
    assert "sc_01" in delivery["completion"]["criteria_met"]


def test_negative_insufficient_budget_not_succeeded(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal("goal_budget"),
        target_path=target,
        gos_root=gos,
        budget_usd=0.0,
        hooks={"tool_cost_usd": 0.01},
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert delivery["completion"]["status"] != CompletionStatus.ACHIEVED.value


def test_negative_forbidden_tool_fail_closed(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal("goal_forbidden_tool"),
        target_path=target,
        gos_root=gos,
        hooks={"inject_forbidden_tool_id": "shell.exec"},
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert delivery["completion"]["status"] != CompletionStatus.ACHIEVED.value
    assert not delivery.get("executed_tools")


def test_negative_unknown_tool_catalog_fail_closed() -> None:
    with pytest.raises(ToolCatalogError, match="unknown_tool_id"):
        assert_tool_permitted("shell.exec", allowed_tool_ids=["repo.audit"])
    with pytest.raises(ToolCatalogError, match="forbidden_tool_id"):
        assert_tool_permitted("repo.inventory", allowed_tool_ids=["repo.audit"])


def test_negative_deny_capability_not_succeeded(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal("goal_deny_cap"),
        target_path=target,
        gos_root=gos,
        hooks={"deny_capability": True},
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert delivery["completion"]["status"] != CompletionStatus.ACHIEVED.value


def test_tool_catalog_capability_intersection() -> None:
    assert "repo.audit" in registered_tool_ids()
    assert "repo.inventory" in registered_tool_ids()
    allowed = resolve_allowed_tool_ids(
        goal_capabilities=["filesystem.read", "git.read"],
        brief_allowed_capabilities=["filesystem.read"],
    )
    assert allowed == ["repo.audit", "repo.inventory"]
    none = resolve_allowed_tool_ids(
        goal_capabilities=["web.read"],
        brief_allowed_capabilities=["web.read"],
    )
    assert none == []


def test_inventory_criteria_not_bound_by_audit_verifier() -> None:
    goal = _inventory_goal("goal_inv_support")
    assert criteria_supported_by_tool(goal, "repo.inventory") == ["sc_inv_01"]
    assert criteria_supported_by_tool(goal, "repo.audit") == []
    assert criteria_supported_by_repo_audit(goal) == []


def test_inventory_verifier_rejects_corrupt() -> None:
    assert (
        verify_repo_inventory_report(
            {"kind": "repo_inventory", "entries": [], "modified_target": True}
        )["ok"]
        is False
    )
    assert verify_tool_artifact("repo.inventory", {"kind": "nope"})["ok"] is False


def test_completion_gate_independent_of_tool_catalog() -> None:
    """Completion Gate still refuses empty receipts regardless of catalog wiring."""
    decision = evaluate_goal_completion(goal=_inventory_goal(), effect_receipts=[])
    assert decision.status != CompletionStatus.ACHIEVED


def test_mock_model_two_action_cycles(tmp_path: Path) -> None:
    """Recording + ScriptedActionProvider: ≥2 sequential action-selection cycles."""
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal("goal_model_cycles"),
        target_path=target,
        gos_root=gos,
        hooks={
            "model_script": [
                {"action": "call_tool", "tool_id": "repo.audit", "args": {}},
                {"action": "stop"},
            ]
        },
    )
    assert delivery["terminal_status"] == "SUCCEEDED"
    assert int(delivery["model_cycles"]) >= 2
