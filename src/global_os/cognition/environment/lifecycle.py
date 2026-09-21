"""Execution environment trust lifecycle — governed artifact (not free self-rewrite)."""

from __future__ import annotations

from enum import Enum


class EnvironmentLifecycle(str, Enum):
    PROPOSED = "PROPOSED"
    SANDBOXED = "SANDBOXED"
    EVALUATED = "EVALUATED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    MONITORED = "MONITORED"
    REVOKED = "REVOKED"


_ALLOWED: dict[EnvironmentLifecycle, set[EnvironmentLifecycle]] = {
    EnvironmentLifecycle.PROPOSED: {EnvironmentLifecycle.SANDBOXED, EnvironmentLifecycle.REVOKED},
    EnvironmentLifecycle.SANDBOXED: {EnvironmentLifecycle.EVALUATED, EnvironmentLifecycle.REVOKED},
    EnvironmentLifecycle.EVALUATED: {EnvironmentLifecycle.APPROVED, EnvironmentLifecycle.REVOKED},
    EnvironmentLifecycle.APPROVED: {EnvironmentLifecycle.ACTIVE, EnvironmentLifecycle.REVOKED},
    EnvironmentLifecycle.ACTIVE: {EnvironmentLifecycle.MONITORED, EnvironmentLifecycle.REVOKED},
    EnvironmentLifecycle.MONITORED: {
        EnvironmentLifecycle.ACTIVE,
        EnvironmentLifecycle.REVOKED,
        EnvironmentLifecycle.PROPOSED,
    },
    EnvironmentLifecycle.REVOKED: set(),
}


class EnvironmentLifecycleError(Exception):
    pass


def transition(current: EnvironmentLifecycle, new: EnvironmentLifecycle) -> EnvironmentLifecycle:
    if new not in _ALLOWED[current]:
        raise EnvironmentLifecycleError(f"illegal transition {current.value} → {new.value}")
    return new
