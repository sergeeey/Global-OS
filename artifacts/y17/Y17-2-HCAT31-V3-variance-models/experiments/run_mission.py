"""Y17-2 — H-CAT31-4 Relaxation Map V3: nested Var model comparison.

Reads Y-17 committed metrics only (no Y-17 writes). Different class from Y17-1
(model selection on Lovász variance law vs Fisher confirmatory on ω(A)).

Preregistration locked before fit:
  M0: Var(n) = C / n
  M1: Var(n) = C / n + D / n²
  Primary: nested F-test of M1 vs M0 on composite H-CAT31-3 rows, α=0.05
  SUPPORTED iff p_F < 0.05 AND D_hat > 0
  REJECTED iff p_F >= 0.05 OR (p_F < 0.05 AND D_hat <= 0)
  Prime rows (H-CAT31-4) are secondary / wall-off only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

Y17 = Path("/workspace/Y-17-100-gipotez/experiments")
COMPOSITE_RUN = (
    Y17 / "20260910-lovasz-theta-variance-scaling-cat31-3" / "metrics" / "run.json"
)
PRIME_ANALYSIS = (
    Y17 / "20260919-lovasz-prime-n-variance-cat31-4" / "metrics" / "analysis.json"
)

PRIMARY_ALPHA = 0.05


def load_composite_rows() -> list[dict[str, float]]:
    data = json.loads(COMPOSITE_RUN.read_text(encoding="utf-8"))
    rows: list[dict[str, float]] = []
    for r in data["sweep"]:
        var = float(r["var_log_ratio"])
        se_rel = float(r["var_log_ratio_relative_se"])
        se_var = max(se_rel * var, 1e-18)
        rows.append(
            {
                "n": float(r["n"]),
                "var": var,
                "reps": float(r["n_reps"]),
                "se_var": se_var,
                "weight": 1.0 / (se_var**2),
            }
        )
    return rows


def load_prime_rows() -> list[dict[str, float]]:
    data = json.loads(PRIME_ANALYSIS.read_text(encoding="utf-8"))
    rows: list[dict[str, float]] = []
    for r in data["rows"]:
        var = float(r["var"])
        se_log = float(r["se_log_var"])
        se_var = max(se_log * var, 1e-18)  # delta method
        rows.append(
            {
                "n": float(r["n"]),
                "var": var,
                "reps": float(r["reps"]),
                "se_var": se_var,
                "weight": 1.0 / (se_var**2),
            }
        )
    return rows


def _design(
    rows: list[dict[str, float]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = np.array([r["n"] for r in rows], dtype=float)
    y = np.array([r["var"] for r in rows], dtype=float)
    w = np.array([r["weight"] for r in rows], dtype=float)
    x0 = (1.0 / n).reshape(-1, 1)  # M0: C/n
    x1 = np.column_stack([1.0 / n, 1.0 / (n**2)])  # M1: C/n + D/n²
    return y, w, x0, x1, n


def weighted_ols(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> dict[str, Any]:
    """Weighted OLS through columns of x (no intercept beyond design)."""
    sw = np.sqrt(w)
    xw = x * sw[:, None]
    yw = y * sw
    beta, residuals, rank, s = np.linalg.lstsq(xw, yw, rcond=None)
    yhat = x @ beta
    resid = y - yhat
    rss = float(np.sum(w * resid**2))
    n_obs, k = x.shape
    # weighted R² vs weighted mean
    ybar = float(np.sum(w * y) / np.sum(w))
    tss = float(np.sum(w * (y - ybar) ** 2))
    r2 = 1.0 - rss / tss if tss > 0 else float("nan")
    aic = n_obs * np.log(rss / n_obs + 1e-300) + 2 * k
    bic = n_obs * np.log(rss / n_obs + 1e-300) + k * np.log(n_obs)
    return {
        "beta": beta.tolist(),
        "rss": rss,
        "r2": r2,
        "aic": float(aic),
        "bic": float(bic),
        "n_obs": n_obs,
        "k": k,
        "rank": int(rank),
        "yhat": yhat.tolist(),
        "resid": resid.tolist(),
    }


def nested_f_test(fit0: dict[str, Any], fit1: dict[str, Any]) -> dict[str, Any]:
    """Nested F comparing restricted fit0 vs unrestricted fit1 (one extra param)."""
    n_obs = fit1["n_obs"]
    df1 = 1  # extra parameters
    df2 = n_obs - fit1["k"]
    rss0 = fit0["rss"]
    rss1 = fit1["rss"]
    if df2 <= 0 or rss1 <= 0:
        return {"F": float("nan"), "p": float("nan"), "df1": df1, "df2": df2}
    f_stat = ((rss0 - rss1) / df1) / (rss1 / df2)
    p = float(1.0 - stats.f.cdf(f_stat, df1, df2))
    return {"F": float(f_stat), "p": p, "df1": df1, "df2": df2, "delta_rss": float(rss0 - rss1)}


def analyze_population(rows: list[dict[str, float]], label: str) -> dict[str, Any]:
    y, w, x0, x1, n = _design(rows)
    fit0 = weighted_ols(x0, y, w)
    fit1 = weighted_ols(x1, y, w)
    ftest = nested_f_test(fit0, fit1)
    c_hat = float(fit1["beta"][0])
    d_hat = float(fit1["beta"][1])
    return {
        "label": label,
        "n_points": len(rows),
        "n_values": n.tolist(),
        "vars": y.tolist(),
        "fit_M0_C_over_n": {"C": fit0["beta"][0], **{k: fit0[k] for k in ("rss", "r2", "aic", "bic")}},
        "fit_M1_C_over_n_plus_D_over_n2": {
            "C": c_hat,
            "D": d_hat,
            **{k: fit1[k] for k in ("rss", "r2", "aic", "bic")},
        },
        "nested_f": ftest,
        "delta_aic_M0_minus_M1": float(fit0["aic"] - fit1["aic"]),
    }


def decide_primary(primary: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    p = primary["nested_f"]["p"]
    d_hat = primary["fit_M1_C_over_n_plus_D_over_n2"]["D"]
    nulls: list[dict[str, Any]] = []
    if p >= PRIMARY_ALPHA:
        decision = "REJECTED"
        nulls.append(
            {
                "id": "nested_F_not_significant",
                "p": p,
                "alpha": PRIMARY_ALPHA,
                "interpretation": "extra D/n² term not justified at α=0.05 — C/n sufficient under this test",
            }
        )
    elif d_hat <= 0:
        decision = "REJECTED"
        nulls.append(
            {
                "id": "D_nonpositive_despite_significant_F",
                "D": d_hat,
                "p": p,
                "interpretation": "significant F but D≤0 — not support for positive finite-size correction",
            }
        )
    else:
        decision = "SUPPORTED"
    return decision, nulls


def run_experiment() -> dict[str, Any]:
    composite = load_composite_rows()
    primes = load_prime_rows()
    primary = analyze_population(composite, "H-CAT31-3_composite")
    secondary = analyze_population(primes, "H-CAT31-4_primes_walled")
    decision, nulls = decide_primary(primary)

    # secondary agreement (walled — must not upgrade verdict)
    sec_p = secondary["nested_f"]["p"]
    sec_d = secondary["fit_M1_C_over_n_plus_D_over_n2"]["D"]
    secondary_would_support = sec_p < PRIMARY_ALPHA and sec_d > 0
    secondary_agrees = secondary_would_support == (decision == "SUPPORTED")

    contradictory: list[dict[str, Any]] = []
    if not secondary_agrees:
        contradictory.append(
            {
                "note": "prime secondary nested-F direction disagrees with primary",
                "secondary_p": sec_p,
                "secondary_D": sec_d,
                "rule": "walled — does not change primary decision",
            }
        )
    if sec_p < PRIMARY_ALPHA and sec_d <= 0:
        contradictory.append(
            {
                "note": "primes: nested F significant but D≤0 (wrong-sign correction)",
                "secondary_p": sec_p,
                "secondary_D": sec_d,
                "rule": "walled descriptive — reinforces REJECTED for positive D/n² claim",
            }
        )

    return {
        "config": {
            "primary_population": "H-CAT31-3 composite committed Var(log(theta/sqrt(n))) rows",
            "secondary_population": "H-CAT31-4 prime rows (descriptive wall-off)",
            "models": {"M0": "Var = C/n", "M1": "Var = C/n + D/n^2"},
            "primary_test": "nested weighted F-test M1 vs M0",
            "alpha": PRIMARY_ALPHA,
            "weights": "inverse variance of Var_hat (composite: se_rel*var; primes: se_log_var*var)",
            "sources_read_only": [str(COMPOSITE_RUN), str(PRIME_ANALYSIS)],
        },
        "primary": primary,
        "secondary_walled": secondary,
        "secondary_agrees_with_primary_direction": secondary_agrees,
        "decision": decision,
        "nulls": nulls,
        "contradictory_evidence": contradictory,
    }


def deterministic_verify(raw: dict[str, Any]) -> tuple[str, list[str]]:
    checks: list[str] = []
    ok = True
    p = raw["primary"]["nested_f"]["p"]
    if not (0.0 <= p <= 1.0) or not np.isfinite(p):
        ok = False
        checks.append("nested F p not in [0,1]")
    else:
        checks.append("nested F p in [0,1]")
    # RSS must decrease (or stay) when adding a parameter
    if raw["primary"]["fit_M1_C_over_n_plus_D_over_n2"]["rss"] > raw["primary"]["fit_M0_C_over_n"]["rss"] + 1e-12:
        ok = False
        checks.append("M1 RSS worse than M0 — OLS bug")
    else:
        checks.append("M1 RSS <= M0 RSS")
    # decision consistency with prereg rule
    d_hat = raw["primary"]["fit_M1_C_over_n_plus_D_over_n2"]["D"]
    expected = "SUPPORTED" if (p < PRIMARY_ALPHA and d_hat > 0) else "REJECTED"
    if raw["decision"] != expected:
        ok = False
        checks.append(f"decision {raw['decision']} != expected {expected}")
    else:
        checks.append("decision matches prereg rule")
    # n*Var under M0 should be near C
    c0 = raw["primary"]["fit_M0_C_over_n"]["C"]
    if not np.isfinite(c0) or c0 <= 0:
        ok = False
        checks.append("M0 C not positive finite")
    else:
        checks.append("M0 C positive finite")
    return ("PASS" if ok else "FAIL", checks)


def decide_fn(raw: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    return raw["decision"], raw.get("nulls", [])


if __name__ == "__main__":
    out = run_experiment()
    print(json.dumps({"decision": out["decision"], "primary_nested_f": out["primary"]["nested_f"], "D": out["primary"]["fit_M1_C_over_n_plus_D_over_n2"]["D"]}, indent=2))
