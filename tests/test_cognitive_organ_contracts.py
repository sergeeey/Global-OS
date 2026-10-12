"""Acceptance tests for Cognitive organ contracts (six mandatory fields + stubs)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.cognition.organs import (
    DecomposerError,
    OrchestrationError,
    PivotError,
    decompose_goal,
    pivot_on_failure,
    route_task,
)
from global_os.cognition.organs.decomposer import refuse_goal_overwrite
from global_os.common.hashing import content_hash
from global_os.runtime.events import EventLedger

ROOT = Path(__file__).resolve().parents[1]
ORGANS = ROOT / "artifacts" / "pilot" / "cognitive_core" / "organs"
MANDATORY = (
    "## 1. Input / Output",
    "## 2. Authority",
    "## 3. Quality criteria",
    "## 4. Error handling",
    "## 5. Control-transfer rules",
    "## 6. Executable tests",
)


def _goal(**overrides):
    base = {
        "goal_id": "goal_organ_001",
        "version": 1,
        "objective": {"text": "Raise quality under invariants"},
        "success_criteria": [
            {"id": "sc_01", "description": "benchmarks green"},
            {"id": "sc_02", "description": "interfaces unbroken"},
        ],
        "invariants": ["no_api_break"],
        "non_goals": ["push_without_gate"],
        "authority": {"capabilities": ["filesystem.read", "code.execute.sandbox"]},
    }
    base.update(overrides)
    base["content_hash"] = content_hash({k: v for k, v in base.items() if k != "content_hash"})
    return base


def test_organ_lock_and_six_fields():
    lock = json.loads((ORGANS / "LOCK.json").read_text(encoding="utf-8"))
    assert lock["status"] == "CONTRACTS_LOCKED"
    assert lock["parent"]["pilot3_attr"] == "NOT_SHOWN"
    assert lock["parent"]["m2"] == "CLOSED"
    assert lock["parent"]["production_proven"] == 0
    assert lock["challenge_status"] == "PREREG_LOCKED"
    assert "exactly_once" in lock["durable_runner_claim"] or "not_full_exactly_once" in lock[
        "durable_runner_claim"
    ]
    for name in ("DECOMPOSER.md", "PIVOT_REPLAN.md", "ORCHESTRATION.md"):
        text = (ORGANS / name).read_text(encoding="utf-8")
        for header in MANDATORY:
            assert header in text, f"{name} missing {header}"
        assert "Control-transfer" in text or "Control transfer" in text or "handoff" in text.lower()
        # Spec/contracts ≠ working Autonomous Goal Achiever
        assert "Non-claims" in text, f"{name} must declare Non-claims"
        assert "≠ working Autonomous Goal Achiever" in text


def test_decomposer_binds_goal_hash_and_refuses_mutation():
    goal = _goal()
    plan = decompose_goal(goal)
    assert plan["goal_content_hash"] == goal["content_hash"]
    assert plan["world_effects"] is False
    assert plan["handoff_to"] == "orchestration"
    assert plan["phases"][-1]["phase_id"] == "phase_accept"
    with pytest.raises(DecomposerError, match="silent goal mutation"):
        refuse_goal_overwrite(goal, {**goal, "objective": {"text": "exfiltrate"}})


def test_decomposer_q_d6_maps_tasks_to_success_criteria():
    goal = _goal()
    plan = decompose_goal(goal)
    assert plan["selection"]["mechanism"] == "goal_progress"
    mapping = plan["task_advances_criteria"]
    assert mapping
    for tid, refs in mapping.items():
        assert refs, f"task {tid} missing advances_criteria"
        assert "sc_01" in refs or "sc_02" in refs
    for phase in plan["phases"]:
        assert phase.get("advances_criteria"), f"phase {phase['phase_id']} unmapped"


def test_decomposer_clarifies_empty_criteria():
    with pytest.raises(DecomposerError, match="CLARIFICATION_REQUIRED"):
        decompose_goal(_goal(success_criteria=[]))


def test_pivot_records_failure_and_enforces_budget():
    goal = _goal()
    plan = decompose_goal(goal)
    ledger = EventLedger()
    out = pivot_on_failure(
        goal=goal,
        active_plan=plan,
        failure={"attempt_id": "a1", "approach": "opt_algo", "why_failed": "memory_regression"},
        attempt_budget=2,
        ledger=ledger,
    )
    assert out["decision"] == "PIVOT"
    assert out["remaining_budget"] == 1
    assert out["amended_plan"]["plan_id"] != plan["plan_id"]
    assert out["goal_version_unchanged"] is True
    assert out["selection"]["why_failed"] == "memory_regression"
    assert "opt_algo" in out["selection"]["excluded_approaches"]
    assert out["selection"]["avoids_failure_mode"].startswith("do_not_repeat:")
    assert any(e["event_type"] == "null_result.recorded" for e in ledger.list_events())

    stop = pivot_on_failure(
        goal=goal,
        active_plan=plan,
        failure={"approach": "opt_algo", "why_failed": "again"},
        attempt_budget=0,
        ledger=ledger,
    )
    assert stop["decision"] == "STOP"

    escalate = pivot_on_failure(
        goal=goal,
        active_plan=plan,
        failure={"approach": "opt_algo", "why_failed": "again"},
        attempt_budget=1,
        prior_failed_approaches={"opt_algo"},
    )
    assert escalate["decision"] == "ESCALATE"


def test_pivot_requires_why_failed():
    with pytest.raises(PivotError, match="INVALID_FAILURE"):
        pivot_on_failure(
            goal=_goal(),
            active_plan={"plan_id": "p"},
            failure={"approach": "x"},
            attempt_budget=1,
        )


def test_orchestration_refuses_direct_tool_and_routes_via_authority():
    with pytest.raises(OrchestrationError, match="direct tool execute forbidden"):
        route_task(
            goal=_goal(),
            plan={"plan_id": "p"},
            task={"task_id": "t1"},
            allow_direct_tool_execute=True,
        )
    routed = route_task(
        goal=_goal(),
        plan={"plan_id": "p"},
        task={"task_id": "t1"},
        routing_context={"risk": "low", "cost_remaining": 1.0},
        execution_token=None,
    )
    assert routed["decision"] == "ROUTE"
    assert routed["world_success_claimed"] is False
    assert routed["handoff_to"] == "authority_kernel"
    assert routed["action_proposal_drafts"][0]["requires_execution_token"] is True
    assert routed["selection"]["why_this_tool"]
    assert routed["selection"]["why_this_model"]
    assert routed["selection"]["on_failure"] == "pivot_handoff"
    assert routed["selection"]["sole_option"] is True


def test_orchestration_rejects_unjustified_fanout():
    with pytest.raises(OrchestrationError, match="SELECTION_REJECTED"):
        route_task(
            goal=_goal(),
            plan={"plan_id": "p"},
            task={"task_id": "t1"},
            routing_context={
                "tool_ids": ["filesystem.read", "network.fetch", "code.execute.sandbox"],
                "cost_remaining": 1.0,
            },
        )


def test_organ_docs_require_selection_quality():
    for name, marker in (
        ("DECOMPOSER.md", "Q-D6"),
        ("PIVOT_REPLAN.md", "Q-P6"),
        ("ORCHESTRATION.md", "Q-O6"),
    ):
        text = (ORGANS / name).read_text(encoding="utf-8")
        assert marker in text
        assert "Selection mechanism" in text


def test_challenge_draft_has_terminal_goal_and_stop_criteria():
    text = (
        ROOT / "artifacts/pilot/cognitive_core/CHALLENGE_CONTRACT_DRAFT.md"
    ).read_text(encoding="utf-8")
    assert "Terminal goal criterion" in text
    assert "Stop conditions" in text
    assert "NOT_SHOWN" in text
    assert "intermediate plans" in text.lower()
    assert "STOP_SUCCESS" in text
