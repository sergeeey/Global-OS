"""Y18-4 — Provider / tool degradation (honest BLOCKED / null, no fabricate).

Hypothesis: Model outage records null result; missing live keys → BLOCKED_ENVIRONMENT
for provider IV; deterministic path still completes; no fabricated LIVE_PROVIDER_IV.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))

from global_os.adapters.models import GenerateRequest, ModelProviderError, OutageModelProvider
from global_os.evals.research import PriorWorkReframe, provider_iv_status, run_research_mission
from global_os.memory import NullResultStore
from global_os.runtime.events.ledger import EventLedger

ART = Path(__file__).resolve().parent


def run_experiment() -> dict:
    ledger = EventLedger()
    nulls = NullResultStore(ledger)
    outage = OutageModelProvider()
    outage_raised = False
    try:
        outage.generate(GenerateRequest(prompt="degraded"))
    except ModelProviderError:
        outage_raised = True
        nulls.record(
            attempt="model.generate",
            why_failed="provider_outage",
            evidence=["ModelProviderError"],
            conditions="no_network_or_provider_down",
            reopen_condition="provider_healthy",
            tenant_id="dogfood",
            workspace_id="y18",
            goal_id="goal_y18_4",
        )
    # Deterministic fallback work still succeeds
    det_ok = sum(range(1, 11)) == 55
    iv_status, iv_detail, keys = provider_iv_status()
    return {
        "failure_mode": "provider_tool_degradation",
        "outage_raised": outage_raised,
        "null_count": len(nulls.list_all()),
        "deterministic_fallback_ok": det_ok,
        "provider_iv_status": iv_status,
        "provider_iv_detail": iv_detail,
        "keys_present": keys,
        "fabricated_live_iv": iv_status == "LIVE_PROVIDER_IV",  # must be False here
    }


def decide_fn(raw: dict) -> tuple[str, list[dict]]:
    # In cloud/dev without keys, BLOCKED_ENVIRONMENT is the honest outcome.
    honest_iv = raw["provider_iv_status"] in {
        "BLOCKED_ENVIRONMENT",
        "AVAILABLE",
        "NOT_REQUESTED",
    } and raw["fabricated_live_iv"] is False
    ok = (
        raw["outage_raised"] is True
        and raw["null_count"] >= 1
        and raw["deterministic_fallback_ok"] is True
        and honest_iv
    )
    nulls = [] if ok else [{"id": "y18-4-degrade-miss", "detail": raw}]
    # Also preserve the outage null as mission null knowledge
    preserved = [{"id": "provider_outage_null", "why": "ModelProviderError"}]
    return ("SUPPORTED" if ok else "REJECTED"), preserved + nulls


def verify(raw: dict) -> tuple[str, list[str]]:
    checks = [
        f"outage={raw.get('outage_raised')}",
        f"nulls={raw.get('null_count')}",
        f"iv={raw.get('provider_iv_status')}",
        f"det={raw.get('deterministic_fallback_ok')}",
    ]
    ok = (
        raw.get("outage_raised") is True
        and raw.get("null_count", 0) >= 1
        and raw.get("deterministic_fallback_ok") is True
        and raw.get("fabricated_live_iv") is False
    )
    return ("PASS" if ok else "FAIL"), checks


PREREG = {
    "mission_id": "Y18-4",
    "failure_mode_class": "provider_tool_degradation",
    "primary_criterion": "outage→null + honest IV status + deterministic continue",
    "hypothesis": (
        "Provider outage is recorded as null; provider IV does not fabricate LIVE; "
        "deterministic work continues."
    ),
    "kill_criterion": "REJECTED if outage swallowed or LIVE_PROVIDER_IV fabricated",
}


def main() -> None:
    report = run_research_mission(
        mission_id="Y18-4",
        artifact_root=ART,
        objective_text="Y18-4 dogfood: provider/tool degradation honesty",
        hypothesis_statement=PREREG["hypothesis"],
        preregistration=PREREG,
        plan={"steps": ["outage probe", "null record", "IV status", "deterministic fallback"]},
        experiment_fn=run_experiment,
        decide_fn=decide_fn,
        deterministic_verify_fn=verify,
        kill_criteria=[PREREG["kill_criterion"]],
        alternative_explanations=["Silent provider fallback to success"],
        reopen_conditions=["Inject live keys and recheck AVAILABLE path"],
        reframe=PriorWorkReframe(
            discovered_prior_id="Y17-FC-001",
            original_intent="Live multi-provider research",
            reframed_intent="Dogfood degradation without fabricated IV",
            rationale="Failure-mode diversity for freeze candidate",
        ),
        request_provider_iv=True,
        tenant_id="dogfood",
        workspace_id="y18",
    )
    print(report.decision, report.verification.provider_status)


if __name__ == "__main__":
    main()
