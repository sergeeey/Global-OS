from __future__ import annotations

from global_os.contracts import validate


def test_execution_environment_contract_validates():
    env = {
        "id": "env_repo_audit_arch_001",
        "schema_version": "0.1.0",
        "task_id": "task_architecture",
        "org_unit_id": "org_manager",
        "goal_id": "goal_repo_audit_001",
        "model_requirements": {
            "reasoning": "medium",
            "vision": False,
            "coding": True,
            "tool_use": True,
        },
        "reasoning_budget": {
            "requested": {"tokens": 8000, "usd": 0.5, "wall_time_seconds": 600},
            "maximum": {"tokens": 20000, "usd": 2.0, "wall_time_seconds": 1800},
            "policy_source": "goal_contract",
        },
        "tools": {"allow": ["filesystem.read", "git.read"]},
        "sandbox": {"profile": "process_local"},
        "retrieval": {"strategy": "hybrid"},
        "memory": {"scopes": ["episodic", "negative"]},
        "context": {
            "token_budget": 12000,
            "freshness": {"max_age": "7d", "prefer_verified": True},
            "include_refs": ["goal_contract"],
        },
        "clarification": {
            "materiality_policy": "high_impact_only",
            "ask_when": ["authority_gap", "irreversible_action"],
            "assume_when": ["formatting_only", "low_impact"],
            "record_assumption": True,
            "max_rounds": 2,
        },
        "verification": {"required_tier": 2},
        "output_contract": "artifact_and_evidence",
    }
    validate(env, "execution_environment.schema.json")


def test_observation_and_belief_are_distinct_schemas():
    from datetime import UTC, datetime

    from global_os.common.hashing import content_hash

    now = datetime.now(UTC).isoformat()
    digest = content_hash({"s": "file X exists"})
    observation = {
        "observation_id": "obs_001",
        "schema_version": "0.1.0",
        "goal_id": "goal_x",
        "statement": "CONSTITUTION.md exists",
        "source_ref": "CONSTITUTION.md",
        "trust_label": "USER_TRUSTED",
        "observed_at": now,
        "recorded_at": now,
        "known_at": now,
        "content_digest": digest,
    }
    belief = {
        "belief_id": "bel_001",
        "schema_version": "0.1.0",
        "goal_id": "goal_x",
        "statement": "Repository documents invariants",
        "status": "ACTIVE",
        "confidence": "MEDIUM",
        "confidence_basis": "single observation",
        "derived_from_observation_ids": ["obs_001"],
        "recorded_at": now,
    }
    validate(observation, "observation.schema.json")
    validate(belief, "belief.schema.json")
