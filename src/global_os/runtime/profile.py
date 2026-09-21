"""Runtime profile resolution — production prefers Rust Authority (fail-closed).

Profiles:
- ``dev`` (default): Python Authority OK for local/tests
- ``production``: requires ``GOS_AUTHORITY_BACKEND=rust`` (or defaults to rust)
  and probes ``gos-authority`` at startup — never silent Python allow
"""

from __future__ import annotations

import os
from typing import Literal

from global_os.adapters.authority.rust_client import RustAuthorityError, find_gos_authority_bin
from global_os.kernel.authority.kernel import AuthorityBackend

RuntimeProfile = Literal["dev", "production"]


class ProductionProfileError(Exception):
    """Production profile cannot start safely."""


def resolve_profile(raw: str | None = None) -> RuntimeProfile:
    value = (raw if raw is not None else os.environ.get("GOS_PROFILE", "dev")).strip().lower()
    if value not in {"dev", "production"}:
        raise ValueError(f"unsupported GOS_PROFILE: {value!r}")
    return value  # type: ignore[return-value]


def resolve_authority_backend(
    *,
    profile: RuntimeProfile | None = None,
    explicit: AuthorityBackend | None = None,
) -> AuthorityBackend:
    """Choose Authority backend.

    Explicit constructor arg wins. Else env ``GOS_AUTHORITY_BACKEND``.
    Production profile defaults to ``rust``; dev defaults to ``python``.
    """
    if explicit is not None:
        return explicit
    env = os.environ.get("GOS_AUTHORITY_BACKEND")
    if env in {"python", "rust"}:
        return env  # type: ignore[return-value]
    active = profile if profile is not None else resolve_profile()
    return "rust" if active == "production" else "python"


def probe_production_authority() -> None:
    """Fail closed if production Authority binary is missing."""
    if find_gos_authority_bin() is None:
        raise ProductionProfileError(
            "GOS_PROFILE=production requires gos-authority binary; "
            "refusing silent Python Authority fallback"
        )


def apply_production_guards(*, profile: RuntimeProfile, backend: AuthorityBackend) -> None:
    """Enforce production invariants at RuntimeContext construction."""
    if profile != "production":
        return
    if backend != "rust":
        raise ProductionProfileError(
            "GOS_PROFILE=production forbids python Authority backend; "
            "set GOS_AUTHORITY_BACKEND=rust"
        )
    try:
        probe_production_authority()
    except RustAuthorityError as exc:
        raise ProductionProfileError(str(exc)) from exc
