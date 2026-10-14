"""Regressions for CHANGES_REQUESTED RC review (PR #49/#50)."""

from __future__ import annotations

import json
from pathlib import Path

from global_os.adapters.models.openai_compat import extract_json_object
from global_os.runtime.preprod import start_mission
from global_os.verification.completion_gate import CompletionStatus, evaluate_goal_completion
from global_os.verification.falsifiers import (
    FalsificationOutcome,
    falsify_filesystem_criterion,
    run_filesystem_falsifiers,
)
from global_os.verification.substrate_health import SubstrateStatus, assess_substrate_health
from global_os.world.tools.research_scan import run_research_scan, verify_research_scan
from global_os.world.tools.workspace_io import run_workspace_write_text


def test_research_scan_empty_sources_and_claims_not_ok(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("plain prose without links or claim bullets.\n", encoding="utf-8")
    report = run_research_scan(tmp_path)
    assert report.get("files_scanned", 0) >= 1
    assert report.get("sources") == []
    assert report.get("claims") == []
    v = verify_research_scan(report)
    assert v.get("ok") is False
    assert v.get("reason") == "empty_sources"


def test_research_scan_empty_evidence_cannot_succeed_mission(tmp_path: Path) -> None:
    ws = tmp_path / "corpus"
    ws.mkdir()
    (ws / "notes.txt").write_text("no links here\n", encoding="utf-8")
    goal = {
        "schema_version": "0.1.0",
        "goal_id": "goal_research_empty_001",
        "version": 1,
        "tenant_id": "tenant_local",
        "workspace_id": "ws_r",
        "objective": {"text": "Scan corpus for sources and claims"},
        "success_criteria": [
            {"id": "sc_src", "description": "source inventory from research scan"},
            {"id": "sc_claims", "description": "claim spans extracted by research scan"},
        ],
        "invariants": ["sandbox_target_only"],
        "non_goals": [],
        "forbidden_outcomes": [],
        "risk": {"tolerance": "low", "maximum_irreversibility": "none"},
        "authority": {
            "delegation_depth_max": 3,
            "capabilities": ["filesystem.read", "web.read"],
        },
        "evidence_requirements": {"major_finding": {"verification_tier": 2}},
        "termination": ["success_criteria_met"],
        "created_at": "2026-10-14T12:00:00+00:00",
    }
    delivery = start_mission(
        goal,
        target_path=ws,
        gos_root=tmp_path / "gos",
        budget_usd=5.0,
        hooks={
            "force_model_mode": "scripted",
            "model_script": [
                {"action": "call_tool", "tool_id": "research.scan", "args": {}},
                {"action": "stop"},
            ],
        },
    )
    assert delivery["terminal_status"] != "SUCCEEDED"
    assert delivery["completion"]["status"] != CompletionStatus.ACHIEVED.value


def test_workspace_overwrite_forbidden_by_default(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("original\n", encoding="utf-8")
    report = run_workspace_write_text(
        tmp_path, rel_path="README.md", content="clobber\n", allow_overwrite=False
    )
    assert report.get("ok") is False
    assert report.get("error") == "overwrite_forbidden"
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "original\n"


def test_mission_overwrite_does_not_clobber_existing(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "README.md").write_text("keep-me\n", encoding="utf-8")
    goal = {
        "schema_version": "0.1.0",
        "goal_id": "goal_overwrite_001",
        "version": 1,
        "tenant_id": "tenant_local",
        "workspace_id": "ws_w",
        "objective": {"text": "Write README.md"},
        "success_criteria": [
            {
                "id": "sc_write",
                "description": "apply fix by write file README.md in workspace",
            }
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
        "created_at": "2026-10-14T12:00:00+00:00",
    }
    delivery = start_mission(
        goal,
        target_path=ws,
        gos_root=tmp_path / "gos",
        budget_usd=5.0,
        hooks={
            "force_model_mode": "scripted",
            "model_script": [
                {
                    "action": "call_tool",
                    "tool_id": "workspace.write_text",
                    "args": {"path": "README.md", "content": "clobber\n"},
                },
                {"action": "stop"},
            ],
        },
    )
    assert (ws / "README.md").read_text(encoding="utf-8") == "keep-me\n"
    assert delivery["terminal_status"] != "SUCCEEDED"


def test_exact_line_rejects_substring_not_full_line(tmp_path: Path) -> None:
    (tmp_path / "ACCEPT_NONCE_RC1.txt").write_text(
        "prefix-preprod-accept-rc1-suffix\n", encoding="utf-8"
    )
    r = falsify_filesystem_criterion(
        criterion_id="sc_accept",
        description="write file ACCEPT_NONCE_RC1.txt with acceptance marker",
        target=tmp_path,
        contract_text=(
            "create ACCEPT_NONCE_RC1.txt containing the exact line preprod-accept-rc1"
        ),
    )
    assert r.outcome == FalsificationOutcome.FALSIFIED
    assert r.reason == "exact_line_marker_absent"


def test_exact_line_from_objective_not_only_criterion(tmp_path: Path) -> None:
    goal = json.loads(
        (
            Path(__file__).resolve().parents[1] / "examples" / "goal_accept_nonce.json"
        ).read_text(encoding="utf-8")
    )
    (tmp_path / "ACCEPT_NONCE_RC1.txt").write_text("wrong\n", encoding="utf-8")
    results = run_filesystem_falsifiers(goal, tmp_path)
    assert "sc_accept" in results
    assert results["sc_accept"].outcome == FalsificationOutcome.FALSIFIED


def test_exact_line_full_line_ok(tmp_path: Path) -> None:
    (tmp_path / "ACCEPT_NONCE_RC1.txt").write_text("preprod-accept-rc1\n", encoding="utf-8")
    r = falsify_filesystem_criterion(
        criterion_id="sc_accept",
        description="write file ACCEPT_NONCE_RC1.txt",
        target=tmp_path,
        contract_text="exact line preprod-accept-rc1",
    )
    assert r.outcome == FalsificationOutcome.NOT_FALSIFIED


def test_sandbox_signals_from_hooks_reach_delivery(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "README.md").write_text("x\n", encoding="utf-8")
    goal = {
        "schema_version": "0.1.0",
        "goal_id": "goal_substrate_hook_001",
        "version": 1,
        "tenant_id": "tenant_local",
        "workspace_id": "ws_s",
        "objective": {"text": "noop"},
        "success_criteria": [
            {"id": "sc_inv", "description": "workspace inventory with file listing"}
        ],
        "invariants": [],
        "non_goals": [],
        "forbidden_outcomes": [],
        "risk": {"tolerance": "low", "maximum_irreversibility": "none"},
        "authority": {
            "delegation_depth_max": 3,
            "capabilities": ["filesystem.read"],
        },
        "evidence_requirements": {"major_finding": {"verification_tier": 2}},
        "termination": ["success_criteria_met"],
        "created_at": "2026-10-14T12:00:00+00:00",
    }
    delivery = start_mission(
        goal,
        target_path=ws,
        gos_root=tmp_path / "gos",
        budget_usd=5.0,
        hooks={
            "force_model_mode": "scripted",
            "model_script": [{"action": "stop"}],
            "sandbox_signals": {"timed_out": True, "process_started": False},
        },
    )
    vs = delivery.get("verification_substrate") or {}
    assert vs.get("status") == SubstrateStatus.UNHEALTHY.value
    assert "sandbox_never_started_timeout" in (vs.get("signals") or [])
    # Cannot ACHIEVE when substrate unhealthy even if checks would pass.
    d = evaluate_goal_completion(
        goal=goal,
        criterion_checks={"sc_inv": True},
        substrate_status=vs.get("status"),
    )
    assert d.status != CompletionStatus.ACHIEVED


def test_extract_json_object_nested_fenced() -> None:
    text = (
        "Here:\n```json\n"
        '{"action":"call_tool","tool_id":"workspace.write_text",'
        '"args":{"path":"FIX_APPLIED.txt","content":"ok\\n"}}\n'
        "```\n"
    )
    extracted = extract_json_object(text)
    assert extracted is not None
    parsed = json.loads(extracted)
    assert parsed["action"] == "call_tool"
    assert parsed["args"]["path"] == "FIX_APPLIED.txt"


def test_extract_json_object_rejects_truncated_inner_brace() -> None:
    # Old non-greedy regex would stop after first nested `}`.
    bad_inner = '{"action":"call_tool","args":{"path":"a.txt"}'
    # Balanced extract from bare text with trailing noise
    text = bad_inner + ',"tool_id":"x"}'
    extracted = extract_json_object(text)
    assert extracted is not None
    parsed = json.loads(extracted)
    assert parsed["tool_id"] == "x"
    assert parsed["args"]["path"] == "a.txt"


def test_assess_substrate_bare_timeout_still_healthy() -> None:
    h = assess_substrate_health(sandbox={"timed_out": True, "process_started": True})
    assert h.status == SubstrateStatus.HEALTHY
