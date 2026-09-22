"""Reusable research mission orchestration — thin layer over existing primitives.

Goal → Hypothesis → Preregistration → Plan → Experiment → Evidence → NullResult
→ Verification (deterministic + optional provider) → Decision → Postmortem.

Degraded verification: missing live providers ⇒ BLOCKED_ENVIRONMENT, not fabricated success.
Prior-work reframe is an explicit mission step (Y17-FC-003), not silent overwrite.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from global_os.adapters.models.factory import free_live_ready, live_keys_present
from global_os.common.hashing import new_id
from global_os.epistemic.hypotheses import HypothesisState, HypothesisStore
from global_os.runtime.events.ledger import EventLedger
from global_os.runtime.goals.store import GoalStore

Decision = str  # SUPPORTED | WEAKENED | REJECTED | INCONCLUSIVE


@dataclass
class PriorWorkReframe:
    discovered_prior_id: str
    original_intent: str
    reframed_intent: str
    rationale: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VerificationBundle:
    deterministic_status: str
    deterministic_checks: list[str] = field(default_factory=list)
    provider_status: str = "NOT_REQUESTED"
    provider_detail: str = ""
    live_keys: dict[str, bool] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchMissionReport:
    mission_id: str
    artifact_root: str
    decision: Decision
    goal_id: str
    hypothesis_id: str
    verification: VerificationBundle
    reframe: PriorWorkReframe | None = None
    null_results: list[dict[str, Any]] = field(default_factory=list)
    failure_cases: list[dict[str, Any]] = field(default_factory=list)
    scientific_claim_accepted: bool = False
    recorded_at: str = ""

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if self.reframe is None:
            d["reframe"] = None
        return d


class ResearchMissionError(Exception):
    pass


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def provider_iv_status() -> tuple[str, str, dict[str, bool]]:
    """Return (status, detail, keys_present). Never fabricates provider success."""
    keys = live_keys_present()
    if free_live_ready():
        return "AVAILABLE", "at least one free live provider key present", keys
    return (
        "BLOCKED_ENVIRONMENT",
        "no OPENROUTER/GROQ/GEMINI keys — deterministic verification only",
        keys,
    )


def run_research_mission(
    *,
    mission_id: str,
    artifact_root: Path,
    objective_text: str,
    hypothesis_statement: str,
    preregistration: dict[str, Any],
    plan: dict[str, Any],
    experiment_fn: Callable[[], dict[str, Any]],
    decide_fn: Callable[[dict[str, Any]], tuple[Decision, list[dict[str, Any]]]],
    deterministic_verify_fn: Callable[[dict[str, Any]], tuple[str, list[str]]],
    kill_criteria: list[str],
    alternative_explanations: list[str],
    reopen_conditions: list[str],
    sources: dict[str, Any] | None = None,
    reframe: PriorWorkReframe | None = None,
    tenant_id: str = "research",
    workspace_id: str = "dogfood",
    request_provider_iv: bool = True,
) -> ResearchMissionReport:
    """Orchestrate one research mission. Does not invent evidence or provider IV."""
    if "primary_criterion" not in preregistration and "primary" not in preregistration:
        raise ResearchMissionError("preregistration must include primary criterion before compute")

    root = Path(artifact_root)
    root.mkdir(parents=True, exist_ok=True)
    ledger = EventLedger()
    goals = GoalStore(ledger)
    hyps = HypothesisStore(ledger)

    goal = goals.create(
        {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "objective": {"text": objective_text},
            "success_criteria": [
                {
                    "id": "sc_decision",
                    "description": "Emit SUPPORTED/WEAKENED/REJECTED/INCONCLUSIVE with artifacts",
                }
            ],
            "invariants": [
                "Do not fabricate provider verification",
                "Preserve null results",
                "Preregistration locked before experiment",
            ],
            "non_goals": ["Rewrite prior scientific corpus", "Claim PRODUCTION_PROVEN"],
            "forbidden_outcomes": ["Silent upgrade of exploratory result to confirmation"],
            "risk": {"tolerance": "low", "maximum_irreversibility": "low"},
            "authority": {
                "delegation_depth_max": 2,
                "capabilities": ["research.read", "research.compute"],
            },
        }
    )

    hyp = hyps.propose(
        goal_id=goal["goal_id"],
        statement=hypothesis_statement,
        kill_criteria=kill_criteria,
        alternative_explanations=alternative_explanations,
        reopen_conditions=reopen_conditions,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
    )
    hyp = hyps.activate(hyp.hypothesis_id, tenant_id=tenant_id, workspace_id=workspace_id)

    mission_doc = {
        "mission_id": mission_id,
        "goal_id": goal["goal_id"],
        "hypothesis_id": hyp.hypothesis_id,
        "status": "RUNNING",
        "reframe": reframe.as_dict() if reframe else None,
        "created_at": _now(),
    }
    _write(root / "mission.json", mission_doc)
    _write(root / "preregistration.json", preregistration)
    _write(root / "plan.json", plan)
    if sources is not None:
        _write(root / "sources.json", sources)
    if reframe is not None:
        _write(root / "reframe.json", reframe.as_dict())

    exp_dir = root / "experiments"
    exp_dir.mkdir(exist_ok=True)
    raw = experiment_fn()
    _write(exp_dir / "metrics" / "run.json", raw)

    decision, nulls = decide_fn(raw)
    _write(root / "null_results.json", {"preserved_nulls": nulls, "rule": "GOS-I11"})
    # Promote optional experiment fields to top-level artifacts (Y17-2 lesson).
    if isinstance(raw, dict) and raw.get("contradictory_evidence") is not None:
        _write(root / "contradictory_evidence.json", raw["contradictory_evidence"])
    if isinstance(raw, dict) and raw.get("independent_verification_status") is not None:
        _write(
            root / "independent_verification_status.json",
            raw["independent_verification_status"],
        )

    det_status, det_checks = deterministic_verify_fn(raw)
    prov_status, prov_detail, keys = ("NOT_REQUESTED", "", live_keys_present())
    failure_cases: list[dict[str, Any]] = []
    if request_provider_iv:
        prov_status, prov_detail, keys = provider_iv_status()
        if prov_status == "BLOCKED_ENVIRONMENT":
            failure_cases.append(
                {
                    "id": f"{mission_id}-FC-IV",
                    "class": "ENVIRONMENT_GAP",
                    "title": "provider independent verification blocked",
                    "detail": prov_detail,
                }
            )

    verification = VerificationBundle(
        deterministic_status=det_status,
        deterministic_checks=det_checks,
        provider_status=prov_status,
        provider_detail=prov_detail,
        live_keys=keys,
    )
    _write(root / "verification.json", verification.as_dict())

    outcome_map = {
        "SUPPORTED": HypothesisState.SUPPORTED,
        "WEAKENED": HypothesisState.INCONCLUSIVE,  # store closest; decision text keeps WEAKENED
        "REJECTED": HypothesisState.KILLED,
        "INCONCLUSIVE": HypothesisState.INCONCLUSIVE,
    }
    if decision not in outcome_map:
        raise ResearchMissionError(f"invalid decision {decision!r}")
    hyps.resolve(
        hyp.hypothesis_id,
        outcome_map[decision],
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        null_result=bool(nulls),
    )

    claims = {
        "goal_id": goal["goal_id"],
        "hypothesis_id": hyp.hypothesis_id,
        "statement": hypothesis_statement,
        "decision": decision,
        "scientific_claim_accepted": False,
    }
    _write(root / "claims.json", claims)

    decision_md = (
        f"# Decision — {mission_id}\n\n"
        f"**{decision}**\n\n"
        f"Deterministic verification: `{det_status}`\n\n"
        f"Provider IV: `{prov_status}` — {prov_detail}\n\n"
        f"scientific_claim_accepted: false\n"
    )
    _write(root / "decision.md", decision_md)

    postmortem = {
        "real_evidence_found": decision != "INCONCLUSIVE",
        "sources_invented": False,
        "null_results_preserved": True,
        "provider_iv": prov_status,
        "reframe_applied": reframe is not None,
        "decision": decision,
        "deterministic_verification": det_status,
        "contradictory_evidence_recorded": bool(
            isinstance(raw, dict) and raw.get("contradictory_evidence")
        ),
        "recorded_at": _now(),
    }
    _write(root / "postmortem.json", postmortem)
    _write(root / "failure_cases.json", failure_cases)

    mission_doc["status"] = "COMPLETED"
    mission_doc["decision"] = decision
    mission_doc["completed_at"] = _now()
    _write(root / "mission.json", mission_doc)

    files = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
    _write(
        root / "run_manifest.json",
        {
            "mission_id": mission_id,
            "decision": decision,
            "files": files,
            "recorded_at": _now(),
            "report_id": new_id("rmr"),
        },
    )

    return ResearchMissionReport(
        mission_id=mission_id,
        artifact_root=str(root),
        decision=decision,
        goal_id=goal["goal_id"],
        hypothesis_id=hyp.hypothesis_id,
        verification=verification,
        reframe=reframe,
        null_results=nulls,
        failure_cases=failure_cases,
        scientific_claim_accepted=False,
        recorded_at=_now(),
    )
