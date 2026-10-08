"""Emit machine-readable project status aligned with implementation evidence."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "docs" / "IMPLEMENTATION_STATUS.md"


def _pytest_count() -> tuple[int, str]:
    """Return (count, diagnostic). count < 0 means collection failed."""
    env = os.environ.copy()
    src = str(ROOT / "src")
    prev = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src if not prev else f"{src}{os.pathsep}{prev}"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    for line in reversed(proc.stdout.strip().splitlines()):
        # e.g. "318 tests collected in 0.90s"
        if "test" in line and "collected" in line:
            try:
                return int(line.split()[0]), ""
            except ValueError:
                break
    diag_parts = [
        f"pytest_exit={proc.returncode}",
        f"stdout_tail={proc.stdout.strip()[-400:]!r}",
        f"stderr_tail={proc.stderr.strip()[-400:]!r}",
    ]
    return -1, "; ".join(diag_parts)


def main() -> int:
    count, diag = _pytest_count()
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
        print(f"error: pytest collect failed ({diag})", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
