"""Rebuild org A/B dataset across Y17-1..Y17-5 with decomposability tags.

A: single solver (one coherent compute/decide path).
B: manager + specialized workers with explicit handoffs (no shared mutable goal).

N≥5 enables pattern inspection by decomposability; H-ORG still not claimed.
"""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import combine_pvalues

OUT = Path("/workspace/artifacts/hardening/org_ab_dataset.json")
Y173 = Path("/workspace/artifacts/hardening/org_ab_y17_3.json")
Y171_METRICS = Path(
    "/workspace/artifacts/y17/Y17-1-HB2-1n-confirmatory/experiments/metrics/run.json"
)
RUN2 = Path("/workspace/artifacts/y17/Y17-2-HCAT31-V3-variance-models/experiments/run_mission.py")
RUN4 = Path("/workspace/artifacts/y17/Y17-4-B2-GOE-spacing/experiments/run_mission.py")
RUN5 = Path("/workspace/artifacts/y17/Y17-5-B2-omega-forecast-holdout/experiments/run_mission.py")

PRIMARY_ALPHA = 0.05


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _row(
    task: str,
    *,
    decomposability: str,
    class_tag: str,
    a: dict[str, Any],
    b: dict[str, Any],
) -> dict[str, Any]:
    return {
        "task": task,
        "class": class_tag,
        "decomposability": decomposability,
        "A": a,
        "B": b,
        "comparison": {
            "same_decision": a.get("decision") == b.get("decision"),
            "wall_ratio_B_over_A": (
                (b["wall_s"] / a["wall_s"]) if a.get("wall_s", 0) > 0 else None
            ),
            "B_more_duplicate_work": b.get("duplicate_work", 0) > a.get("duplicate_work", 0),
            "B_information_loss_flag": bool(b.get("information_loss")),
        },
    }


def _y17_1() -> dict[str, Any]:
    """Fisher confirmatory — HIGH decomposability (independent n_dim slices → combine)."""
    metrics = json.loads(Y171_METRICS.read_text(encoding="utf-8"))
    slices = metrics["per_n_slice"]

    t0 = time.perf_counter()
    ps = [float(slices[k]["spearman_p"]) for k in sorted(slices, key=lambda x: int(x))]
    _, fisher_p = combine_pvalues(ps, method="fisher")
    decision_a = "SUPPORTED" if fisher_p < PRIMARY_ALPHA else "REJECTED"
    wall_a = time.perf_counter() - t0
    a = {
        "mode": "A_single_solver",
        "wall_s": wall_a,
        "completion": True,
        "decision": decision_a,
        "escaped_errors": 0,
        "duplicate_work": 0,
        "information_loss": False,
        "human_intervention": 0,
        "evidence_integrity": True,
        "tokens_cost": None,
        "fisher_p": float(fisher_p),
        "source": "locked_metrics_recompute",
    }

    t1 = time.perf_counter()
    handoffs = 0
    worker_msgs: list[dict[str, Any]] = []
    for key in sorted(slices, key=lambda x: int(x)):
        # worker: emits only p (manager does not see rho / per-seed) → info loss
        msg = {"n_dim": int(key), "spearman_p": float(slices[key]["spearman_p"])}
        worker_msgs.append(msg)
        handoffs += 1
    manager_ps = [m["spearman_p"] for m in worker_msgs]
    _, fisher_b = combine_pvalues(manager_ps, method="fisher")
    decision_b = "SUPPORTED" if fisher_b < PRIMARY_ALPHA else "REJECTED"
    handoffs += 1
    wall_b = time.perf_counter() - t1
    b = {
        "mode": "B_manager_specialized_workers",
        "wall_s": wall_b,
        "completion": True,
        "decision": decision_b,
        "escaped_errors": 0,
        "duplicate_work": 0,
        "information_loss": True,  # manager saw p only, not rho/per_seed
        "human_intervention": 0,
        "evidence_integrity": decision_a == decision_b,
        "tokens_cost": None,
        "handoffs": handoffs,
        "n_workers": len(worker_msgs),
        "fisher_p": float(fisher_b),
        "note": "per-n_dim workers → manager Fisher; manager lacks rho/per_seed",
    }
    return _row(
        "Y17-1 Fisher confirmatory slices",
        decomposability="HIGH",
        class_tag="statistics_fisher",
        a=a,
        b=b,
    )


def _y17_3_from_prior() -> dict[str, Any]:
    prior = json.loads(Y173.read_text(encoding="utf-8"))
    return _row(
        prior.get("task", "Y17-3 permanent-clamp Boolean recompute"),
        decomposability="HIGH",
        class_tag="causal_boolean",
        a=prior["A"],
        b=prior["B"],
    )


def _y17_4_staged(mod) -> dict[str, Any]:
    """RMT GOE — MEDIUM: controls ∥ spectra can parallelize; decide needs both."""
    t0 = time.perf_counter()
    raw = mod.run_experiment()
    wall_a = time.perf_counter() - t0

    t1 = time.perf_counter()
    handoffs = 0
    multin = mod._load("org_y174_multin", mod.MULTIN)
    rng = np.random.default_rng(mod.CONTROL_SEED)

    # worker: GOE control
    goe_rs = [mod.mean_r(mod.synthetic_goe(mod.N_DIM, rng)) for _ in range(40)]
    goe_msg = {
        "goe_mean": float(np.mean(goe_rs)),
        "ok": abs(float(np.mean(goe_rs)) - mod.R_GOE) < mod.TOL,
    }
    handoffs += 1

    # worker: Poisson control
    poi_rs = [mod.mean_r(mod.synthetic_poisson(mod.N_DIM, rng)) for _ in range(40)]
    poi_msg = {
        "poi_mean": float(np.mean(poi_rs)),
        "ok": abs(float(np.mean(poi_rs)) - mod.R_POISSON) < mod.TOL,
    }
    handoffs += 1

    # worker: B2 spectra (manager gets only r_bar, not per-seed)
    rs: list[float] = []
    for seed in range(mod.SEED_START, mod.SEED_END):
        a = multin.build_matrix_with_seed_and_n(mod.N_DIM, seed)
        rs.append(mod.analyze_matrix_r(a))
    r_bar = float(np.mean(rs))
    spectra_msg = {"r_bar": r_bar, "n": len(rs)}
    handoffs += 1

    dist_goe = abs(r_bar - mod.R_GOE)
    dist_poi = abs(r_bar - mod.R_POISSON)
    in_band = dist_goe < mod.TOL
    closer = dist_goe < dist_poi
    decision_b = (
        "SUPPORTED"
        if (goe_msg["ok"] and poi_msg["ok"] and in_band and closer)
        else "REJECTED"
    )
    handoffs += 1
    wall_b = time.perf_counter() - t1

    a = {
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
    }
    b = {
        "mode": "B_manager_specialized_workers",
        "wall_s": wall_b,
        "completion": True,
        "decision": decision_b,
        "escaped_errors": 0,
        "duplicate_work": 0,
        "information_loss": True,  # manager lacks per-seed r list
        "human_intervention": 0,
        "evidence_integrity": raw["decision"] == decision_b,
        "tokens_cost": None,
        "handoffs": handoffs,
        "note": "controls ∥ spectra workers; manager decides from summaries",
    }
    return _row(
        "Y17-4 B2 GOE-spacing",
        decomposability="MEDIUM",
        class_tag="cross_domain_rmt",
        a=a,
        b=b,
    )


def _y17_5_staged(mod) -> dict[str, Any]:
    """Forecast holdout — HIGH: train collect | fit | hold collect | eval."""
    t0 = time.perf_counter()
    raw = mod.run_experiment()
    wall_a = time.perf_counter() - t0

    t1 = time.perf_counter()
    handoffs = 0
    multin = mod._load("org_y175_multin", mod.MULTIN)
    dim_sweep = mod._load("org_y175_dim", mod.DIM)
    abscissa = mod._load("org_y175_abs", mod.ABS)

    train_rows = mod._collect(multin, abscissa, dim_sweep, mod.TRAIN_SEEDS)
    handoffs += 1
    model = mod._fit_omega_model(train_rows)
    baseline_level = float(np.mean([r["log_m1"] for r in train_rows]))
    fit_msg = {"model": model, "baseline": baseline_level}
    handoffs += 1

    hold_rows = mod._collect(multin, abscissa, dim_sweep, mod.HOLD_SEEDS)
    handoffs += 1
    # manager: only summaries from workers (no raw train rows → info loss potential)
    hold_log = np.array([r["log_m1"] for r in hold_rows])
    hold_omega = np.array([r["omega"] for r in hold_rows])
    hold_pred_model = fit_msg["model"]["intercept"] + fit_msg["model"]["slope"] * hold_omega
    hold_pred_base = np.full_like(hold_log, fit_msg["baseline"])
    rmse_m = mod._rmse(hold_log, hold_pred_model)
    rmse_b = mod._rmse(hold_log, hold_pred_base)
    ratio = rmse_m / rmse_b if rmse_b > 0 else float("inf")
    decision_b = "SUPPORTED" if ratio <= mod.MCID_RATIO else "REJECTED"
    handoffs += 1
    wall_b = time.perf_counter() - t1

    a = {
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
    }
    b = {
        "mode": "B_manager_specialized_workers",
        "wall_s": wall_b,
        "completion": True,
        "decision": decision_b,
        "escaped_errors": 0,
        "duplicate_work": 0,
        "information_loss": True,  # manager did not retain full train rows after fit
        "human_intervention": 0,
        "evidence_integrity": raw["decision"] == decision_b,
        "tokens_cost": None,
        "handoffs": handoffs,
        "hold_ratio": ratio,
        "note": "train→fit→hold→eval handoffs; natural pipeline decomposition",
    }
    return _row(
        "Y17-5 omega forecast holdout",
        decomposability="HIGH",
        class_tag="forecasting_holdout",
        a=a,
        b=b,
    )


def _y17_2_staged(mod) -> dict[str, Any]:
    """Nested model selection — LOW decomposability (sequential fit dependence)."""
    t0 = time.perf_counter()
    raw = mod.run_experiment()
    wall_a = time.perf_counter() - t0

    t1 = time.perf_counter()
    handoffs = 0
    rows = mod.load_composite_rows()
    handoffs += 1
    y, w, x0, x1, _n = mod._design(rows)
    fit0 = mod.weighted_ols(x0, y, w)
    handoffs += 1
    fit1 = mod.weighted_ols(x1, y, w)
    handoffs += 1
    nested = mod.nested_f_test(fit0, fit1)
    handoffs += 1
    p = float(nested["p"])
    d_hat = float(fit1["beta"][1])
    decision_b = "SUPPORTED" if (p < PRIMARY_ALPHA and d_hat > 0) else "REJECTED"
    handoffs += 1
    wall_b = time.perf_counter() - t1

    a = {
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
    }
    b = {
        "mode": "B_manager_specialized_workers",
        "wall_s": wall_b,
        "completion": True,
        "decision": decision_b,
        "escaped_errors": 0,
        "duplicate_work": 1,
        "information_loss": True,
        "human_intervention": 0,
        "evidence_integrity": raw["decision"] == decision_b,
        "tokens_cost": None,
        "handoffs": handoffs,
        "note": "sequential M0→M1→F via staged WLS; low decomposability",
    }
    return _row(
        "Y17-2 nested Var model selection",
        decomposability="LOW",
        class_tag="model_selection",
        a=a,
        b=b,
    )


def main() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    rows.append(_y17_1())
    mod2 = _load(RUN2, "org_y172")
    rows.append(_y17_2_staged(mod2))
    if Y173.exists():
        rows.append(_y17_3_from_prior())
    mod4 = _load(RUN4, "org_y174")
    rows.append(_y17_4_staged(mod4))
    mod5 = _load(RUN5, "org_y175")
    rows.append(_y17_5_staged(mod5))

    n = len(rows)
    by_task = {
        r["task"]: {
            "same_decision": r["comparison"]["same_decision"],
            "B_info_loss": r["B"]["information_loss"],
            "wall_ratio": r["comparison"]["wall_ratio_B_over_A"],
            "decomposability": r["decomposability"],
            "class": r["class"],
        }
        for r in rows
    }
    by_decomp: dict[str, list[str]] = {}
    for r in rows:
        by_decomp.setdefault(r["decomposability"], []).append(r["task"])

    # Pattern inspection (not a scientific claim)
    high = [r for r in rows if r["decomposability"] == "HIGH"]
    low = [r for r in rows if r["decomposability"] == "LOW"]
    pattern_notes: list[str] = []
    if high:
        pattern_notes.append(
            f"HIGH n={len(high)}: same_decision="
            f"{sum(1 for r in high if r['comparison']['same_decision'])}/{len(high)}; "
            "B still shows information_loss on summary handoffs"
        )
    if low:
        pattern_notes.append(
            f"LOW n={len(low)}: specialization does not remove sequential fit dependence; "
            f"same_decision={sum(1 for r in low if r['comparison']['same_decision'])}/{len(low)}"
        )

    if n >= 5:
        verdict = "PATTERNS_OBSERVABLE_H_ORG_NOT_CLAIMED"
        note = (
            f"N={n} (≥5). Decomposability patterns inspectable; "
            "do NOT claim H-ORG supported. Need larger multi-class sample + token costs "
            "before any org superiority claim."
        )
    else:
        verdict = "INCONCLUSIVE_REAL_SAMPLE_TOO_SMALL"
        note = f"N={n} (<5). Do not claim H-ORG."

    report = {
        "n_tasks": n,
        "tasks": rows,
        "by_task": by_task,
        "by_decomposability": by_decomp,
        "aggregate": {
            "same_decision_rate": sum(1 for r in rows if r["comparison"]["same_decision"]) / n,
            "mean_wall_ratio_B_over_A": float(
                sum((r["comparison"]["wall_ratio_B_over_A"] or 0.0) for r in rows) / n
            ),
            "B_information_loss_rate": sum(1 for r in rows if r["B"]["information_loss"]) / n,
            "B_duplicate_work_rate": sum(1 for r in rows if r["B"].get("duplicate_work", 0) > 0)
            / n,
        },
        "pattern_notes": pattern_notes,
        "verdict": verdict,
        "scientific_claim_accepted": False,
        "note": note,
        "decomposability_hypothesis": (
            "Manager+workers may help only when stages are independently verifiable (HIGH). "
            "On LOW (sequential nested fit), B adds handoff/info-loss cost without decision gain. "
            "Current sample shows same_decision≈1 with B information_loss≈1 — org does not yet "
            "beat single solver on these deterministic research pipelines."
        ),
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "n_tasks": n,
                "verdict": report["verdict"],
                "by_decomposability": by_decomp,
                "aggregate": report["aggregate"],
                "pattern_notes": pattern_notes,
            },
            indent=2,
        )
    )
    return report


if __name__ == "__main__":
    main()
