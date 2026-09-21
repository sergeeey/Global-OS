from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from global_os.adapters.capabilities import CapabilityRegistry
from global_os.cognition.context import ContextAssembler
from global_os.cognition.environment import EnvironmentLifecycle, transition
from global_os.cognition.environment.lifecycle import EnvironmentLifecycleError
from global_os.cognition.retrieval import RetrievalRouter, RetrievalStrategy
from global_os.verification.evaluators import EvaluatorError, EvaluatorRegistry


def test_capability_registry_filters_by_tags_and_risk():
    reg = CapabilityRegistry()
    now = datetime.now(UTC).isoformat()
    reg.register(
        {
            "id": "cap_tool.git.read",
            "schema_version": "0.1.0",
            "kind": "tool",
            "provider": "local",
            "implementation": "git_cli",
            "risk": "low",
            "verified_at": now,
            "capabilities": ["git.read"],
        }
    )
    reg.register(
        {
            "id": "cap_tool.payment",
            "schema_version": "0.1.0",
            "kind": "tool",
            "provider": "stripe",
            "implementation": "stripe_api",
            "risk": "critical",
            "verified_at": now,
            "capabilities": ["payment.execute"],
        }
    )
    found = reg.find(kind="tool", required_tags={"git.read"}, max_risk="moderate")
    assert len(found) == 1
    assert found[0]["id"] == "cap_tool.git.read"


def test_context_assembler_respects_budget_and_provenance():
    items = ContextAssembler().assemble(
        goal_id="goal_x",
        token_budget=100,
        candidates=[
            {
                "source": "goal",
                "type": "goal_fragment",
                "trust": "USER_TRUSTED",
                "token_cost": 40,
                "reason_included": "needed objective",
                "priority": 1,
            },
            {
                "source": "obs_1",
                "type": "observation",
                "trust": "EXTERNAL_UNTRUSTED",
                "token_cost": 80,
                "reason_included": "too large",
                "priority": 2,
            },
            {
                "source": "bel_1",
                "type": "belief",
                "trust": "DERIVED",
                "token_cost": 30,
                "reason_included": "supports claim",
                "priority": 3,
            },
        ],
    )
    assert len(items) == 2
    assert all("reason_included" in i for i in items)
    assert sum(i["token_cost"] for i in items) <= 100


def test_retrieval_router_not_always_graph():
    r = RetrievalRouter()
    assert r.route("similar_document") == RetrievalStrategy.VECTOR
    assert r.route("dependency_of_invalidated_claim") == RetrievalStrategy.GRAPH
    assert r.route("what_we_knew_at_time") == RetrievalStrategy.TEMPORAL


def test_evaluator_rejects_self_validation():
    reg = EvaluatorRegistry()
    with pytest.raises(EvaluatorError, match="GOS-I24"):
        reg.register(
            {
                "id": "evl_bad",
                "schema_version": "0.1.0",
                "model": "judge-x",
                "domain": ["repo_audit"],
                "calibrated_on": {"dataset_id": "self"},
                "metrics": {
                    "human_agreement": 0.9,
                    "swap_consistency": 0.9,
                    "verbosity_bias": 0.1,
                    "false_positive": 0.1,
                    "false_negative": 0.1,
                },
                "valid_until": (datetime.now(UTC) + timedelta(days=30)).isoformat(),
            }
        )


def test_environment_lifecycle_governed():
    state = EnvironmentLifecycle.PROPOSED
    state = transition(state, EnvironmentLifecycle.SANDBOXED)
    state = transition(state, EnvironmentLifecycle.EVALUATED)
    state = transition(state, EnvironmentLifecycle.APPROVED)
    state = transition(state, EnvironmentLifecycle.ACTIVE)
    with pytest.raises(EnvironmentLifecycleError):
        transition(EnvironmentLifecycle.REVOKED, EnvironmentLifecycle.ACTIVE)
