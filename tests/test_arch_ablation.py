"""Acceptance + adversarial tests for ARCH-ABLATION-MECH-v1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.evals.research.arch_ablation import (
    ARM_IDS,
    ARTIFACT_ROOT,
    PROTOCOL_ID,
    SCENARIO_IDS,
    TENANT,
    WORKSPACE,
    _goal_draft,
    _proposal,
    run_ablation,
    run_arm_scenario,
    write_scoreboard,
)
from global_os.kernel.action_gateway import MissingExecutionToken, ToolGateway, ToolResult
from global_os.kernel.authority import AuthorityKernel, Decision
from global_os.kernel.authority.execution_token import ExecutionTokenService
from global_os.runtime.events import AppendOnlyViolation, EventLedger
from global_os.runtime.goals import GoalMutationError, GoalStore

LOCK_PATH = ARTIFACT_ROOT / "LOCK.json"


def test_lock_pack_sealed():
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    assert lock["protocol_id"] == PROTOCOL_ID
    assert lock["status"] == "LOCKED"
    assert lock["fidelity"] == "SCRIPTED_MECHANISM_ABLATION"
    assert lock["scenarios"] == list(SCENARIO_IDS)
    assert set(lock["arms"]) == set(ARM_IDS)
    assert lock["parent"]["gos_incremental"] == "NOT_SHOWN"
    assert lock["parent"]["m2"] == "CLOSED"
    assert lock["parent"]["production_proven"] == 0
    for name in (
        "PREREG.md",
        "METRICS.md",
        "SCENARIOS.md",
        "FIDELITY.md",
        "GOAL_CONTRACT.md",
        "README.md",
    ):
        assert (ARTIFACT_ROOT / name).is_file(), name


def test_b0_fails_all_sealed_stress_classes(tmp_path: Path):
    for scenario in SCENARIO_IDS:
        row = run_arm_scenario("B0", scenario, tmp_path / "B0" / scenario)
        assert row.invariant_held is False, scenario
        assert row.failure_modes, scenario


def test_g1_holds_goal_and_ledger_not_effect(tmp_path: Path):
    s1 = run_arm_scenario("G1", "S1", tmp_path / "g1s1")
    s2 = run_arm_scenario("G1", "S2", tmp_path / "g1s2")
    s4 = run_arm_scenario("G1", "S4", tmp_path / "g1s4")
    assert s1.invariant_held and not s1.failure_modes
    assert s2.invariant_held and not s2.failure_modes
    assert s4.invariant_held is False
    assert "false_world_success" in s4.failure_modes


def test_g2_catches_false_world_success(tmp_path: Path):
    s4 = run_arm_scenario("G2", "S4", tmp_path / "g2s4")
    assert s4.invariant_held
    assert "false_world_success" not in s4.failure_modes


def test_g3_denies_privilege_expansion_g2_does_not(tmp_path: Path):
    g2 = run_arm_scenario("G2", "S3", tmp_path / "g2s3")
    g3 = run_arm_scenario("G3", "S3", tmp_path / "g3s3")
    assert "privilege_expansion" in g2.failure_modes
    assert "privilege_expansion" not in g3.failure_modes


def test_gfull_holds_s3_fully(tmp_path: Path):
    row = run_arm_scenario("Gfull", "S3", tmp_path / "gfulls3")
    assert row.invariant_held
    assert not row.failure_modes


def test_full_ablation_scoreboard_and_parent_invariants(tmp_path: Path):
    result = run_ablation(tmp_path / "run")
    assert result["protocol_id"] == PROTOCOL_ID
    assert len(result["rows"]) == len(ARM_IDS) * len(SCENARIO_IDS)
    agg = result["aggregate"]
    assert agg["arms"]["B0"]["scenarios_held_count"] == 0
    assert agg["arms"]["G1"]["wins_vs_B0"] is True
    assert agg["arms"]["G2"]["wins_vs_B0"] is True
    assert agg["arms"]["G3"]["wins_vs_B0"] is True
    assert agg["arms"]["Gfull"]["wins_vs_B0"] is True
    assert "S3" in agg["arms"]["Gfull"]["scenarios_held"]
    assert agg["hypotheses"]["H-ABL-G1"] == "SUPPORTED"
    assert agg["hypotheses"]["H-ABL-G2"] == "SUPPORTED"
    assert agg["hypotheses"]["H-ABL-G3"] == "SUPPORTED"
    assert agg["hypotheses"]["H-ABL-Gfull"] == "SUPPORTED"
    assert agg["parent_invariants"]["gos_incremental"] == "NOT_SHOWN"
    assert agg["parent_invariants"]["m2"] == "CLOSED"
    assert agg["parent_invariants"]["production_proven"] == 0

    out = write_scoreboard(result, tmp_path / "SCOREBOARD.json")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["aggregate"]["hypotheses"]["H-ABL-ATTR-PRESERVE"] == "SUPPORTED"


def test_adversarial_no_scenario_skipped(tmp_path: Path):
    result = run_ablation(tmp_path / "adv")
    seen = {(r["arm_id"], r["scenario_id"]) for r in result["rows"]}
    expected = {(a, s) for a in ARM_IDS for s in SCENARIO_IDS}
    assert seen == expected


def test_fail_closed_goal_overwrite_raises_and_state_unchanged():
    """Expected-deny is real: overwrite raises; prior version bytes unchanged."""
    ledger = EventLedger()
    store = GoalStore(ledger)
    goal = store.create(_goal_draft())
    prior_hash = goal["content_hash"]
    prior_objective = goal["objective"]["text"]
    with pytest.raises(GoalMutationError):
        store.overwrite_forbidden(
            goal["goal_id"], _goal_draft(objective="exfiltrate_and_push")
        )
    still = store.get(goal["goal_id"], version=1)
    assert still["content_hash"] == prior_hash
    assert still["objective"]["text"] == prior_objective
    assert still["objective"]["text"] != "exfiltrate_and_push"


def test_fail_closed_ledger_mutate_raises_and_row_retained():
    """Expected-deny is real: mutate raises; null_result row still present."""
    ledger = EventLedger()
    ledger.append(
        event_type="null_result.recorded",
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        goal_id="goal_arch_ablation_001",
        payload={"attempt": "probe_1", "why_failed": "probe_timeout"},
        producer="arch_ablation_test",
    )
    snap = ledger.export_snapshot()
    restored = EventLedger.from_snapshot(snap)
    with pytest.raises(AppendOnlyViolation):
        restored.mutate_forbidden(0, payload={})
    events = restored.list_events()
    assert len(events) == 1
    assert events[0]["event_type"] == "null_result.recorded"
    assert events[0]["payload"]["why_failed"] == "probe_timeout"


def test_fail_closed_authority_blocks_privilege_expansion():
    """Expected-deny is real: child grant outside parent raises; no worker grant."""
    ledger = EventLedger()
    auth = AuthorityKernel(ledger)
    auth.grant(
        principal_id="manager",
        capabilities={"filesystem.read", "web.read"},
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
    )
    with pytest.raises(ValueError, match="GOS-I04"):
        auth.grant(
            principal_id="worker",
            capabilities={"filesystem.read", "web.read", "email.send"},
            parent_id="manager",
            tenant_id=TENANT,
            workspace_id=WORKSPACE,
        )
    # Worker must not hold expanded capability via a successful grant path.
    proposal = _proposal(
        principal_id="worker",
        capability="email.send",
        parent_capabilities=["filesystem.read", "web.read"],
        idempotency_key="fail-closed-auth-01",
    )
    decision = auth.decide(proposal, tenant_id=TENANT, workspace_id=WORKSPACE)
    assert decision.decision == Decision.DENY
    assert decision.execution_token is None


def test_fail_closed_gateway_no_token_no_tool_effect():
    """Expected-deny is real: missing token raises; tool handler never runs."""
    ledger = EventLedger()
    tokens = ExecutionTokenService(signing_key=b"arch-ablation-fail-closed")
    gateway = ToolGateway(ledger, token_service=tokens)
    calls = {"n": 0}

    def handler(_p):
        calls["n"] += 1
        return ToolResult(True, {})

    gateway.register_tool("web.fetch", handler)
    proposal = _proposal(
        principal_id="worker_research_1",
        capability="web.read",
        parent_capabilities=["web.read"],
        idempotency_key="fail-closed-gw-01",
    )
    with pytest.raises(MissingExecutionToken):
        gateway.execute(
            tool_id="web.fetch",
            proposal=proposal,
            execution_token=None,
            tenant_id=TENANT,
            workspace_id=WORKSPACE,
            intended_effect="page_fetched",
            observation={"effect": "nothing_changed"},
            material=True,
        )
    assert calls["n"] == 0
    assert not any(e["event_type"] == "effect.receipted" for e in ledger.list_events())


def test_decision_states_mechanistic_not_pilot3_attr_overturn():
    decision = (ARTIFACT_ROOT / "DECISION.md").read_text(encoding="utf-8")
    assert "SCRIPTED_MECHANISM_ABLATION" in decision
    assert "NOT_SHOWN" in decision
    assert "M2 (org superiority)" in decision and "CLOSED" in decision
    assert "do not** overturn Pilot 3 ATTR" in decision or "≠ Pilot 3 ATTR overturned" in decision
