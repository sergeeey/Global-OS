"""Y17-5 — forecasting: does ω(A) log-linear model beat a mean baseline on holdout M1?

Class: predictive / forecasting with locked temporal-style seed holdout.
Distinct from Y17-1 (Fisher confirmatory), Y17-2 (model selection), Y17-3 (causal),
Y17-4 (RMT spacing).

Protocol locked before holdout compute:
  TRAIN seeds 550-564, N_DIM=24  → fit log(M1) ~ a + b·ω(A)
  HOLD  seeds 650-664, N_DIM=24  → evaluate RMSE; never used for fit
  BASELINE: predict mean(log M1) from TRAIN only
  MCID: model RMSE_hold ≤ 0.90 · baseline RMSE_hold  (strictly ≥10% better)
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import numpy as np

Y17 = Path(__file__).resolve().parents[4] / "Y-17-100-gipotez" / "experiments"
MULTIN = Y17 / "20260907-chernoff-neuralode-nd-multiseed-multin" / "run.py"
DIM = Y17 / "20260907-chernoff-neuralode-nd-dimension-sweep" / "run.py"
ABS = Y17 / "20260907-chernoff-neuralode-nd-numerical-abscissa" / "run.py"

N_DIM = 24
TRAIN_SEEDS = list(range(550, 565))  # 15
HOLD_SEEDS = list(range(650, 665))  # 15
MCID_RATIO = 0.90  # model must be ≤ 90% of baseline RMSE
EXCLUDED_PREVIOUS = set(range(400, 460)) | set(range(500, 520))  # Y17-1, Y17-4


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _assert_no_leak() -> None:
    train, hold = set(TRAIN_SEEDS), set(HOLD_SEEDS)
    assert train.isdisjoint(hold), "train/hold overlap"
    assert train.isdisjoint(EXCLUDED_PREVIOUS), "train overlaps prior mission seeds"
    assert hold.isdisjoint(EXCLUDED_PREVIOUS), "hold overlaps prior mission seeds"


def _collect(multin, abscissa, dim_sweep, seeds: list[int]) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for seed in seeds:
        a = multin.build_matrix_with_seed_and_n(N_DIM, seed)
        omega = float(abscissa.numerical_abscissa(a))
        m1 = float(dim_sweep.measure_m1(a, dim_sweep.T_MAX, dim_sweep.W))
        rows.append({"seed": float(seed), "omega": omega, "m1": m1, "log_m1": float(np.log(m1))})
    return rows


def _fit_omega_model(train: list[dict[str, float]]) -> dict[str, float]:
    x = np.array([r["omega"] for r in train], dtype=float)
    y = np.array([r["log_m1"] for r in train], dtype=float)
    # np.polyfit(x,y,1) returns [slope, intercept] for y = slope*x + intercept
    slope, intercept = np.polyfit(x, y, 1)
    return {"intercept": float(intercept), "slope": float(slope)}


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def run_experiment() -> dict[str, Any]:
    _assert_no_leak()
    multin = _load("y175_multin", MULTIN)
    dim_sweep = _load("y175_dim", DIM)
    abscissa = _load("y175_abs", ABS)

    # --- TRAIN only ---
    train_rows = _collect(multin, abscissa, dim_sweep, TRAIN_SEEDS)
    model = _fit_omega_model(train_rows)
    train_log = np.array([r["log_m1"] for r in train_rows])
    train_omega = np.array([r["omega"] for r in train_rows])
    baseline_level = float(np.mean(train_log))
    train_pred_model = model["intercept"] + model["slope"] * train_omega
    train_pred_base = np.full_like(train_log, baseline_level)
    train_rmse_model = _rmse(train_log, train_pred_model)
    train_rmse_base = _rmse(train_log, train_pred_base)

    # --- HOLD (after train fit locked) ---
    hold_rows = _collect(multin, abscissa, dim_sweep, HOLD_SEEDS)
    hold_log = np.array([r["log_m1"] for r in hold_rows])
    hold_omega = np.array([r["omega"] for r in hold_rows])
    hold_pred_model = model["intercept"] + model["slope"] * hold_omega
    hold_pred_base = np.full_like(hold_log, baseline_level)
    hold_rmse_model = _rmse(hold_log, hold_pred_model)
    hold_rmse_base = _rmse(hold_log, hold_pred_base)
    ratio = hold_rmse_model / hold_rmse_base if hold_rmse_base > 0 else float("inf")
    beats_baseline = ratio <= MCID_RATIO

    if beats_baseline:
        decision = "SUPPORTED"
        nulls: list[dict[str, Any]] = []
    else:
        decision = "REJECTED"
        nulls = [
            {
                "id": "model_fails_mcid_vs_baseline",
                "hold_rmse_model": hold_rmse_model,
                "hold_rmse_baseline": hold_rmse_base,
                "ratio": ratio,
                "mcid_ratio": MCID_RATIO,
                "interpretation": "ω(A) forecast does not beat mean baseline by ≥10% on holdout",
            }
        ]

    contradictory: list[dict[str, Any]] = []
    if train_rmse_model < train_rmse_base and not beats_baseline:
        contradictory.append(
            {
                "note": "model beats baseline in-sample but fails holdout MCID — classic overfit signature",
                "train_ratio": train_rmse_model / train_rmse_base,
                "hold_ratio": ratio,
                "rule": "walled — verdict uses holdout only",
            }
        )
    if beats_baseline and hold_rmse_model > hold_rmse_base:
        contradictory.append(
            {
                "note": "beats MCID ratio check but absolute RMSE worse than baseline (should be impossible)",
                "rule": "logic check",
            }
        )

    return {
        "config": {
            "class": "forecasting_holdout",
            "n_dim": N_DIM,
            "train_seeds": TRAIN_SEEDS,
            "hold_seeds": HOLD_SEEDS,
            "feature": "ω(A)=λ_max((A+Aᵀ)/2)",
            "target": "log(M1)",
            "model": "OLS log(M1) ~ a + b·ω",
            "baseline": "mean(log M1) from TRAIN only",
            "mcid_ratio": MCID_RATIO,
            "protocol": "fit on TRAIN only; evaluate on HOLD; no post-cutoff refit",
            "y17_writes": False,
        },
        "train": {
            "n": len(train_rows),
            "rows": train_rows,
            "model": model,
            "baseline_level_log_m1": baseline_level,
            "rmse_model": train_rmse_model,
            "rmse_baseline": train_rmse_base,
        },
        "holdout": {
            "n": len(hold_rows),
            "rows": hold_rows,
            "rmse_model": hold_rmse_model,
            "rmse_baseline": hold_rmse_base,
            "ratio_model_over_baseline": ratio,
            "beats_baseline_mcid": beats_baseline,
        },
        "decision": decision,
        "nulls": nulls,
        "contradictory_evidence": contradictory,
        "scope": {
            "qualification": (
                "SUPPORTED means this ω→M1 OLS forecast beats mean baseline by ≥10% RMSE "
                "on locked holdout seeds for N_DIM=24 B2 family — not a general forecasting theorem."
            )
        },
    }


def decide_fn(raw: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    return raw["decision"], raw.get("nulls", [])


def deterministic_verify(raw: dict[str, Any]) -> tuple[str, list[str]]:
    checks: list[str] = []
    ok = True
    train_seeds = set(int(r["seed"]) for r in raw["train"]["rows"])
    hold_seeds = set(int(r["seed"]) for r in raw["holdout"]["rows"])
    if not train_seeds.isdisjoint(hold_seeds):
        ok = False
        checks.append("train/hold seed leak")
    else:
        checks.append("train/hold seeds disjoint")
    if train_seeds & EXCLUDED_PREVIOUS or hold_seeds & EXCLUDED_PREVIOUS:
        ok = False
        checks.append("overlap with Y17-1/Y17-4 seed ranges")
    else:
        checks.append("no overlap with Y17-1/Y17-4 seeds")
    # model must not have been refit on holdout: slope from train-only polyfit check
    x = np.array([r["omega"] for r in raw["train"]["rows"]])
    y = np.array([r["log_m1"] for r in raw["train"]["rows"]])
    slope, intercept = np.polyfit(x, y, 1)
    if abs(slope - raw["train"]["model"]["slope"]) > 1e-9 or abs(
        intercept - raw["train"]["model"]["intercept"]
    ) > 1e-9:
        ok = False
        checks.append("stored model != recompute from TRAIN rows")
    else:
        checks.append("model matches TRAIN-only recompute")
    ratio = raw["holdout"]["ratio_model_over_baseline"]
    expected = "SUPPORTED" if ratio <= MCID_RATIO else "REJECTED"
    if raw["decision"] != expected:
        ok = False
        checks.append(f"decision {raw['decision']} != expected {expected}")
    else:
        checks.append("decision matches holdout MCID rule")
    if raw["config"]["y17_writes"] is not False:
        ok = False
        checks.append("y17_writes must be false")
    else:
        checks.append("no Y-17 writes")
    return ("PASS" if ok else "FAIL", checks)


if __name__ == "__main__":
    import json

    out = run_experiment()
    print(
        json.dumps(
            {
                "decision": out["decision"],
                "hold": out["holdout"],
                "train_rmse": {
                    "model": out["train"]["rmse_model"],
                    "base": out["train"]["rmse_baseline"],
                },
                "model": out["train"]["model"],
            },
            indent=2,
        )
    )
