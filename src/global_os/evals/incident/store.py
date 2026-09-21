"""Incident ledger — dataset for long-horizon self-improvement (not architecture expansion)."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from global_os.common.hashing import new_id
from global_os.contracts.validate import validate
from global_os.runtime.events.ledger import EventLedger


class IncidentError(Exception):
    pass


class IncidentStore:
    """Append-only incident records with required postmortem fields."""

    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._items: dict[str, dict[str, Any]] = {}

    def record(
        self,
        *,
        title: str,
        root_cause: str,
        blast_radius: str,
        detection_gap: str,
        why_tests_missed: str,
        regression_test: str,
        fix: str,
        residual_risk: str,
        tenant_id: str = "t",
        workspace_id: str = "w",
        goal_id: str | None = None,
        capability_ids: list[str] | None = None,
        status: str = "OPEN",
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        incident: dict[str, Any] = {
            "incident_id": new_id("inc"),
            "schema_version": "0.1.0",
            "title": title,
            "status": status,
            "detected_at": now,
            "root_cause": root_cause,
            "blast_radius": blast_radius,
            "detection_gap": detection_gap,
            "why_tests_missed": why_tests_missed,
            "regression_test": regression_test,
            "fix": fix,
            "residual_risk": residual_risk,
        }
        if goal_id:
            incident["goal_id"] = goal_id
        if capability_ids:
            incident["capability_ids"] = list(capability_ids)
        validate(incident, "incident.schema.json")
        self._items[incident["incident_id"]] = incident
        self._ledger.append(
            event_type="incident.recorded",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=goal_id,
            payload={
                "incident_id": incident["incident_id"],
                "title": title,
                "status": status,
            },
            producer="evals.incident",
        )
        return deepcopy(incident)

    def resolve(
        self,
        incident_id: str,
        *,
        tenant_id: str = "t",
        workspace_id: str = "w",
        status: str = "RESOLVED",
    ) -> dict[str, Any]:
        if incident_id not in self._items:
            raise IncidentError(f"unknown incident: {incident_id}")
        if status not in {"MITIGATED", "RESOLVED", "ACCEPTED_RISK"}:
            raise IncidentError(f"invalid resolve status: {status}")
        item = self._items[incident_id]
        item["status"] = status
        item["resolved_at"] = datetime.now(UTC).isoformat()
        validate(item, "incident.schema.json")
        self._ledger.append(
            event_type="incident.resolved",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=item.get("goal_id"),
            payload={"incident_id": incident_id, "status": status},
            producer="evals.incident",
        )
        return deepcopy(item)

    def list_all(self) -> list[dict[str, Any]]:
        return [deepcopy(v) for v in self._items.values()]

    def get(self, incident_id: str) -> dict[str, Any]:
        return deepcopy(self._items[incident_id])
