"""Y18-2 — External effect discrepancy / recovery (GOS-I13/I22).

Hypothesis: Tool success ≠ world effect; discrepancy surfaces; retry with same
idempotency key does not double material side-effect.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))

from global_os.common.hashing import new_id
from global_os.evals.research import PriorWorkReframe, run_research_mission
from global_os.kernel.action_gateway import ToolGateway, ToolResult
from global_os.runtime.events.ledger import EventLedger

ART = Path(__file__).resolve().parent


def run_experiment() -> dict:
    ledger = EventLedger()
    gateway = ToolGateway(ledger)
    calls = {"n": 0}

    def lying_tool(_proposal: dict) -> ToolResult:
        calls["n"] += 1
        return ToolResult(success=True, payload={"claimed": "paid"})

    gateway.register_tool("payment.fake", lying_tool)
    proposal = {
        "idempotency_key": "idem_y18_2",
        "goal_id": "goal_y18_2",
        "principal_id": "wkr_y18",
    }
    t1, t2 = new_id("tok"), new_id("tok")
    gateway.accept_token(t1)
    gateway.accept_token(t2)
    r1 = gateway.execute(
        tool_id="payment.fake",
        proposal=proposal,
        execution_token=t1,
        tenant_id="dogfood",
        workspace_id="y18",
        intended_effect="invoice_paid",
        observation={"effect": "invoice_still_unpaid"},
    )
    r2 = gateway.execute(
        tool_id="payment.fake",
        proposal=proposal,
        execution_token=t2,
        tenant_id="dogfood",
        workspace_id="y18",
        intended_effect="invoice_paid",
        observation={"effect": "invoice_still_unpaid"},
    )
    return {
        "failure_mode": "effect_discrepancy_idempotency",
        "tool_claimed_success": r1["tool_response"]["success"] is True,
        "discrepancy": r1.get("discrepancy"),
        "reconciliation_status": r1.get("reconciliation_status"),
        "handler_calls": calls["n"],
        "same_receipt": r1["receipt_id"] == r2["receipt_id"],
        "receipt_ids": [r1["receipt_id"], r2["receipt_id"]],
    }


def decide_fn(raw: dict) -> tuple[str, list[dict]]:
    ok = (
        raw["tool_claimed_success"] is True
        and raw["discrepancy"] not in (None, "none", "")
        and raw["handler_calls"] == 1
        and raw["same_receipt"] is True
    )
    nulls = [] if ok else [{"id": "y18-2-effect-miss", "detail": raw}]
    return ("SUPPORTED" if ok else "REJECTED"), nulls


def verify(raw: dict) -> tuple[str, list[str]]:
    checks = [
        f"calls={raw.get('handler_calls')}",
        f"discrepancy={raw.get('discrepancy')}",
        f"same_receipt={raw.get('same_receipt')}",
    ]
    ok = raw.get("handler_calls") == 1 and raw.get("same_receipt") is True
    return ("PASS" if ok else "FAIL"), checks


PREREG = {
    "mission_id": "Y18-2",
    "failure_mode_class": "external_effect_recovery",
    "primary_criterion": "discrepancy surfaced + idempotent no double effect",
    "hypothesis": (
        "False tool success yields discrepancy; duplicate idempotency key does not "
        "re-invoke material handler."
    ),
    "kill_criterion": "REJECTED if handler_calls!=1 or discrepancy missing",
}


def main() -> None:
    report = run_research_mission(
        mission_id="Y18-2",
        artifact_root=ART,
        objective_text="Y18-2 dogfood: effect discrepancy + idempotent recovery",
        hypothesis_statement=PREREG["hypothesis"],
        preregistration=PREREG,
        plan={"steps": ["lying tool", "observe unpaid", "retry same idempotency"]},
        experiment_fn=run_experiment,
        decide_fn=decide_fn,
        deterministic_verify_fn=verify,
        kill_criteria=[PREREG["kill_criterion"]],
        alternative_explanations=["Gateway silently trusts tool success"],
        reopen_conditions=["Add EffectReconciliation escalation path check"],
        reframe=PriorWorkReframe(
            discovered_prior_id="GOS-I13",
            original_intent="Payment automation",
            reframed_intent="Dogfood effect receipt discrepancy",
            rationale="Failure-mode diversity for freeze candidate",
        ),
        request_provider_iv=False,
        tenant_id="dogfood",
        workspace_id="y18",
    )
    print(report.decision, report.verification.as_dict() if hasattr(report, "verification") else "")


if __name__ == "__main__":
    main()
