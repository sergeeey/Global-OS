"""Verification substrate health — concrete infra signals only (not a Kernel).

Distinguishes unusable verification procedure from hypothesis falsification.
Never maps bare timeout → UNHEALTHY without process_started=False.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class SubstrateStatus(str, Enum):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"


@dataclass(frozen=True)
class SubstrateHealth:
    status: SubstrateStatus
    signals: tuple[str, ...]
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "signals": list(self.signals),
            "details": dict(self.details),
            # Honesty alias — not a new Authority/Kernel enum.
            "taxonomy": (
                "ENVIRONMENT_GAP"
                if self.status == SubstrateStatus.UNHEALTHY
                else "SUBSTRATE_OK"
            ),
            "blocked_environment": self.status == SubstrateStatus.UNHEALTHY,
        }


def assess_substrate_health(
    *,
    target: Path | None = None,
    sandbox: dict[str, Any] | None = None,
) -> SubstrateHealth:
    """Return HEALTHY/UNHEALTHY from explicit, fail-closed signals only."""
    signals: list[str] = []
    details: dict[str, Any] = {}

    if target is not None:
        details["target"] = str(target)
        if not target.exists():
            signals.append("target_missing")
        elif not target.is_dir():
            signals.append("target_not_directory")
        else:
            try:
                next(target.iterdir(), None)
            except OSError as exc:
                signals.append("target_not_readable")
                details["target_error"] = str(exc)

    if sandbox:
        details["sandbox"] = {
            k: sandbox.get(k)
            for k in ("timed_out", "process_started", "exit_code", "reason")
            if k in sandbox
        }
        timed_out = bool(sandbox.get("timed_out"))
        # Only treat as infra when the process never started *and* timed out.
        if timed_out and sandbox.get("process_started") is False:
            signals.append("sandbox_never_started_timeout")
        # Explicit operator/harness signal
        if sandbox.get("environment_gap") is True:
            signals.append("environment_gap_flag")

    if signals:
        return SubstrateHealth(
            status=SubstrateStatus.UNHEALTHY,
            signals=tuple(signals),
            details=details,
        )
    return SubstrateHealth(
        status=SubstrateStatus.HEALTHY,
        signals=(),
        details=details,
    )
