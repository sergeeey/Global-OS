"""Acceptance + adversarial tests: falsification-before-SUCCESS + substrate health."""

from __future__ import annotations

import json
from pathlib import Path

from global_os.runtime.preprod import start_mission
from global_os.verification.completion_gate import (
    CompletionStatus,
    evaluate_goal_completion,
)
from global_os.verification.falsifiers import (
    FalsificationOutcome,
    falsify_filesystem_criterion,
    run_filesystem_falsifiers,
)
from global_os.verification.substrate_health import (
    SubstrateStatus,
    assess_substrate_health,
)


def _write_goal() -> dict:
    return {
        "schema_version": "0.1.0",
        "goal_id": "goal_falsify_fix_001",
        "version": 1,
        "tenant_id": "tenant_local",
        "workspace_id": "ws_falsify",
        "objective": {"text": "Apply FIX_APPLIED.txt marker"},
        "success_criteria": [
            {
                "id": "sc_inv",
                "description": "workspace inventory with top-level file listing",
            },
            {
                "id": "sc_write",
                "description": "apply fix by write file FIX_APPLIED.txt in workspace",
            },
        ],
        "invariants": ["sandbox_target_only"],
        "non_goals": [],
        "forbidden_outcomes": ["path_escape"],
        "risk": {"tolerance": "low", "maximum_irreversibility": "none"},
        "authority": {
            "delegation_depth_max": 3,
            "capabilities": ["filesystem.read", "filesystem.write"],
        },
        "evidence_requirements": {"major_finding": {"verification_tier": 2}},
        "termination": ["success_criteria_met"],
        "created_at": "2026-10-14T12:00:00+00:00",
    }


def _accept_goal() -> dict:
    return json.loads(
        (
            Path(__file__).resolve().parents[1] / "examples" / "goal_accept_nonce.json"
        ).read_text(encoding="utf-8")
    )


def test_missing_expected_file_falsifies() -> None:
    tmp = Path("/tmp/gos_falsify_missing")
    tmp.mkdir(parents=True, exist_ok=True)
    for p in tmp.iterdir():
        p.unlink()
    (tmp / "README.md").write_text("seed\n", encoding="utf-8")
    r = falsify_filesystem_criterion(
        criterion_id="sc_write",
        description="apply fix by write file FIX_APPLIED.txt",
        target=tmp,
    )
    assert r.outcome == FalsificationOutcome.FALSIFIED
    assert r.reason == "required_file_absent"


def test_wrong_filename_present_still_falsifies_required_name(tmp_path: Path) -> None:
    (tmp_path / "fix_marker.txt").write_text("done\n", encoding="utf-8")
    r = falsify_filesystem_criterion(
        criterion_id="sc_write",
        description="apply fix by write file FIX_APPLIED.txt",
        target=tmp_path,
    )
    assert r.outcome == FalsificationOutcome.FALSIFIED
    assert r.reason == "required_file_absent"


def test_exact_line_marker_mismatch_falsifies(tmp_path: Path) -> None:
    (tmp_path / "ACCEPT_NONCE_RC1.txt").write_text("wrong-marker\n", encoding="utf-8")
    r = falsify_filesystem_criterion(
        criterion_id="sc_accept",
        description=(
            "apply fix by write file ACCEPT_NONCE_RC1.txt "
            "containing the exact line preprod-accept-rc1"
        ),
        target=tmp_path,
    )
    assert r.outcome == FalsificationOutcome.FALSIFIED
    assert r.reason == "exact_line_marker_absent"


def test_correct_file_and_marker_not_falsified(tmp_path: Path) -> None:
    (tmp_path / "FIX_APPLIED.txt").write_text("ok\n", encoding="utf-8")
    r = falsify_filesystem_criterion(
        criterion_id="sc_write",
        description="apply fix by write file FIX_APPLIED.txt",
        target=tmp_path,
    )
    assert r.outcome == FalsificationOutcome.NOT_FALSIFIED


def test_gate_receipt_met_but_falsifier_blocks_achieved(tmp_path: Path) -> None:
    """Reconciled receipt binds sc_write but file absent → not ACHIEVED."""
    receipts = [
        {
            "binds_criteria": ["sc_inv", "sc_write"],
            "reconciliation_status": "RECONCILED",
            "world_success": True,
            "tool_response": {"success": True},
        }
    ]
    falsifiers = run_filesystem_falsifiers(_write_goal(), tmp_path)
    d = evaluate_goal_completion(
        goal=_write_goal(),
        effect_receipts=receipts,
        falsification_results={k: v.to_dict() for k, v in falsifiers.items()},
    )
    assert d.status != CompletionStatus.ACHIEVED
    assert "sc_write" in d.criteria_unmet
    assert d.reason.startswith("criterion_falsified:")


def test_gate_positive_control_achieved(tmp_path: Path) -> None:
    (tmp_path / "FIX_APPLIED.txt").write_text("ok\n", encoding="utf-8")
    receipts = [
        {
            "binds_criteria": ["sc_inv"],
            "reconciliation_status": "RECONCILED",
            "world_success": True,
            "tool_response": {"success": True},
        },
        {
            "binds_criteria": ["sc_write"],
            "reconciliation_status": "RECONCILED",
            "world_success": True,
            "tool_response": {"success": True},
        },
    ]
    falsifiers = run_filesystem_falsifiers(_write_goal(), tmp_path)
    d = evaluate_goal_completion(
        goal=_write_goal(),
        effect_receipts=receipts,
        falsification_results={k: v.to_dict() for k, v in falsifiers.items()},
        substrate_status="HEALTHY",
    )
    assert d.status == CompletionStatus.ACHIEVED


def test_substrate_unhealthy_forbids_achieved(tmp_path: Path) -> None:
    missing = tmp_path / "no_such_target"
    health = assess_substrate_health(target=missing)
    assert health.status == SubstrateStatus.UNHEALTHY
    assert "target_missing" in health.signals

    (tmp_path / "FIX_APPLIED.txt").write_text("ok\n", encoding="utf-8")
    receipts = [
        {
            "binds_criteria": ["sc_inv", "sc_write"],
            "reconciliation_status": "RECONCILED",
            "world_success": True,
            "tool_response": {"success": True},
        }
    ]
    # Healthy target falsifiers would pass, but substrate of missing path blocks.
    d = evaluate_goal_completion(
        goal=_write_goal(),
        effect_receipts=receipts,
        falsification_results={
            "sc_write": {
                "outcome": "not_falsified",
                "reason": "no_filesystem_counterexample",
                "observation": {},
            }
        },
        substrate_status=health.status.value,
    )
    assert d.status == CompletionStatus.UNKNOWN
    assert "ENVIRONMENT_GAP" in d.reason


def test_bare_timeout_is_not_automatic_infra() -> None:
    health = assess_substrate_health(
        sandbox={"timed_out": True, "process_started": True}
    )
    assert health.status == SubstrateStatus.HEALTHY


def test_never_started_timeout_is_infra() -> None:
    health = assess_substrate_health(
        sandbox={"timed_out": True, "process_started": False}
    )
    assert health.status == SubstrateStatus.UNHEALTHY
    assert "sandbox_never_started_timeout" in health.signals


def test_mission_wrong_filename_not_succeeded(tmp_path: Path) -> None:
    target = tmp_path / "ws"
    target.mkdir()
    (target / "README.md").write_text("seed\n", encoding="utf-8")
    delivery = start_mission(
        _write_goal(),
        target_path=target,
        gos_root=tmp_path / "gos",
        budget_usd=5.0,
        hooks={
            "force_model_mode": "scripted",
            "max_model_cycles": 8,
            "model_script": [
                {"action": "call_tool", "tool_id": "repo.inventory", "args": {}},
                {
                    "action": "call_tool",
                    "tool_id": "workspace.write_text",
                    "args": {"path": "fix_marker.txt", "content": "done\n"},
                },
                {"action": "stop"},
            ],
        },
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert delivery.get("falsification_results", {}).get("sc_write", {}).get(
        "outcome"
    ) == "falsified"
    assert "sc_write" in (delivery["completion"].get("criteria_unmet") or [])
    assert (delivery.get("verification_substrate") or {}).get("status") == "HEALTHY"


def test_mission_missing_target_substrate_blocks(tmp_path: Path) -> None:
    missing = tmp_path / "absent_ws"
    delivery = start_mission(
        _write_goal(),
        target_path=missing,
        gos_root=tmp_path / "gos",
        budget_usd=5.0,
        hooks={
            "force_model_mode": "scripted",
            "max_model_cycles": 4,
            "model_script": [{"action": "stop"}],
        },
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    vs = delivery.get("verification_substrate") or {}
    assert vs.get("status") == "UNHEALTHY"
    assert vs.get("blocked_environment") is True


def test_mission_accept_nonce_positive(tmp_path: Path) -> None:
    target = tmp_path / "ws"
    target.mkdir()
    (target / "README.md").write_text("seed\n", encoding="utf-8")
    delivery = start_mission(
        _accept_goal(),
        target_path=target,
        gos_root=tmp_path / "gos",
        budget_usd=5.0,
        hooks={"force_model_mode": "reactive", "max_model_cycles": 10},
    )
    assert delivery["terminal_status"] == "SUCCEEDED"
    assert (target / "ACCEPT_NONCE_RC1.txt").read_text(encoding="utf-8").strip() == (
        "preprod-accept-rc1"
    )


def test_comparison_metrics_fixture_pack(tmp_path: Path) -> None:
    """Local honesty metrics on known cases — not arXiv claims."""
    cases = []

    # wrong filename
    ws = tmp_path / "wrong"
    ws.mkdir()
    (ws / "fix_marker.txt").write_text("x\n", encoding="utf-8")
    fr = run_filesystem_falsifiers(_write_goal(), ws)
    d = evaluate_goal_completion(
        goal=_write_goal(),
        effect_receipts=[
            {
                "binds_criteria": ["sc_inv", "sc_write"],
                "reconciliation_status": "RECONCILED",
                "world_success": True,
                "tool_response": {"success": True},
            }
        ],
        falsification_results={k: v.to_dict() for k, v in fr.items()},
    )
    cases.append(
        {
            "case": "wrong_filename",
            "false_success": d.status == CompletionStatus.ACHIEVED,
            "falsifier_calls": len(fr),
        }
    )

    # missing file
    ws2 = tmp_path / "missing"
    ws2.mkdir()
    fr2 = run_filesystem_falsifiers(_write_goal(), ws2)
    d2 = evaluate_goal_completion(
        goal=_write_goal(),
        effect_receipts=[],
        falsification_results={k: v.to_dict() for k, v in fr2.items()},
    )
    cases.append(
        {
            "case": "missing_expected_file",
            "false_success": d2.status == CompletionStatus.ACHIEVED,
            "falsified": "sc_write" in d2.criteria_unmet,
            "falsifier_calls": len(fr2),
        }
    )

    # substrate unavailable
    d3 = evaluate_goal_completion(
        goal=_write_goal(),
        criterion_checks={"sc_inv": True, "sc_write": True},
        substrate_status="UNHEALTHY",
    )
    cases.append(
        {
            "case": "target_unavailable",
            "false_success": d3.status == CompletionStatus.ACHIEVED,
            "environment_gap": "ENVIRONMENT_GAP" in d3.reason,
        }
    )

    false_success = sum(1 for c in cases if c.get("false_success"))
    assert false_success == 0
    assert cases[1]["falsified"] is True
    assert cases[2]["environment_gap"] is True
