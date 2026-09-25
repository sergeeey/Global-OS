"""Mission artifact root resolution + historical rewrite guard."""

from __future__ import annotations

import os
from pathlib import Path

# Repo-relative prefixes treated as frozen historical evidence after dogfood.
HISTORICAL_ARTIFACT_PREFIXES: tuple[str, ...] = (
    "artifacts/y17/",
    "artifacts/y19/",
    "artifacts/hardening/dogfood_fm/",
)

_ENV_ROOT = "GOS_MISSION_ARTIFACT_ROOT"
_ENV_ALLOW = "GOS_ALLOW_HISTORICAL_ARTIFACT_REWRITE"


def repo_root_from(path: Path) -> Path:
    """Walk up until src/global_os or .git exists."""
    cur = path.resolve()
    if cur.is_file():
        cur = cur.parent
    for p in [cur, *cur.parents]:
        if (p / "src" / "global_os").is_dir() or (p / ".git").exists():
            return p
    return cur


def mission_artifact_dir(script_file: str | Path) -> Path:
    """Prefer isolated root from env (tests); else script directory."""
    override = os.environ.get(_ENV_ROOT)
    if override:
        return Path(override).resolve()
    return Path(script_file).resolve().parent


def historical_rewrite_allowed() -> bool:
    return os.environ.get(_ENV_ALLOW, "").strip() == "1"


def assert_artifact_path_writable(path: Path, *, repo_root: Path | None = None) -> None:
    """Refuse silent overwrite of frozen historical mission artifacts."""
    if historical_rewrite_allowed():
        return
    root = repo_root or repo_root_from(path)
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return
    if any(rel.startswith(prefix) for prefix in HISTORICAL_ARTIFACT_PREFIXES):
        raise PermissionError(
            f"refusing to rewrite historical artifact '{rel}'. "
            f"Run under isolated {_ENV_ROOT}=... or set {_ENV_ALLOW}=1 intentionally."
        )
