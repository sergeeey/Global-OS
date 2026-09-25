"""Run all Y18 failure-mode dogfood missions and write summary."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MISSIONS = [
    "Y18-1-evidence-invalidation",
    "Y18-2-effect-discrepancy",
    "Y18-3-authority-boundary",
    "Y18-4-provider-degradation",
]


def main() -> int:
    results = []
    for name in MISSIONS:
        script = Path(__file__).parent / name / "execute_mission.py"
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
            env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(ROOT / "src")},
        )
        decision_path = script.parent / "mission.json"
        decision = None
        if decision_path.is_file():
            decision = json.loads(decision_path.read_text(encoding="utf-8")).get("decision")
        results.append(
            {
                "mission": name,
                "exit_code": proc.returncode,
                "decision": decision,
                "stdout": (proc.stdout or "").strip()[-500:],
                "stderr": (proc.stderr or "").strip()[-500:],
            }
        )
        print(name, "exit", proc.returncode, "decision", decision)
        if proc.returncode != 0:
            print(proc.stderr[-1000:])

    summary = {
        "suite": "Y18_failure_mode_dogfood",
        "n": len(results),
        "results": results,
        "all_supported": all(r.get("decision") == "SUPPORTED" for r in results),
        "failure_mode_classes": [
            "evidence_change_invalidation",
            "external_effect_recovery",
            "authority_boundary",
            "provider_tool_degradation",
        ],
        "freeze_relevance": (
            "Diversity of failure modes for freeze candidate — not M1.5 claim"
        ),
    }
    out = Path(__file__).parent / "suite_summary.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("all_supported", summary["all_supported"])
    return 0 if summary["all_supported"] and all(r["exit_code"] == 0 for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
