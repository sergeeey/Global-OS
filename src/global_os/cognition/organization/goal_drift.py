"""Goal drift detection — implicit reinterpretation without amendment (GOS-I27)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DriftFinding:
    kind: str
    severity: str
    detail: str
    goal_version: int
    evidence: tuple[str, ...]


# Explore/research language escalating into irreversible execute language.
_EXPLORE = (
    "исследовать",
    "investigate",
    "evaluate",
    "feasibility",
    "possibility",
    "возможность",
    "assess",
)
_EXECUTE = (
    "совершить покупк",
    "execute purchase",
    "buy now",
    "place order",
    "оплатить",
    "sign contract",
    "transfer funds",
    "wire payment",
)


class GoalDriftDetector:
    """Compare GoalContract objective with missions / actions / summaries."""

    def detect(
        self,
        goal: dict[str, Any],
        *,
        missions: list[dict[str, Any]] | None = None,
        action_summaries: list[str] | None = None,
        reasoning_summaries: list[str] | None = None,
    ) -> list[DriftFinding]:
        findings: list[DriftFinding] = []
        objective = str(goal.get("objective", {}).get("text", goal.get("objective", "")))
        obj_l = objective.lower()
        version = int(goal.get("version", 1))
        explore_goal = any(t in obj_l for t in _EXPLORE)
        texts = [objective]
        for m in missions or []:
            texts.append(str(m.get("objective", "")))
        if action_summaries:
            texts.extend(action_summaries)
        if reasoning_summaries:
            texts.extend(reasoning_summaries)
        joined = "\n".join(texts).lower()

        if explore_goal and any(t in joined for t in _EXECUTE):
            # Only flag if execute language appears outside the goal objective itself
            outside = "\n".join(texts[1:]).lower() if len(texts) > 1 else ""
            if any(t in outside for t in _EXECUTE):
                findings.append(
                    DriftFinding(
                        kind="explore_to_execute",
                        severity="high",
                        detail=(
                            "Goal explores/investigates; missions/actions escalate to execute "
                            "without GoalAmendment (GOS-I27)"
                        ),
                        goal_version=version,
                        evidence=tuple(
                            t for t in _EXECUTE if t in outside
                        ),
                    )
                )

        forbidden = {str(x).lower() for x in goal.get("forbidden_outcomes", [])}
        scan_texts = [str(m.get("objective", "")) for m in missions or []]
        if action_summaries:
            scan_texts.extend(action_summaries)
        for text in scan_texts:
            mo = text.lower()
            for f in forbidden:
                if f and f in mo:
                    findings.append(
                        DriftFinding(
                            kind="forbidden_outcome_in_mission",
                            severity="critical",
                            detail=f"mission/action references forbidden_outcome {f!r}",
                            goal_version=version,
                            evidence=(f, mo[:200]),
                        )
                    )
        return findings

    def has_blocking_drift(self, findings: list[DriftFinding]) -> bool:
        return any(f.severity in {"high", "critical"} for f in findings)
