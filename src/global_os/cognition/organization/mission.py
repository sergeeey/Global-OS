"""Mission / Outcome Contract assignment — outcome-first, not microsteps."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.common.hashing import new_id
from global_os.contracts.validate import validate
from global_os.runtime.events.ledger import EventLedger


class MissionError(Exception):
    pass


_MICROSTEP_MARKERS = (
    "открой ",
    "open google",
    "click ",
    "then open",
    "step 1",
    "шаг 1",
)


class MissionAssigner:
    """Assign MissionContract to an OrgUnit. Local autonomy for how; not how-to prompts."""

    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._missions: dict[str, dict[str, Any]] = {}

    def assign(
        self,
        *,
        org_unit: dict[str, Any],
        objective: str,
        success_criteria: list[str],
        evidence_required: list[str],
        constraints: list[str] | None = None,
        output_contract: str | None = None,
        tenant_id: str,
        workspace_id: str,
    ) -> dict[str, Any]:
        lowered = objective.lower()
        if any(m in lowered for m in _MICROSTEP_MARKERS):
            raise MissionError("mission must be outcome-level, not microsteps")
        org_caps = list(org_unit.get("authority", {}).get("capabilities", []))
        budget = org_unit.get("budget", {"usd": 0, "tokens": 0})
        mission: dict[str, Any] = {
            "id": new_id("msn"),
            "schema_version": "0.1.0",
            "org_unit_id": org_unit["id"],
            "goal_id": org_unit["goal_id"],
            "objective": objective,
            "success_criteria": list(success_criteria),
            "constraints": list(constraints or []),
            "evidence_required": list(evidence_required),
            "authority": {"capabilities": org_caps},
            "budget": {
                "usd": float(budget.get("usd", 0)),
                "tokens": int(budget.get("tokens", 0)),
            },
            "output_contract": output_contract or org_unit.get(
                "output_contract", "artifact_and_evidence"
            ),
        }
        validate(mission, "mission_contract.schema.json")
        # GOS-I04: mission authority cannot exceed org unit
        if not set(mission["authority"]["capabilities"]).issubset(set(org_caps)):
            raise MissionError("mission authority must be ⊆ org unit")
        self._missions[mission["id"]] = mission
        self._ledger.append(
            event_type="mission.assigned",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=org_unit["goal_id"],
            org_unit_id=org_unit["id"],
            payload={"mission_id": mission["id"], "objective": objective},
            producer="organization.mission",
        )
        return deepcopy(mission)

    def get(self, mission_id: str) -> dict[str, Any]:
        return deepcopy(self._missions[mission_id])
