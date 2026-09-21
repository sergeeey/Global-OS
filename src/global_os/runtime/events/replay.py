"""Event replay — rebuild epistemic projections from append-only ledger (GOS-I15)."""

from __future__ import annotations

from copy import deepcopy

from global_os.runtime.events.ledger import EventLedger


class EventReplayError(Exception):
    pass


class EventReplayEngine:
    """Rebuild claim/model/forecast/decision/commitment status projections from events.

    Does not mutate the ledger. Projection is derived truth for status fields only;
    entity bodies must still be seeded (events carry deltas, not full snapshots).
    """

    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger

    def rebuild_status_projection(
        self,
        *,
        seed: dict[str, dict[str, str]] | None = None,
        goal_id: str | None = None,
        tenant_id: str = "system",
        workspace_id: str = "system",
    ) -> dict[str, dict[str, str]]:
        """Return {kind: {id: status}} after replaying invalidation/stale events."""
        projection: dict[str, dict[str, str]] = {
            "evidence": {},
            "claim": {},
            "model": {},
            "forecast": {},
            "decision": {},
            "commitment": {},
            "belief": {},
            "assumption": {},
        }
        if seed:
            for kind, items in seed.items():
                if kind not in projection:
                    raise EventReplayError(f"unknown projection kind: {kind}")
                projection[kind] = dict(items)

        for event in self._ledger.list_events(goal_id=goal_id):
            et = event["event_type"]
            payload = event.get("payload", {})
            if et == "evidence.invalidated" and "evidence_id" in payload:
                projection["evidence"][payload["evidence_id"]] = "INVALIDATED"
            elif et == "claim.staled":
                if "claim_id" in payload:
                    projection["claim"][payload["claim_id"]] = payload.get(
                        "new_status", "STALE"
                    )
                if "belief_id" in payload:
                    projection["belief"][payload["belief_id"]] = payload.get(
                        "new_status", "STALE"
                    )
            elif et == "model.staled":
                projection["model"][payload["model_id"]] = "STALE"
            elif et == "forecast.staled":
                projection["forecast"][payload["forecast_id"]] = "STALE"
            elif et == "decision.needs_review":
                projection["decision"][payload["decision_id"]] = "NEEDS_REVIEW"
            elif et == "commitment.needs_review":
                projection["commitment"][payload["commitment_id"]] = "NEEDS_REVIEW"
            elif et == "assumption.staled":
                projection["assumption"][payload["assumption_id"]] = "STALE"

        self._ledger.append(
            event_type="projection.rebuilt",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=goal_id,
            payload={
                "kinds": sorted(projection.keys()),
                "counts": {k: len(v) for k, v in projection.items()},
            },
            producer="event.replay",
        )
        return deepcopy(projection)
