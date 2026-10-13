"""Acceptance + adversarial tests for Contextual Task Compiler (Execution Brief)."""

from __future__ import annotations

from copy import deepcopy

import pytest

from global_os.cognition.organs import (
    AchieverLoopError,
    TaskCompilerError,
    compile_execution_brief,
    resolve_brief_criterion_ids,
    run_achiever_organ_loop,
    should_emit_new_brief,
)
from global_os.cognition.organs.decomposer import decompose_goal
from global_os.common.hashing import content_hash
from global_os.contracts.validate import validate
from global_os.verification.completion_gate import CompletionStatus


def _goal(**overrides: object) -> dict:
    body: dict = {
        "schema_version": "0.1.0",
        "goal_id": "goal_ctc_001",
        "version": 1,
        "tenant_id": "t",
        "workspace_id": "w",
        "objective": {"text": "Ship a verified engineering report"},
        "success_criteria": [
            {"id": "sc_01", "description": "verified engineering report"},
            {"id": "sc_integration_tests", "description": "интеграционные тесты прошли"},
        ],
        "invariants": ["read_only_target_repo"],
        "non_goals": [],
        "forbidden_outcomes": [],
        "risk": {"tolerance": "low", "maximum_irreversibility": "none"},
        "authority": {
            "delegation_depth_max": 2,
            "capabilities": ["filesystem.read", "git.read"],
        },
        "evidence_requirements": {"major_finding": {"verification_tier": 1}},
        "termination": ["success_criteria_met"],
        "created_at": "2026-10-13T00:00:00+00:00",
    }
    body.update(overrides)  # type: ignore[arg-type]
    body["content_hash"] = content_hash(
        {k: v for k, v in body.items() if k != "content_hash"}
    )
    return body


def _org(goal: dict) -> dict:
    return {
        "id": "org_ctc_test",
        "authority": {"capabilities": list(goal["authority"]["capabilities"])},
        "budget": {"usd": 5.0, "tokens": 4000},
        "output_contract": "artifact_and_evidence",
    }


def test_compile_brief_validates_and_scopes_criteria() -> None:
    goal = _goal()
    before = deepcopy(goal)
    plan = decompose_goal(goal)
    task = plan["tasks"][0]
    brief = compile_execution_brief(
        goal=goal,
        plan=plan,
        task=task,
        org_unit=_org(goal),
        material_reason="first_attempt",
        criterion_ids=["sc_01"],
    )
    assert brief is not None
    validate(brief, "execution_brief.schema.json")
    assert brief["criterion_ids"] == ["sc_01"]
    assert "sc_integration_tests" not in brief["criterion_ids"]
    assert set(brief["allowed_tools"]).issubset(set(goal["authority"]["capabilities"]))
    assert brief["authority_check"]["caps_subset"] is True
    assert goal == before


def test_underspecified_all_criteria_map_binds_none() -> None:
    goal = _goal()
    plan = decompose_goal(goal)
    task = plan["tasks"][0]
    # Decomposer maps every task to all criteria — CTC must not inherit that.
    ids = resolve_brief_criterion_ids(goal=goal, plan=plan, task=task)
    assert ids == []


def test_reject_criterion_not_in_goal() -> None:
    goal = _goal()
    plan = decompose_goal(goal)
    with pytest.raises(TaskCompilerError, match="not in Goal"):
        compile_execution_brief(
            goal=goal,
            plan=plan,
            task=plan["tasks"][0],
            org_unit=_org(goal),
            criterion_ids=["sc_unknown"],
        )


def test_reject_authority_expansion() -> None:
    goal = _goal()
    plan = decompose_goal(goal)
    bad = _org(goal)
    bad["authority"]["capabilities"] = ["filesystem.read", "email.send"]
    with pytest.raises(TaskCompilerError):
        compile_execution_brief(
            goal=goal,
            plan=plan,
            task=plan["tasks"][0],
            org_unit=bad,
            criterion_ids=["sc_01"],
        )


def test_material_gate_skips_duplicate_partial() -> None:
    assert should_emit_new_brief(material_reason="first_attempt", prior_brief=None) is True
    prior = {"brief_id": "brf_x"}
    assert (
        should_emit_new_brief(
            material_reason="partial_unknown",
            prior_brief=prior,
            prior_failure_class="insufficient_evidence",
            new_failure_class="insufficient_evidence",
        )
        is False
    )
    assert (
        should_emit_new_brief(
            material_reason="partial_unknown",
            prior_brief=prior,
            prior_failure_class="insufficient_evidence",
            new_failure_class="some_criteria_unmet",
        )
        is True
    )


def test_achiever_emits_brief_without_self_certifying() -> None:
    goal = _goal(
        success_criteria=[{"id": "sc_01", "description": "verified engineering report"}]
    )

    def attempt_fn(g, plan, route):  # type: ignore[no-untyped-def]
        del g, plan, route
        return {
            "effect_receipts": [
                {
                    "binds_criteria": ["sc_01"],
                    "reconciliation_status": "RECONCILED",
                    "world_success": True,
                    "intended_effect": "repo_audit_report",
                    "observed_effect": "repo_audit_report",
                    "tool_response": {"success": True},
                }
            ],
            "world_effects": False,
            "challenge_win_claimed": False,
        }

    result = run_achiever_organ_loop(
        goal,
        attempt_fn=attempt_fn,
        attempt_budget=1,
        org_unit=_org(goal),
        routing_context={"brief_criterion_ids": ["sc_01"]},
    )
    assert result.briefs
    assert result.briefs[0]["criterion_ids"] == ["sc_01"]
    assert any(e.startswith("brief:") for e in result.events)
    assert result.completion.status == CompletionStatus.ACHIEVED
    # Brief is not a completion certificate
    assert "completion" not in result.briefs[0]


def test_empty_allowed_tools_fail_closed_no_filesystem_default() -> None:
    """P0: brief with allowed_tools=[] must not route as filesystem.read."""
    goal = _goal(
        success_criteria=[{"id": "sc_01", "description": "verified engineering report"}],
        authority={
            "delegation_depth_max": 2,
            "capabilities": [],  # EnvironmentCompiler → empty allow
        },
    )
    # Goal with empty caps still needs ⊆ check via org
    goal["authority"]["capabilities"] = []

    def attempt_fn(g, plan, route):  # type: ignore[no-untyped-def]
        del g, plan, route
        raise AssertionError("attempt_fn must not run when tools are empty")

    with pytest.raises(AchieverLoopError, match="empty allowed_tools"):
        run_achiever_organ_loop(
            goal,
            attempt_fn=attempt_fn,
            attempt_budget=1,
            org_unit={
                "id": "org_empty",
                "authority": {"capabilities": []},
                "budget": {"usd": 1.0, "tokens": 100},
                "output_contract": "artifact_and_evidence",
            },
            routing_context={"brief_criterion_ids": ["sc_01"]},
        )


def test_abc_harness_stub_structural_only() -> None:
    """A/B/C pilot metrics NOT_MEASURED; C must at least produce a valid brief."""
    goal = _goal(
        success_criteria=[{"id": "sc_01", "description": "verified engineering report"}]
    )
    plan = decompose_goal(goal)
    brief_c = compile_execution_brief(
        goal=goal,
        plan=plan,
        task=plan["tasks"][0],
        org_unit=_org(goal),
        criterion_ids=["sc_01"],
    )
    assert brief_c is not None
    validate(brief_c, "execution_brief.schema.json")
    harness = {
        "variant_a_raw_user_brief": "NOT_MEASURED",
        "variant_b_fixed_template": "NOT_MEASURED",
        "variant_c_contextual_brief": "STRUCTURAL_OK",
        "false_success_rate": "NOT_MEASURED",
        "retries": "NOT_MEASURED",
        "cost": "NOT_MEASURED",
    }
    assert harness["variant_c_contextual_brief"] == "STRUCTURAL_OK"
