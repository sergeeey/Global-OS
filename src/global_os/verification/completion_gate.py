"""Goal Completion Gate — executable terminal check (not an LLM judge).

Binds Goal Contract success_criteria + EffectReceipts + invariants.
Plans finished ≠ goal achieved (GOS-I08 / GOS-I13).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CompletionStatus(str, Enum):
    ACHIEVED = "ACHIEVED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CompletionDecision:
    status: CompletionStatus
    criteria_met: tuple[str, ...]
    criteria_unmet: tuple[str, ...]
    criteria_unknown: tuple[str, ...]
    invariant_violations: tuple[str, ...]
    authority_ok: bool
    evidence_bound: bool
    reason: str
    llm_used_as_oracle: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "criteria_met": list(self.criteria_met),
            "criteria_unmet": list(self.criteria_unmet),
            "criteria_unknown": list(self.criteria_unknown),
            "invariant_violations": list(self.invariant_violations),
            "authority_ok": self.authority_ok,
            "evidence_bound": self.evidence_bound,
            "reason": self.reason,
            "llm_used_as_oracle": self.llm_used_as_oracle,
        }


def _receipt_supports_criterion(receipt: dict[str, Any], criterion_id: str) -> bool | None:
    """True/False if receipt clearly addresses criterion; None if unrelated."""
    binds = receipt.get("binds_criteria") or receipt.get("success_criteria_ids") or []
    if isinstance(binds, str):
        binds = [binds]
    if criterion_id not in binds and criterion_id not in (
        receipt.get("intended_effect"),
        receipt.get("observed_effect"),
    ):
        # Allow explicit criterion_results map
        results = receipt.get("criterion_results") or {}
        if criterion_id not in results:
            return None
        return bool(results[criterion_id])
    status = str(receipt.get("reconciliation_status") or "")
    world_ok = receipt.get("world_success")
    if world_ok is False or status in {"DISCREPANCY", "ESCALATION_REQUIRED"}:
        return False
    if status == "OBSERVATION_PENDING":
        return None
    if world_ok is True or status == "RECONCILED":
        return True
    # tool_response.success alone is never enough (GOS-I13)
    tr = receipt.get("tool_response") or {}
    if tr.get("success") is True and world_ok is None and status not in {"RECONCILED"}:
        return None
    return None


def _apply_falsification(
    *,
    met: list[str],
    unmet: list[str],
    unknown_ids: list[str],
    falsification_results: dict[str, Any] | None,
) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    """Apply active counterexamples. Absence of falsify never upgrades unknown→met."""
    falsified_ids: list[str] = []
    unobservable_ids: list[str] = []
    if not falsification_results:
        return met, unmet, unknown_ids, falsified_ids, unobservable_ids

    for cid, raw in falsification_results.items():
        if not isinstance(raw, dict):
            continue
        outcome = str(raw.get("outcome") or "")
        if outcome == "falsified":
            falsified_ids.append(cid)
            if cid in met:
                met.remove(cid)
            if cid in unknown_ids:
                unknown_ids.remove(cid)
            if cid not in unmet:
                unmet.append(cid)
        elif outcome == "unobservable":
            unobservable_ids.append(cid)
            if cid in met:
                met.remove(cid)
                if cid not in unknown_ids:
                    unknown_ids.append(cid)
        # not_falsified: no upgrade of unknown/unmet → met
    return met, unmet, unknown_ids, falsified_ids, unobservable_ids


def evaluate_goal_completion(
    *,
    goal: dict[str, Any],
    effect_receipts: list[dict[str, Any]] | None = None,
    criterion_checks: dict[str, bool | None] | None = None,
    invariant_break_flags: list[str] | None = None,
    authority_expanded: bool = False,
    forbidden_outcomes_observed: list[str] | None = None,
    llm_completion_claim: str | None = None,
    falsification_results: dict[str, Any] | None = None,
    substrate_status: str | None = None,
) -> CompletionDecision:
    """Decide ACHIEVED/PARTIAL/FAILED/UNKNOWN from executable evidence only.

    ``llm_completion_claim`` is ignored for the decision (recorded as non-oracle).
    ``falsification_results`` actively seek counterexamples before SUCCESS.
    ``substrate_status`` ``UNHEALTHY`` forbids ACHIEVED (ENVIRONMENT_GAP).
    """
    del llm_completion_claim  # never sole oracle
    criteria = list(goal.get("success_criteria") or [])
    if not criteria:
        return CompletionDecision(
            status=CompletionStatus.UNKNOWN,
            criteria_met=(),
            criteria_unmet=(),
            criteria_unknown=(),
            invariant_violations=("missing_success_criteria",),
            authority_ok=not authority_expanded,
            evidence_bound=False,
            reason="no_success_criteria",
        )

    checks = dict(criterion_checks or {})
    receipts = list(effect_receipts or [])
    for crit in criteria:
        cid = str(crit.get("id") or "")
        if not cid or cid in checks:
            continue
        # Aggregate receipt evidence for this criterion
        votes: list[bool] = []
        unknown = False
        for rec in receipts:
            v = _receipt_supports_criterion(rec, cid)
            if v is True:
                votes.append(True)
            elif v is False:
                votes.append(False)
            elif v is None and (
                cid in (rec.get("binds_criteria") or [])
                or cid in (rec.get("criterion_results") or {})
            ):
                unknown = True
        if votes:
            checks[cid] = all(votes)
        elif unknown:
            checks[cid] = None
        else:
            checks[cid] = None

    met: list[str] = []
    unmet: list[str] = []
    unknown_ids: list[str] = []
    for crit in criteria:
        cid = str(crit.get("id") or "")
        val = checks.get(cid)
        if val is True:
            met.append(cid)
        elif val is False:
            unmet.append(cid)
        else:
            unknown_ids.append(cid)

    met, unmet, unknown_ids, falsified_ids, unobservable_ids = _apply_falsification(
        met=met,
        unmet=unmet,
        unknown_ids=unknown_ids,
        falsification_results=falsification_results,
    )

    violations = list(invariant_break_flags or [])
    forbidden = list(forbidden_outcomes_observed or [])
    for f in forbidden:
        violations.append(f"forbidden_outcome:{f}")
    authority_ok = not authority_expanded
    if authority_expanded:
        violations.append("authority_expanded")

    evidence_bound = (
        bool(receipts)
        or bool(criterion_checks)
        or bool(falsification_results)
    )

    substrate_unhealthy = str(substrate_status or "").upper() == "UNHEALTHY"

    if violations or not authority_ok:
        status = CompletionStatus.FAILED
        reason = "invariant_or_authority_violation"
    elif unmet and not met and not unknown_ids:
        status = CompletionStatus.FAILED
        reason = (
            f"criterion_falsified:{falsified_ids[0]}"
            if falsified_ids
            else "all_criteria_failed"
        )
    elif unmet and met:
        status = CompletionStatus.PARTIAL
        reason = (
            f"criterion_falsified:{falsified_ids[0]}"
            if falsified_ids
            else "some_criteria_unmet"
        )
    elif unknown_ids and not unmet and met:
        status = CompletionStatus.PARTIAL
        reason = (
            "falsification_unobservable"
            if unobservable_ids
            else "some_criteria_unknown"
        )
    elif unknown_ids and not met and not unmet:
        status = CompletionStatus.UNKNOWN
        reason = (
            "falsification_unobservable"
            if unobservable_ids
            else "insufficient_evidence"
        )
    elif met and not unmet and not unknown_ids:
        status = CompletionStatus.ACHIEVED
        reason = "all_criteria_verified"
    else:
        status = CompletionStatus.PARTIAL
        reason = "mixed_or_incomplete"

    # Unhealthy verification procedure cannot certify SUCCESS.
    if substrate_unhealthy and status == CompletionStatus.ACHIEVED:
        status = CompletionStatus.UNKNOWN
        reason = "ENVIRONMENT_GAP:verification_substrate_unhealthy"
    elif substrate_unhealthy and status == CompletionStatus.PARTIAL and not unmet:
        reason = "ENVIRONMENT_GAP:verification_substrate_unhealthy"

    return CompletionDecision(
        status=status,
        criteria_met=tuple(met),
        criteria_unmet=tuple(unmet),
        criteria_unknown=tuple(unknown_ids),
        invariant_violations=tuple(violations),
        authority_ok=authority_ok,
        evidence_bound=evidence_bound,
        reason=reason,
        llm_used_as_oracle=False,
    )
