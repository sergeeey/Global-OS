"""Gated Environment Change Proposal — GOS-I20; no silent runtime rewrite."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.cognition.environment.lifecycle import (
    EnvironmentLifecycle,
    EnvironmentLifecycleError,
    transition,
)
from global_os.common.hashing import new_id
from global_os.contracts.validate import validate
from global_os.runtime.events.ledger import EventLedger


class EnvironmentChangeError(Exception):
    pass


class EnvironmentChangeGate:
    """Propose → sandbox → eval → approve → activate. Authority required for APPROVED+."""

    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._proposals: dict[str, dict[str, Any]] = {}
        self._active_envs: dict[str, dict[str, Any]] = {}

    def register_active(self, environment: dict[str, Any]) -> None:
        validate(environment, "execution_environment.schema.json")
        self._active_envs[environment["id"]] = deepcopy(environment)

    def propose(
        self,
        *,
        environment_id: str,
        proposer: str,
        reason: str,
        diff: dict[str, Any],
        evaluation_plan: str,
        required_authority: list[str],
        expected_gain: str | None = None,
        new_risks: list[str] | None = None,
        tenant_id: str,
        workspace_id: str,
        goal_id: str | None = None,
    ) -> dict[str, Any]:
        if environment_id not in self._active_envs:
            raise EnvironmentChangeError(f"unknown environment: {environment_id}")
        if "id" in diff or "schema_version" in diff:
            raise EnvironmentChangeError("cannot rewrite environment identity via diff")
        proposal: dict[str, Any] = {
            "id": new_id("ecp"),
            "schema_version": "0.1.0",
            "environment_id": environment_id,
            "proposer": proposer,
            "reason": reason,
            "diff": deepcopy(diff),
            "requires_approval": True,
            "lifecycle_state": EnvironmentLifecycle.PROPOSED.value,
            "evaluation_plan": evaluation_plan,
            "required_authority": list(required_authority),
        }
        if expected_gain is not None:
            proposal["expected_gain"] = expected_gain
        if new_risks is not None:
            proposal["new_risks"] = list(new_risks)
        validate(proposal, "environment_change_proposal.schema.json")
        self._proposals[proposal["id"]] = proposal
        self._ledger.append(
            event_type="environment.change_proposed",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=goal_id,
            payload={"proposal_id": proposal["id"], "environment_id": environment_id},
            producer="environment.change_gate",
        )
        return deepcopy(proposal)

    def advance(
        self,
        proposal_id: str,
        new_state: EnvironmentLifecycle,
        *,
        principal_capabilities: list[str],
        tenant_id: str,
        workspace_id: str,
        approval_ref: str | None = None,
    ) -> dict[str, Any]:
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            raise EnvironmentChangeError(f"unknown proposal: {proposal_id}")
        current = EnvironmentLifecycle(proposal["lifecycle_state"])
        try:
            nxt = transition(current, new_state)
        except EnvironmentLifecycleError as exc:
            raise EnvironmentChangeError(str(exc)) from exc

        if nxt in {
            EnvironmentLifecycle.APPROVED,
            EnvironmentLifecycle.ACTIVE,
        }:
            needed = set(proposal["required_authority"])
            if not needed.issubset(set(principal_capabilities)):
                raise EnvironmentChangeError(
                    "insufficient authority for environment promotion (GOS-I20)"
                )
            if nxt == EnvironmentLifecycle.APPROVED and not approval_ref:
                raise EnvironmentChangeError("approval_ref required for APPROVED")
            if approval_ref:
                refs = list(proposal.get("approval_refs", []))
                refs.append(approval_ref)
                proposal["approval_refs"] = refs

        proposal["lifecycle_state"] = nxt.value
        self._ledger.append(
            event_type="environment.lifecycle_transitioned",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            payload={
                "proposal_id": proposal_id,
                "from": current.value,
                "to": nxt.value,
            },
            producer="environment.change_gate",
        )

        if nxt == EnvironmentLifecycle.ACTIVE:
            self._apply_diff(proposal)

        return deepcopy(proposal)

    def _apply_diff(self, proposal: dict[str, Any]) -> None:
        env_id = proposal["environment_id"]
        env = self._active_envs[env_id]
        for key, value in proposal["diff"].items():
            if key in {"id", "schema_version", "goal_id", "task_id"}:
                raise EnvironmentChangeError(f"forbidden diff key: {key}")
            env[key] = deepcopy(value)
        validate(env, "execution_environment.schema.json")

    def get_proposal(self, proposal_id: str) -> dict[str, Any]:
        return deepcopy(self._proposals[proposal_id])

    def get_environment(self, environment_id: str) -> dict[str, Any]:
        return deepcopy(self._active_envs[environment_id])
