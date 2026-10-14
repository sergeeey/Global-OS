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
    assert delivery["honesty"]["tool_selection"] == (
        "brief_catalog_gateway_observation_conditioned"
    )
    assert "repo.audit" in (delivery.get("executed_tools") or [])
    assert "repo.audit" in (delivery.get("allowed_tool_ids") or [])
    assert int(delivery.get("model_cycles") or 0) >= 2
    assert delivery["limits"]["live_llm"] in {
        "NOT_USED_MOCK_OR_REACTIVE",
        "AUTHORIZED_GROQ_FREE_TIER",
    }

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
    # DENY must not invoke producer (execution boundary).
    calls_path = gos / "missions" / delivery["run_id"] / "tool_calls.json"
    assert not calls_path.exists() or json.loads(calls_path.read_text()) == {}
    assert delivery.get("observe_block") == "authority_capability_denied"


def test_deny_path_never_produces_tool_artifact(tmp_path: Path) -> None:
    """Regression: Authority DENY → produce_tool_artifact not called."""
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal("goal_deny_no_produce"),
        target_path=target,
        gos_root=gos,
        hooks={"deny_capability": True},
    )
    run_dir = gos / "missions" / delivery["run_id"]
    assert not (run_dir / "last_tool_report.json").exists()
    assert not (run_dir / "tool_calls.json").exists()
    assert delivery["evidence"]["effect_receipts"] == []


def test_allow_path_produces_exactly_once_and_coherent_evidence(tmp_path: Path) -> None:
    """ALLOW → producer once; artifact hash, verifier, receipt share one result."""
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal("goal_allow_once"),
        target_path=target,
        gos_root=gos,
    )
    assert delivery["terminal_status"] == "SUCCEEDED"
    assert delivery["tool_calls"].get("repo.audit") == 1
    receipts = delivery["evidence"]["effect_receipts"]
    assert len(receipts) == 1
    rec = receipts[0]
    assert rec["report_hash"] == delivery["report_hash"]
    assert rec["artifact_digest"] == delivery["artifact_digest"]
    assert rec["artifact_verify"]["ok"] is True
    assert rec["gateway_reconciliation_status"] == "OBSERVATION_PENDING"
    assert rec["reconciliation_status"] == "RECONCILED"
    assert rec["verification_method"] == "post_execution_artifact_verify"
    assert rec["world_success"] is True
    # Persisted Gateway produce must match delivery hash.
    saved = json.loads(
        (gos / "missions" / delivery["run_id"] / "last_tool_report.json").read_text()
    )
    assert saved["report_hash"] == delivery["report_hash"]
    assert saved["tool_id"] == "repo.audit"


def test_negative_nonempty_args_rejected(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    target = Path(__file__).resolve().parents[1]
    delivery = start_mission(
        _goal("goal_bad_args"),
        target_path=target,
        gos_root=gos,
        hooks={
            "model_script": [
                {
                    "action": "call_tool",
                    "tool_id": "repo.audit",
                    "args": {"path": "/etc/passwd"},
                },
                {"action": "stop"},
            ]
        },
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert str(delivery.get("observe_block") or "").startswith("invalid_tool_args")
    calls_path = gos / "missions" / delivery["run_id"] / "tool_calls.json"
    assert not calls_path.exists()


def test_tool_catalog_capability_intersection() -> None:
    assert "repo.audit" in registered_tool_ids()
    assert "repo.inventory" in registered_tool_ids()
    allowed = resolve_allowed_tool_ids(
        goal_capabilities=["filesystem.read", "git.read"],
        brief_allowed_capabilities=["filesystem.read"],
    )
    assert "repo.audit" in allowed
    assert "repo.inventory" in allowed
    assert "workspace.read_text" in allowed
    assert "research.scan" in allowed
    assert "workspace.write_text" not in allowed
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


def test_observation_reactive_changes_next_action(tmp_path: Path) -> None:
    """Next decision depends on observation — multi-step preferred tools."""
    gos = tmp_path / ".gos"
    sandbox = tmp_path / "se_box"
    sandbox.mkdir()
    (sandbox / "README.md").write_text("# se box\nbuggy=1\n", encoding="utf-8")
    (sandbox / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    draft = {
        "schema_version": "0.1.0",
        "goal_id": "goal_reactive_multi",
        "version": 1,
        "tenant_id": "tenant_local",
        "workspace_id": "ws_preprod",
        "objective": {"text": "Inventory, inspect README, then write a fix marker."},
        "success_criteria": [
            {"id": "sc_inv", "description": "workspace inventory with file listing"},
            {"id": "sc_read", "description": "read workspace file README"},
            {"id": "sc_write", "description": "apply fix by write file in workspace"},
        ],
        "invariants": ["sandbox_target_only"],
        "non_goals": [],
        "forbidden_outcomes": [],
        "risk": {"tolerance": "low", "maximum_irreversibility": "none"},
        "authority": {
            "delegation_depth_max": 3,
            "capabilities": ["filesystem.read", "filesystem.write"],
        },
        "evidence_requirements": {"major_finding": {"verification_tier": 2}},
        "termination": ["success_criteria_met"],
        "created_at": "2026-10-14T00:00:00+00:00",
    }
    delivery = start_mission(
        draft,
        target_path=sandbox,
        gos_root=gos,
        hooks={"force_model_mode": "reactive", "max_model_cycles": 8},
        budget_usd=5.0,
    )
    assert delivery["terminal_status"] == "SUCCEEDED"
    assert delivery["model_mode"] == "reactive"
    assert "repo.inventory" in delivery["executed_tools"]
    assert "workspace.read_text" in delivery["executed_tools"]
    assert "workspace.write_text" in delivery["executed_tools"]
    assert int(delivery["model_cycles"]) >= 4  # 3 tools + stop
    hist = delivery["evidence"]["model_history"]
    assert len(hist) >= 3
    # After first ok observation, later steps must not all be identical.
    actions = [h.get("step", {}).get("tool_id") for h in hist if h.get("step", {}).get("action") == "call_tool"]
    assert len(set(actions)) >= 2
    assert (sandbox / "FIX_APPLIED.txt").exists()


def test_research_scan_goal(tmp_path: Path) -> None:
    gos = tmp_path / ".gos"
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "paper.md").write_text(
        "# Notes\nSee [Source](https://example.com/a) and doi:10.1234/abcd.5678\n"
        "- Hypothesis A is stronger than B under noise.\n",
        encoding="utf-8",
    )
    draft = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "examples"
            / "goal_research_scan.json"
        ).read_text(encoding="utf-8")
    )
    delivery = start_mission(draft, target_path=corpus, gos_root=gos, budget_usd=3.0)
    assert delivery["terminal_status"] == "SUCCEEDED"
    assert delivery["executed_tools"] == ["research.scan"]
