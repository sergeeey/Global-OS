#!/usr/bin/env python3
"""Run PREPROD_SUPERVISED acceptance missions and write delivery archives."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from global_os.runtime.preprod import start_mission  # noqa: E402


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _write(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_se_sandbox(dest: Path) -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    (dest / "README.md").write_text(
        "# SE sandbox\n\nBug: VALUE should be 2 after fix marker is applied.\n",
        encoding="utf-8",
    )
    (dest / "app.py").write_text("VALUE = 1  # intentional pre-fix baseline\n", encoding="utf-8")
    (dest / "tests_smoke.py").write_text(
        "from app import VALUE\n\ndef test_value_baseline():\n    assert VALUE == 1\n",
        encoding="utf-8",
    )
    return dest


def prepare_research_corpus(dest: Path) -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    (dest / "notes.md").write_text(
        "# Local research corpus\n\n"
        "Primary source: [Example Paper](https://example.com/paper-a).\n"
        "Related DOI 10.5555/preprod.research.001 appears in literature.\n\n"
        "- Hypothesis A: structured Goal Contracts reduce false SUCCESS rates.\n"
        "- Hypothesis B: LLM self-report alone is sufficient verification (contested).\n"
        "> Claim: observation-conditioned loops outperform scripted single-tool pilots.\n",
        encoding="utf-8",
    )
    (dest / "methods.txt").write_text(
        "Method: extract sources and claim spans; do not treat claims as facts.\n"
        "See also https://example.com/methods.\n",
        encoding="utf-8",
    )
    return dest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "artifacts/preprod/final_acceptance/missions"))
    parser.add_argument("--model", default="reactive", choices=("reactive", "scripted", "live"))
    parser.add_argument("--authorize-live-llm", action="store_true")
    parser.add_argument("--gos-root", default="")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    gos = Path(args.gos_root) if args.gos_root else out / ".gos_missions"
    if gos.exists():
        shutil.rmtree(gos)
    gos.mkdir(parents=True)

    hooks = {
        "force_model_mode": args.model,
        "max_model_cycles": 10,
    }
    if args.authorize_live_llm:
        hooks["authorize_live_llm"] = True
        hooks["live_budget_usd"] = 0.0

    results: list[dict] = []

    se_target = prepare_se_sandbox(out / "se_sandbox")
    se_goal = json.loads((ROOT / "examples/goal_se_sandbox.json").read_text(encoding="utf-8"))
    try:
        se_delivery = start_mission(
            se_goal,
            target_path=se_target,
            gos_root=gos / "se",
            budget_usd=5.0,
            hooks=hooks,
        )
        _write(out / "se_delivery.json", se_delivery)
        results.append(
            {
                "mission": "software_engineering_sandbox",
                "terminal_status": se_delivery.get("terminal_status"),
                "completion": se_delivery.get("completion", {}).get("status"),
                "executed_tools": se_delivery.get("executed_tools"),
                "model_mode": se_delivery.get("model_mode"),
                "model_cycles": se_delivery.get("model_cycles"),
                "model_cost_usd": se_delivery.get("model_cost_usd"),
                "fix_marker_exists": (se_target / "FIX_APPLIED.txt").exists(),
                "run_id": se_delivery.get("run_id"),
                "observe_block": se_delivery.get("observe_block"),
            }
        )
    except Exception as exc:  # noqa: BLE001 — acceptance harness records failure
        results.append(
            {
                "mission": "software_engineering_sandbox",
                "terminal_status": "BLOCKED",
                "error": repr(exc),
            }
        )

    research_target = prepare_research_corpus(out / "research_corpus")
    research_goal = json.loads(
        (ROOT / "examples/goal_research_scan.json").read_text(encoding="utf-8")
    )
    try:
        research_delivery = start_mission(
            research_goal,
            target_path=research_target,
            gos_root=gos / "research",
            budget_usd=3.0,
            hooks=hooks,
        )
        _write(out / "research_delivery.json", research_delivery)
        results.append(
            {
                "mission": "research_data_analysis",
                "terminal_status": research_delivery.get("terminal_status"),
                "completion": research_delivery.get("completion", {}).get("status"),
                "executed_tools": research_delivery.get("executed_tools"),
                "model_mode": research_delivery.get("model_mode"),
                "model_cycles": research_delivery.get("model_cycles"),
                "model_cost_usd": research_delivery.get("model_cost_usd"),
                "run_id": research_delivery.get("run_id"),
                "observe_block": research_delivery.get("observe_block"),
            }
        )
    except Exception as exc:  # noqa: BLE001 — acceptance harness records failure
        results.append(
            {
                "mission": "research_data_analysis",
                "terminal_status": "BLOCKED",
                "error": repr(exc),
            }
        )

    summary = {
        "generated_at": _now(),
        "model": args.model,
        "authorize_live_llm": bool(args.authorize_live_llm),
        "results": results,
    }
    _write(out / "MISSIONS_SUMMARY.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
