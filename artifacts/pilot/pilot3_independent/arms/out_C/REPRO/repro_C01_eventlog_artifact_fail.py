#!/usr/bin/env python3
"""C01: verify_event_log rejects legitimate artifact-gate FAIL runs.

Observed: when artifact gate fails (status=fail), issue_runner writes final
reason "artifact gate fail", but event_log._validate_consistency only accepts
"artifact gate blocked" and requires status==blocked for the 2-event path.

Expected: a faithfully produced fail path should verify_event_log → pass
(or at least not fail for reason mismatch on a correctly emitted fail sequence).

ToolCallSuccess: gates run and write events.
WorldSuccess: event log validation should accept the authentic fail sequence.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path("/tmp/pilot/p3-arm-C/tools/workflow-controller")
sys.path.insert(0, str(ROOT))

from workflow_controller.event_log import verify_event_log
from workflow_controller.issue_runner import run_issue_gates


def _write_failing_artifacts(project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "test-results.json").write_text(
        json.dumps({"summary": {"passed": 10, "failed": 2}}),
        encoding="utf-8",
    )
    (project_dir / "coverage.xml").write_text(
        '<?xml version="1.0" ?><coverage line-rate="0.90"></coverage>',
        encoding="utf-8",
    )
    (project_dir / "README.md").write_text(
        "# Fail fixture\n\nInstall.\n\nRun.\n\nTest.\n",
        encoding="utf-8",
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        project_dir = root / "project"
        event_log = root / "events.jsonl"
        _write_failing_artifacts(project_dir)

        run = run_issue_gates(
            issue_id="REPRO-1",
            project_dir=project_dir,
            event_log=event_log,
        )
        assert run.final.status == "fail", run.final
        assert run.final.reason == "artifact gate fail", run.final.reason
        assert len(run.gates) == 1, run.gates

        events = [
            json.loads(line)
            for line in event_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert [e["stage"] for e in events] == ["artifact_gate", "issue_gates"]
        assert events[0]["status"] == "fail"
        assert events[1]["status"] == "fail"
        assert events[1]["reason"] == "artifact gate fail"

        verdict = verify_event_log(event_log=event_log, expected_issue_id="REPRO-1")
        print("run.final.status=", run.final.status)
        print("run.final.reason=", run.final.reason)
        print("verify_event_log.status=", verdict.status)
        print("verify_event_log.reason=", verdict.reason)

        # DEFECT: authentic fail sequence is rejected
        if verdict.status == "fail" and "artifact-gate final reason mismatch" in verdict.reason:
            print("CONFIRMED: event log rejects authentic artifact-gate fail sequence")
            return 0
        print("NOT CONFIRMED: unexpected verifier outcome")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
