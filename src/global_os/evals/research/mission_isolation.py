"""Shared helper: run historical mission scripts in an isolated artifact copy."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_mission_isolated(repo_root: Path, mission_dir: Path, *, tmp_path: Path) -> Path:
    """Copy mission_dir → tmp, set GOS_MISSION_ARTIFACT_ROOT, run execute_mission.py."""
    dst = tmp_path / mission_dir.name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(mission_dir, dst)
    env = {
        **dict(os.environ),
        "PYTHONPATH": str(repo_root / "src"),
        "GOS_MISSION_ARTIFACT_ROOT": str(dst),
    }
    proc = subprocess.run(
        [sys.executable, str(dst / "execute_mission.py")],
        cwd=str(repo_root),
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return dst
