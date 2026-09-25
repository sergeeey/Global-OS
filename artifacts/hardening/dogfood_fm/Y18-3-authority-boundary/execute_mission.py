"""Y18-3 — Authority boundary (GOS-I01/I03/I04).

Hypothesis: Default-deny blocks ungranted capability; child grant cannot exceed parent;
unauthorized execute path does not mint usable world effect.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))

from global_os.evals.research import PriorWorkReframe, run_research_mission
from global_os.kernel.authority import AuthorityKernel, Decision
from global_os.runtime.events.ledger import EventLedger

ART = Path(__file__).resolve().parent


def _proposal(*, capability: str, caps: list[str], pid: str = "worker_y18") -> dict:
    return {
        "proposal_id": f"ap_{capability.replace('.', '_')}_{pid}",
        "schema_version": "0.1.0",
        "principal_id": pid,
        "goal_id": "goal_y18_3",
        "capability": capability,
        "resource": "res://y18",
        "intended_effect": "probe",
        "maximum_effect": "probe",
        "reversible": True,
        "information_disclosure": "none",
        "monetary_cost": 0,
        "idempotency_key": f"idem_{capability.replace('.', '_')}_{pid}_xx",
        "evidence_refs": [],
        "approval_refs": [],
        "context": {},
        "parent_capabilities": caps,
    }


def run_experiment() -> dict:
    ledger = EventLedger()
    auth = AuthorityKernel(ledger)
    auth.grant(
        principal_id="mgr_y18",
        capabilities={"filesystem.read", "research.compute"},
        tenant_id="dogfood",
        workspace_id="y18",
    )
    # Child ⊆ parent OK
    child_ok = True
    try:
        auth.grant(
            principal_id="worker_y18",
            capabilities={"filesystem.read"},
            tenant_id="dogfood",
            workspace_id="y18",
            parent_id="mgr_y18",
        )
    except ValueError:
        child_ok = False
    # Child expansion must fail
    expand_denied = False
    try:
        auth.grant(
            principal_id="worker_bad",
            capabilities={"filesystem.read", "email.send"},
            tenant_id="dogfood",
            workspace_id="y18",
            parent_id="mgr_y18",
        )
    except ValueError:
        expand_denied = True
    # Default deny for ungranted capability
    deny = auth.decide(
        _proposal(capability="email.send", caps=["filesystem.read"]),
        tenant_id="dogfood",
        workspace_id="y18",
    )
    allow = auth.decide(
        _proposal(capability="filesystem.read", caps=["filesystem.read"], pid="worker_y18"),
        tenant_id="dogfood",
        workspace_id="y18",
    )
    return {
        "failure_mode": "authority_boundary",
        "child_subset_ok": child_ok,
        "child_expand_denied": expand_denied,
        "ungranted_decision": deny.decision.value,
        "granted_decision": allow.decision.value,
        "ungranted_has_token": deny.execution_token is not None,
        "granted_has_token": allow.execution_token is not None,
    }


def decide_fn(raw: dict) -> tuple[str, list[dict]]:
    ok = (
        raw["child_subset_ok"] is True
        and raw["child_expand_denied"] is True
        and raw["ungranted_decision"] == Decision.DENY.value
        and raw["granted_decision"] == Decision.ALLOW.value
        and raw["ungranted_has_token"] is False
        and raw["granted_has_token"] is True
    )
    nulls = [] if ok else [{"id": "y18-3-auth-miss", "detail": raw}]
    return ("SUPPORTED" if ok else "REJECTED"), nulls


def verify(raw: dict) -> tuple[str, list[str]]:
    checks = [
        f"deny={raw.get('ungranted_decision')}",
        f"allow={raw.get('granted_decision')}",
        f"expand_denied={raw.get('child_expand_denied')}",
    ]
    ok = (
        raw.get("ungranted_decision") == "DENY"
        and raw.get("granted_decision") == "ALLOW"
        and raw.get("child_expand_denied") is True
    )
    return ("PASS" if ok else "FAIL"), checks


PREREG = {
    "mission_id": "Y18-3",
    "failure_mode_class": "authority_boundary",
    "primary_criterion": "default-deny + child ⊆ parent",
    "hypothesis": (
        "AuthorityKernel denies ungranted capabilities, refuses child expansion "
        "beyond parent, and mints tokens only on ALLOW."
    ),
    "kill_criterion": "REJECTED if DENY missing or child expansion allowed",
}


def main() -> None:
    report = run_research_mission(
        mission_id="Y18-3",
        artifact_root=ART,
        objective_text="Y18-3 dogfood: authority default-deny and GOS-I04",
        hypothesis_statement=PREREG["hypothesis"],
        preregistration=PREREG,
        plan={"steps": ["grant parent", "child subset", "deny expand", "decide"]},
        experiment_fn=run_experiment,
        decide_fn=decide_fn,
        deterministic_verify_fn=verify,
        kill_criteria=[PREREG["kill_criterion"]],
        alternative_explanations=["Policy engine silent allow"],
        reopen_conditions=["Add approval-required path"],
        reframe=PriorWorkReframe(
            discovered_prior_id="GOS-I01/I04",
            original_intent="Delegate email to worker",
            reframed_intent="Dogfood authority boundary invariants",
            rationale="Failure-mode diversity for freeze candidate",
        ),
        request_provider_iv=False,
        tenant_id="dogfood",
        workspace_id="y18",
    )
    print(report.decision)


if __name__ == "__main__":
    main()
