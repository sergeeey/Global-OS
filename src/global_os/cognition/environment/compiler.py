"""EnvironmentCompiler — Goal + OrgUnit → typed ExecutionEnvironment (ADR-0003)."""

from __future__ import annotations

from typing import Any

from global_os.common.hashing import new_id
from global_os.contracts.validate import validate


class EnvironmentCompilerError(Exception):
    pass


class EnvironmentCompiler:
    """v0: deterministic compile from goal authority + org unit + task.

    Does not call models. Does not expand authority beyond parent capabilities.
    """

    def compile(
        self,
        *,
        goal: dict[str, Any],
        org_unit: dict[str, Any],
        task: dict[str, Any],
        verification_tier: int = 1,
        sandbox_profile: str = "process_local",
    ) -> dict[str, Any]:
        goal_caps = list(goal.get("authority", {}).get("capabilities", []))
        org_caps = list(org_unit.get("authority", {}).get("capabilities", []))
        if not set(org_caps).issubset(set(goal_caps)):
            raise EnvironmentCompilerError("org capabilities must be ⊆ goal (GOS-I04)")

        budget = org_unit.get("budget", {"usd": 0, "tokens": 0})
        tokens = int(budget.get("tokens", 0))
        usd = float(budget.get("usd", 0))

        env: dict[str, Any] = {
            "id": new_id("env"),
            "schema_version": "0.1.0",
            "task_id": task["task_id"],
            "org_unit_id": org_unit["id"],
            "goal_id": goal["goal_id"],
            "model_requirements": {
                "reasoning": "medium",
                "vision": False,
                "coding": task.get("title") in {"implementation", "testing", "runtime"},
                "tool_use": True,
            },
            "reasoning_budget": {
                "requested": {
                    "tokens": min(tokens, max(tokens // 2, 1)) if tokens else 0,
                    "usd": usd / 2 if usd else 0,
                    "wall_time_seconds": 600,
                },
                "maximum": {
                    "tokens": tokens,
                    "usd": usd,
                    "wall_time_seconds": 1800,
                },
                "policy_source": "org_unit",
            },
            "tools": {"allow": org_caps},
            "sandbox": {"profile": sandbox_profile},
            "retrieval": {"strategy": "hybrid"},
            "memory": {"scopes": ["episodic", "negative"]},
            "context": {
                "token_budget": min(tokens, 12000) if tokens else 4000,
                "freshness": {"max_age": "7d", "prefer_verified": True},
                "include_refs": ["goal_contract", task["task_id"]],
            },
            "clarification": {
                "materiality_policy": "high_impact_only",
                "ask_when": ["authority_gap", "irreversible_action"],
                "max_rounds": 2,
            },
            "verification": {"required_tier": verification_tier},
            "output_contract": org_unit.get("output_contract", "artifact_and_evidence"),
        }
        validate(env, "execution_environment.schema.json")
        return env
