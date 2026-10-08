"""Acceptance: project_status regenerates IMPLEMENTATION_STATUS with a real pytest count."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_project_status_collects_pytest_and_writes_matrix_rows() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "tools.project_status"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    status = (ROOT / "docs" / "IMPLEMENTATION_STATUS.md").read_text(encoding="utf-8")
    m = re.search(r"pytest collected:\s*\*\*(\d+)\*\*", status)
    assert m is not None, status[:400]
    assert int(m.group(1)) >= 100
    assert "goal_contract_immutable" in status
    assert "capabilities tracked:" in status
