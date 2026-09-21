"""Emit machine-readable project status aligned with implementation evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "docs" / "IMPLEMENTATION_STATUS.md"


def _pytest_count() -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    # last non-empty line like "30 tests collected in 0.12s"
    for line in reversed(proc.stdout.strip().splitlines()):
        if "test" in line and "collected" in line:
            return int(line.split()[0])
    return -1


def main() -> int:
    count = _pytest_count()
    matrix = json.loads((ROOT / "docs" / "capability_matrix.json").read_text(encoding="utf-8"))
    lines = [
        "# IMPLEMENTATION_STATUS.md",
        "",
        "Generated evidence snapshot. Do not hand-edit claims that contradict tests.",
        "",
        f"- pytest collected: **{count}**",
        f"- capabilities tracked: **{len(matrix['capabilities'])}**",
        "",
        "| Capability | State | Evidence |",
        "| ---------- | ----- | -------- |",
    ]
    for item in matrix["capabilities"]:
        lines.append(
            f"| {item['id']} | {item['state']} | {item.get('evidence', '')} |"
        )
    lines.append("")
    STATUS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {STATUS_PATH.relative_to(ROOT)} (tests={count})")
    if count < 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
