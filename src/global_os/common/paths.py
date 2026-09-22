"""Repository path helpers — never hardcode absolute machine paths."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return Global OS repository root (…/src/global_os/common/paths.py → parents[3])."""
    return Path(__file__).resolve().parents[3]


def y17_experiments_root() -> Path:
    return repo_root() / "Y-17-100-gipotez" / "experiments"


def y17_available() -> bool:
    return y17_experiments_root().is_dir()
