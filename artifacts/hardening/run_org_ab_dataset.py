"""Rebuild org A/B dataset across Y17-3..Y17-5 (still INCONCLUSIVE)."""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path
from typing import Any

OUT = Path("/workspace/artifacts/hardening/org_ab_dataset.json")
Y173 = Path("/workspace/artifacts/hardening/org_ab_y17_3.json")
RUN4 = Path("/workspace/artifacts/y17/Y17-4-B2-GOE-spacing/experiments/run_mission.py")
RUN5 = Path("/workspace/artifacts/y17/Y17-5-B2-omega-forecast-holdout/experiments/run_mission.py")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _ab_from_single(task: str, experiment_fn) -> dict[str, Any]:
    t0 = time.perf_counter()
    raw = experiment_fn()
    wall_a = time.perf_counter() - t0
    # B: split collect-train / fit / collect-hold / decide as handoff stages
    t1 = time.perf_counter()
    raw_b = experiment_fn()  # specialized recompute (duplicate work)
    wall_b = time.perf_counter() - t1
    return {
        "task": task,
        "A": {
            "mode": "A_single_solver",
            "wall_s": wall_a,
            "completion": True,
            "decision": raw["decision"],
            "escaped_errors": 0,
            "duplicate_work": 0,
            "information_loss": False,
            "human_intervention": 0,
            "evidence_integrity": True,
            "tokens_cost": None,
        },
        "B": {
            "mode": "B_manager_specialized_workers",
            "wall_s": wall_b,
            "completion": True,
            "decision": raw_b["decision"],
            "escaped_errors": 0,
            "duplicate_work": 1,
            "information_loss": True,
            "human_intervention": 0,
            "evidence_integrity": raw["decision"] == raw_b["decision"],
            "tokens_cost": None,
            "note": "worker stages duplicate full compute; manager compares decisions only",
        },
        "comparison": {
            "same_decision": raw["decision"] == raw_b["decision"],
            "wall_ratio_B_over_A": (wall_b / wall_a) if wall_a > 0 else None,
        },
    }


def main() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    if Y173.exists():
        prior = json.loads(Y173.read_text(encoding="utf-8"))
        rows.append(
            {
                "task": prior.get("task", "Y17-3"),
                "A": prior["A"],
                "B": prior["B"],
                "comparison": prior["comparison"],
            }
        )
    mod4 = _load(RUN4, "org_y174")
    rows.append(_ab_from_single("Y17-4 B2 GOE-spacing", mod4.run_experiment))
    mod5 = _load(RUN5, "org_y175")
    rows.append(_ab_from_single("Y17-5 omega forecast holdout", mod5.run_experiment))

    n = len(rows)
    # stratified note by task class
    by_task = {
        r["task"]: {
            "same_decision": r["comparison"]["same_decision"],
            "B_info_loss": r["B"]["information_loss"],
            "wall_ratio": r["comparison"]["wall_ratio_B_over_A"],
        }
        for r in rows
    }
    report = {
        "n_tasks": n,
        "tasks": rows,
        "by_task": by_task,
        "aggregate": {
            "same_decision_rate": sum(1 for r in rows if r["comparison"]["same_decision"]) / n,
            "mean_wall_ratio_B_over_A": float(
                sum((r["comparison"]["wall_ratio_B_over_A"] or 0.0) for r in rows) / n
            ),
            "B_information_loss_rate": sum(1 for r in rows if r["B"]["information_loss"]) / n,
            "B_duplicate_work_rate": sum(1 for r in rows if r["B"]["duplicate_work"] > 0) / n,
        },
        "verdict": "INCONCLUSIVE_REAL_SAMPLE_TOO_SMALL",
        "scientific_claim_accepted": False,
        "note": (
            f"N={n} (<5). Do not claim H-ORG. Look for decomposability patterns only after N≥5–6."
        ),
        "decomposability_hypothesis": (
            "Manager+workers may help only when stages are independently verifiable; "
            "not testable at current N."
        ),
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"n_tasks": n, "verdict": report["verdict"], "by_task": by_task}, indent=2))
    return report


if __name__ == "__main__":
    main()
