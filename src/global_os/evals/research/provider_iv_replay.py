"""Provider-IV replay for completed research missions.

Recurring failure: Y17-FC-IV / BLOCKED_ENVIRONMENT in cloud.
This module does NOT fabricate provider success. When free keys are absent,
it records an honest verification_delta with status BLOCKED_ENVIRONMENT.

When ≥2 free providers are available, runs IndependentVerificationStack judges
(GOS-I10) over locked claim+evidence payloads and writes the delta.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from global_os.adapters.models.factory import (
    free_live_ready,
    live_keys_present,
    open_model_provider,
)
from global_os.adapters.models.pins import GEMINI_FLASH, GROQ_VERIFIER, OPENROUTER_REASONER
from global_os.verification.diversity import assess_diversity
from global_os.verification.independent_stack import IndependentVerificationStack
from global_os.verification.multi_provider import make_provider_judge
from global_os.verification.router import VerificationTier

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_MISSIONS = (
    ROOT / "artifacts" / "y17" / "Y17-1-HB2-1n-confirmatory",
    ROOT / "artifacts" / "y17" / "Y17-2-HCAT31-V3-variance-models",
)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _as_dict(payload: Any) -> dict[str, Any]:
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def mission_payload(mission_root: Path) -> dict[str, Any]:
    """Build claim/evidence payload from locked mission artifacts (no recompute)."""
    claims = _as_dict(_read_json(mission_root / "claims.json"))
    prereg = _as_dict(_read_json(mission_root / "preregistration.json"))
    verification = _as_dict(_read_json(mission_root / "verification.json"))
    metrics = _as_dict(_read_json(mission_root / "experiments" / "metrics" / "run.json"))
    summary = _as_dict(_read_json(mission_root / "experiments" / "metrics" / "run_summary.json"))
    mission = _as_dict(_read_json(mission_root / "mission.json"))

    decision_str = str(claims.get("decision") or mission.get("decision") or "UNKNOWN")
    hypothesis = str(
        claims.get("statement")
        or prereg.get("hypothesis")
        or prereg.get("statement")
        or mission_root.name
    )
    evidence = {
        "decision": decision_str,
        "prereg_primary": prereg.get("primary_criterion") or prereg.get("primary"),
        "deterministic_verification": verification,
        "metrics_keys": sorted(metrics.keys())[:30],
        "summary": summary
        if summary
        else {k: metrics.get(k) for k in ("decision", "primary", "config")},
    }
    before = verification.get("provider_status")
    indep = verification.get("independent_provider")
    if before is None and isinstance(indep, dict):
        before = indep.get("status")
    return {
        "mission_id": mission.get("mission_id") or mission_root.name,
        "claim": (
            f"Mission decision {decision_str} is consistent with preregistered "
            f"criterion for: {hypothesis}"
        ),
        "evidence": evidence,
        "expected": (
            "PASS if decision matches locked primary criterion; "
            "FAIL if inconsistent or fabricated"
        ),
        "before_provider_status": before or "UNKNOWN",
        "decision_md_present": (mission_root / "decision.md").exists(),
    }


def free_provider_pair() -> list[tuple[str, str, Any]]:
    """Return up to two distinct free live providers (name, family, provider)."""
    keys = live_keys_present()
    out: list[tuple[str, str, Any]] = []
    if keys["openrouter"]:
        out.append(("openrouter", "nemotron", open_model_provider("openrouter", model=OPENROUTER_REASONER)))
    if keys["groq"]:
        out.append(("groq", "gpt_oss", open_model_provider("groq", model=GROQ_VERIFIER)))
    if keys["gemini"] and len(out) < 2:
        out.append(("gemini", "gemini_flash", open_model_provider("gemini", model=GEMINI_FLASH)))
    return out[:2]


def run_provider_iv(payload: dict[str, Any]) -> dict[str, Any]:
    keys = live_keys_present()
    if not free_live_ready():
        return {
            "status": "BLOCKED_ENVIRONMENT",
            "detail": "no OPENROUTER/GROQ/GEMINI keys — provider IV not simulated",
            "live_keys": keys,
            "diversity": assess_diversity(()).reason,
            "stack_result": None,
        }
    pair = free_provider_pair()
    if len(pair) < 2:
        return {
            "status": "DEGRADED_SINGLE_PROVIDER",
            "detail": "only one free provider key — GOS-I10 independent IV requires ≥2 families",
            "live_keys": keys,
            "providers_available": [p[0] for p in pair],
            "stack_result": None,
            "note": "Do not treat single-provider judge as independent verification",
        }
    methods = [
        make_provider_judge(
            pair[0][2],
            method_id=f"iv_{pair[0][0]}",
            provider_name=pair[0][0],
            model_family=pair[0][1],
            diversity_axis="different_provider",
        ),
        make_provider_judge(
            pair[1][2],
            method_id=f"iv_{pair[1][0]}",
            provider_name=pair[1][0],
            model_family=pair[1][1],
            diversity_axis="different_model_family",
        ),
    ]
    stack = IndependentVerificationStack(methods)
    result = stack.verify(
        {
            "claim": payload["claim"],
            "evidence": payload["evidence"],
            "expected": payload["expected"],
        },
        required_tier=VerificationTier.INDEPENDENT.value,
    )
    return {
        "status": "LIVE_PROVIDER_IV",
        "detail": "≥2 free providers judged claim vs locked evidence",
        "live_keys": keys,
        "providers_used": [p[0] for p in pair],
        "stack_result": {
            "passed": result.passed,
            "consensus": result.consensus,
            "diversity_factors": list(result.diversity_factors),
            "method_results": [
                {"method_id": m.method_id, "passed": m.passed, "details": m.details}
                for m in result.method_results
            ],
        },
    }


def replay_mission(mission_root: Path) -> dict[str, Any]:
    payload = mission_payload(mission_root)
    after = run_provider_iv(payload)
    delta = {
        "mission_id": payload["mission_id"],
        "mission_root": str(mission_root),
        "recorded_at": _now(),
        "before": {
            "provider_status": payload["before_provider_status"],
        },
        "after": after,
        "delta": {
            "status_changed": payload["before_provider_status"] != after["status"],
            "unblocked": (
                payload["before_provider_status"] == "BLOCKED_ENVIRONMENT"
                and after["status"] == "LIVE_PROVIDER_IV"
            ),
            "still_blocked": after["status"] == "BLOCKED_ENVIRONMENT",
            "scientific_decision_recomputed": False,
            "note": "Provider IV replay does not alter scientific decision artifacts",
        },
        "claim_preview": payload["claim"][:240],
    }
    out_path = mission_root / "verification_delta.json"
    _write_json(out_path, delta)
    return delta


def replay_default_missions(
    missions: tuple[Path, ...] = DEFAULT_MISSIONS,
) -> dict[str, Any]:
    results = [replay_mission(m) for m in missions if m.exists()]
    summary = {
        "recorded_at": _now(),
        "n_missions": len(results),
        "any_live_iv": any(r["after"]["status"] == "LIVE_PROVIDER_IV" for r in results),
        "all_still_blocked": all(r["delta"]["still_blocked"] for r in results),
        "results": results,
        "operator_note": (
            "To unblock: set OPENROUTER_API_KEY and/or GROQ_API_KEY and/or GEMINI_API_KEY "
            "locally (≥2 preferred), then re-run: "
            "PYTHONPATH=src python3 -m global_os.evals.research.provider_iv_replay"
        ),
    }
    summary_path = ROOT / "artifacts" / "hardening" / "provider_iv_replay_summary.json"
    _write_json(summary_path, summary)
    return summary


def main() -> None:
    summary = replay_default_missions()
    print(
        json.dumps(
            {
                "n": summary["n_missions"],
                "any_live_iv": summary["any_live_iv"],
                "all_still_blocked": summary["all_still_blocked"],
                "statuses": [r["after"]["status"] for r in summary["results"]],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
