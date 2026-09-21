from __future__ import annotations

from datetime import UTC, datetime

import pytest

from global_os.cognition.decomposition import build_repo_audit_dag
from global_os.cognition.environment import (
    EnvironmentChangeError,
    EnvironmentChangeGate,
    EnvironmentCompiler,
    EnvironmentLifecycle,
)
from global_os.cognition.organization import MissionAssigner, MissionError, OrganizationCompiler
from global_os.common.hashing import content_hash
from global_os.epistemic import EpistemicStore
from global_os.runtime.events import EventLedger, EventReplayEngine
from global_os.runtime.goals import GoalStore


def _compile_env(sample_goal_factory) -> tuple[EventLedger, dict, dict]:
    ledger = EventLedger()
    goal = GoalStore(ledger).create(sample_goal_factory())
    org = OrganizationCompiler(ledger).compile_manager_workers(
        goal,
        worker_missions=["Audit repository structure"],
        budget_usd=10.0,
        budget_tokens=8000,
    )
    worker = org["workers"][0]
    task = build_repo_audit_dag(goal["goal_id"])[0]
    env = EnvironmentCompiler().compile(
        goal=goal, org_unit=worker, task=task, verification_tier=2
    )
    return ledger, worker, env


def test_environment_change_requires_gated_promotion(sample_goal):
    ledger, _worker, env = _compile_env(sample_goal)
    gate = EnvironmentChangeGate(ledger)
    gate.register_active(env)
    proposal = gate.propose(
        environment_id=env["id"],
        proposer="worker",
        reason="need stronger sandbox for eval",
        diff={"sandbox": {"profile": "container"}},
        evaluation_plan="sandbox eval then approve",
        required_authority=["environment.promote"],
        expected_gain="isolation",
        new_risks=["container escape residual"],
        tenant_id="t",
        workspace_id="w",
        goal_id=env.get("goal_id"),
    )
    assert proposal["lifecycle_state"] == "PROPOSED"
    gate.advance(
        proposal["id"],
        EnvironmentLifecycle.SANDBOXED,
        principal_capabilities=[],
        tenant_id="t",
        workspace_id="w",
    )
    gate.advance(
        proposal["id"],
        EnvironmentLifecycle.EVALUATED,
        principal_capabilities=[],
        tenant_id="t",
        workspace_id="w",
    )
    with pytest.raises(EnvironmentChangeError, match="insufficient authority"):
        gate.advance(
            proposal["id"],
            EnvironmentLifecycle.APPROVED,
            principal_capabilities=["filesystem.read"],
            tenant_id="t",
            workspace_id="w",
            approval_ref="apr_1",
        )
    with pytest.raises(EnvironmentChangeError, match="approval_ref"):
        gate.advance(
            proposal["id"],
            EnvironmentLifecycle.APPROVED,
            principal_capabilities=["environment.promote"],
            tenant_id="t",
            workspace_id="w",
        )
    gate.advance(
        proposal["id"],
        EnvironmentLifecycle.APPROVED,
        principal_capabilities=["environment.promote"],
        tenant_id="t",
        workspace_id="w",
        approval_ref="apr_1",
    )
    gate.advance(
        proposal["id"],
        EnvironmentLifecycle.ACTIVE,
        principal_capabilities=["environment.promote"],
        tenant_id="t",
        workspace_id="w",
    )
    updated = gate.get_environment(env["id"])
    assert updated["sandbox"]["profile"] == "container"
    assert gate.get_proposal(proposal["id"])["lifecycle_state"] == "ACTIVE"


def test_environment_change_rejects_identity_rewrite(sample_goal):
    ledger, _worker, env = _compile_env(sample_goal)
    gate = EnvironmentChangeGate(ledger)
    gate.register_active(env)
    with pytest.raises(EnvironmentChangeError, match="identity"):
        gate.propose(
            environment_id=env["id"],
            proposer="worker",
            reason="hijack",
            diff={"id": "env_evil"},
            evaluation_plan="none",
            required_authority=["environment.promote"],
            tenant_id="t",
            workspace_id="w",
        )


def test_mission_outcome_not_microsteps(sample_goal):
    ledger = EventLedger()
    goal = GoalStore(ledger).create(sample_goal())
    org = OrganizationCompiler(ledger).compile_manager_workers(
        goal,
        worker_missions=["Determine regulatory feasibility"],
        budget_usd=5.0,
        budget_tokens=4000,
    )
    worker = org["workers"][0]
    assigner = MissionAssigner(ledger)
    mission = assigner.assign(
        org_unit=worker,
        objective="Determine regulatory feasibility for payment feature",
        success_criteria=["written feasibility memo", "citations to primary sources"],
        evidence_required=["official_docs", "effect_receipt_if_any"],
        constraints=["no payment execution"],
        tenant_id="t",
        workspace_id="w",
    )
    assert mission["org_unit_id"] == worker["id"]
    assert mission["authority"]["capabilities"] == worker["authority"]["capabilities"]
    with pytest.raises(MissionError, match="microsteps"):
        assigner.assign(
            org_unit=worker,
            objective="Open Google then open the regulator site",
            success_criteria=["done"],
            evidence_required=["none"],
            tenant_id="t",
            workspace_id="w",
        )


def test_event_replay_rebuilds_status_projection():
    ledger = EventLedger()
    epi = EpistemicStore(ledger)
    now = datetime.now(UTC).isoformat()
    epi.put_evidence(
        {
            "evidence_id": "ev_r1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "status": "SOURCE_CONTENT_VERIFIED",
            "trust_label": "ORG_TRUSTED",
            "recorded_at": now,
            "known_at": now,
            "content_digest": content_hash({"a": 1}),
        }
    )
    epi.put_claim(
        {
            "claim_id": "cl_r1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "A holds",
            "status": "ACTIVE",
            "evidence_ids": ["ev_r1"],
            "confidence": "MEDIUM",
            "confidence_basis": "ev",
            "recorded_at": now,
        }
    )
    epi.put_model(
        {
            "model_id": "mdl_r1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "model A",
            "status": "ACTIVE",
            "depends_on_claim_ids": ["cl_r1"],
            "recorded_at": now,
        }
    )
    epi.invalidate_evidence("ev_r1", tenant_id="t", workspace_id="w", reason="retract")
    replay = EventReplayEngine(ledger)
    projection = replay.rebuild_status_projection(
        seed={
            "evidence": {"ev_r1": "SOURCE_CONTENT_VERIFIED"},
            "claim": {"cl_r1": "ACTIVE"},
            "model": {"mdl_r1": "ACTIVE"},
        },
        goal_id="goal_x",
        tenant_id="t",
        workspace_id="w",
    )
    assert projection["evidence"]["ev_r1"] == "INVALIDATED"
    assert projection["claim"]["cl_r1"] == "STALE"
    assert projection["model"]["mdl_r1"] == "STALE"
    assert any(e["event_type"] == "projection.rebuilt" for e in ledger.list_events())
