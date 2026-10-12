#!/usr/bin/env python3
"""C06 probe: coverage.xml line-rate='80' (percent-shaped) false-passes.

Gate multiplies line-rate by 100. If artifact stores percent (80) instead of
ratio (0.80), observed coverage becomes 8000% and passes min_coverage=80.

Materiality: false pass on malformed/non-cobertura coverage artifacts.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path("/tmp/pilot/p3-arm-C/tools/workflow-controller")
sys.path.insert(0, str(ROOT))

from workflow_controller.artifact_gate import verify_artifacts


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        project_dir = Path(tmp)
        (project_dir / "test-results.json").write_text(
            json.dumps({"summary": {"passed": 15, "failed": 0}}),
            encoding="utf-8",
        )
        (project_dir / "coverage.xml").write_text(
            '<?xml version="1.0" ?><coverage line-rate="80"></coverage>',
            encoding="utf-8",
        )
        (project_dir / "README.md").write_text(
            "Install\nRun\nTest\n",
            encoding="utf-8",
        )
        verdict = verify_artifacts(
            issue_id="REPRO-6",
            project_dir=project_dir,
            min_tests=15,
            min_coverage=80.0,
        )
        cov = next(c for c in verdict.checks if c.name == "coverage.xml")
        print("status=", verdict.status)
        print("coverage_check=", cov.status, cov.message, cov.observed)

        if verdict.status == "pass" and cov.observed and cov.observed.get("coverage_percent", 0) > 100:
            print("CONFIRMED: percent-shaped line-rate false-passes")
            return 0
        print("NOT CONFIRMED")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
