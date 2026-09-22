#!/usr/bin/env python3
"""Run compressed 48h research-program preflight (does NOT start wall-clock 48h)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from global_os.evals.survival.research_program import run_preflight  # noqa: E402


def main() -> int:
    out = ROOT / "artifacts" / "hardening" / "long_horizon_48h" / "preflight"
    report = run_preflight(artifact_root=out)
    print(json.dumps(report.as_dict(), indent=2, ensure_ascii=False, default=str))
    print(
        f"\npreflight passed={report.passed} fidelity={report.fidelity} "
        f"m15_claimed={report.m15_claimed} wall_s={report.wall_seconds:.2f}",
        file=sys.stderr,
    )
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
