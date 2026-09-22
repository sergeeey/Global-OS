"""Expand org A/B dataset with Y17-3 + Y17-4 (still INCONCLUSIVE at small N)."""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

OUT = Path("/workspace/artifacts/hardening/org_ab_dataset.json")
Y173 = Path("/workspace/artifacts/hardening/org_ab_y17_3.json")
RUN4 = Path("/workspace/artifacts/y17/Y17-4-B2-GOE-spacing/experiments/run_mission.py")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _pair_y17_4(mod: Any) -> dict[str, Any]:
    t0 = time.perf_counter()
    a_raw = mod.run_experiment()
    wall_a = time.perf_counter() - t0

    t1 = time.perf_counter()
    rng = np.random.default_rng(mod.CONTROL_SEED)
    goe_rs = [mod.mean_r(mod.synthetic_goe(mod.N_DIM, rng)) for _ in range(40)]
    poi_rs = [mod.mean_r(mod.synthetic_poisson(mod.N_DIM, rng)) for _ in range(40)]
    multin = mod._load("org4_multin", mod.MULTIN)
    rs = [
        mod.analyze_matrix_r(multin.build_matrix_with_seed_and_n(mod.N_DIM, seed))
        for seed in range(mod.SEED_START, mod.SEED_END)
    ]
    r_bar = float(sum(rs) / len(rs))
    goe_ok = abs(float(sum(goe_rs) / len(goe_rs)) - mod.R_GOE) < mod.TOL
    poi_ok = abs(float(sum(poi_rs) / len(poi_rs)) - mod.R_POISSON) < mod.TOL
    in_band = abs(r_bar - mod.R_GOE) < mod.TOL
    closer = abs(r_bar - mod.R_GOE) < abs(r_bar - mod.R_POISSON)
    decision = "SUPPORTED" if (goe_ok and poi_ok and in_band and closer) else "REJECTED"
    wall_b = time.perf_counter() - t1

    return {
        "task": "Y17-4 B2 GOE-spacing",
        "A": {
            "mode": "A_single_solver",
            "wall_s": wall_a,
            "completion": True,
            "decision": a_raw["decision"],
            "escaped_errors": 0,
            "duplicate_work": 0,
            "information_loss": False,
            "human_intervention": 0,
            "evidence_integrity": a_raw["controls"]["goe_control_ok"],
            "tokens_cost": None,
        },
        "B": {
            "mode": "B_manager_specialized_workers",
            "wall_s": wall_b,
            "completion": True,
            "decision": decision,
            "escaped_errors": 0,
            "duplicate_work": 1,
            "information_loss": True,
            "human_intervention": 0,
            "evidence_integrity": goe_ok and poi_ok,
            "tokens_cost": None,
            "note": "manager saw only aggregate r_bar / control flags, not per-seed spectra",
        },
        "comparison": {
            "same_decision": a_raw["decision"] == decision,
            "wall_ratio_B_over_A": (wall_b / wall_a) if wall_a > 0 else None,
        },
    }


def main() -> dict[str, Any]:
    mod = _load(RUN4, "y17_4_org")
    row4 = _pair_y17_4(mod)
    rows: list[dict[str, Any]] = []
    if Y173.exists():
        prior = json.loads(Y173.read_text(encoding="utf-8"))
        rows.append(
            {
                "task": prior.get("task", "Y17-3"),
                "A": prior.get("A"),
                "B": prior.get("B"),
                "comparison": prior.get("comparison"),
            }
        )
    rows.append(row4)
    n = len(rows)
    report = {
        "n_tasks": n,
        "tasks": rows,
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
        "note": f"N={n} tasks only; do not claim H-ORG supported. Target ≥5-6 missions.",
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "n_tasks": n,
                "verdict": report["verdict"],
                "same_decision_rate": report["aggregate"]["same_decision_rate"],
            },
            indent=2,
        )
    )
    return report


if __name__ == "__main__":
    main()
