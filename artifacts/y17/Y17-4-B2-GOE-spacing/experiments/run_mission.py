"""Y17-4 — cross-domain RMT probe: do B2 Chernoff/Neural-ODE symmetric-part spectra
look GOE-like locally (nearest-neighbor spacing ratio ⟨r⟩)?

Class: cross-domain spectral / RMT (distinct from Y17-1 Fisher, Y17-2 model selection,
Y17-3 Boolean causal). Opens P-RIEMANN-RMT question on non-number-theoretic spectra.

Uses Y-17 matrix builder read-only; reimplements r-stat locally (no Odlyzko download).
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from typing import Any

import numpy as np

Y17 = Path("/workspace/Y-17-100-gipotez/experiments")
MULTIN = Y17 / "20260907-chernoff-neuralode-nd-multiseed-multin" / "run.py"

R_POISSON = 2 * math.log(2) - 1  # ≈0.386294
R_GOE = 4 - 2 * math.sqrt(3)  # ≈0.535898 (3×3 surmise)
R_GUE = 2 * math.sqrt(3) / math.pi - 0.5  # ≈0.60266
TOL = 0.05  # primary band around GOE (wider than H-B1-1a ±0.01 — different population)

N_DIM = 32
SEED_START = 500
SEED_END = 520  # 20 fresh matrices; disjoint from Y17-1 seeds 400-459
CONTROL_SEED = 7


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def r_stat(levels: np.ndarray) -> np.ndarray:
    s = np.diff(np.asarray(levels, dtype=float))
    if s.size < 2:
        raise ValueError("need ≥3 levels")
    if np.any(s <= 0):
        raise ValueError("non-positive spacing — abort")
    return np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])


def mean_r(levels: np.ndarray) -> float:
    return float(r_stat(levels).mean())


def symmetric_part_eigs(a: np.ndarray) -> np.ndarray:
    s = 0.5 * (a + a.T)
    ev = np.linalg.eigvalsh(s)
    return np.sort(np.real(ev))


def synthetic_goe(n: int, rng: np.random.Generator) -> np.ndarray:
    g = rng.normal(size=(n, n))
    h = 0.5 * (g + g.T)
    return np.sort(np.linalg.eigvalsh(h))


def synthetic_poisson(n: int, rng: np.random.Generator) -> np.ndarray:
    # unordered spacings ~ Exp → sorted cumulative sums as levels
    spacings = rng.exponential(size=n)
    return np.cumsum(spacings)


def analyze_matrix_r(a: np.ndarray) -> float:
    return mean_r(symmetric_part_eigs(a))


def run_experiment() -> dict[str, Any]:
    multin = _load("y17_multin_y174", MULTIN)
    rng = np.random.default_rng(CONTROL_SEED)

    # Controls (synthetic)
    goe_rs = [mean_r(synthetic_goe(N_DIM, rng)) for _ in range(40)]
    poi_rs = [mean_r(synthetic_poisson(N_DIM, rng)) for _ in range(40)]
    goe_mean = float(np.mean(goe_rs))
    poi_mean = float(np.mean(poi_rs))
    goe_control_ok = abs(goe_mean - R_GOE) < TOL
    poi_control_ok = abs(poi_mean - R_POISSON) < TOL

    per_seed: dict[str, Any] = {}
    rs: list[float] = []
    for seed in range(SEED_START, SEED_END):
        a = multin.build_matrix_with_seed_and_n(N_DIM, seed)
        r = analyze_matrix_r(a)
        rs.append(r)
        per_seed[str(seed)] = {"r_mean": r, "n_dim": N_DIM}

    r_bar = float(np.mean(rs))
    r_std = float(np.std(rs, ddof=1))
    dist_goe = abs(r_bar - R_GOE)
    dist_gue = abs(r_bar - R_GUE)
    dist_poi = abs(r_bar - R_POISSON)
    in_goe_band = dist_goe < TOL
    closer_to_goe_than_poisson = dist_goe < dist_poi

    # Primary (locked): GOE-like local statistics on B2 symmetric-part spectra
    if goe_control_ok and poi_control_ok and in_goe_band and closer_to_goe_than_poisson:
        decision = "SUPPORTED"
        nulls: list[dict[str, Any]] = []
    else:
        decision = "REJECTED"
        nulls = []
        if not goe_control_ok:
            nulls.append({"id": "goe_control_failed", "goe_mean": goe_mean, "target": R_GOE})
        if not poi_control_ok:
            nulls.append({"id": "poisson_control_failed", "poi_mean": poi_mean, "target": R_POISSON})
        if not in_goe_band:
            nulls.append(
                {
                    "id": "b2_r_outside_goe_band",
                    "r_bar": r_bar,
                    "R_GOE": R_GOE,
                    "tol": TOL,
                    "dist_goe": dist_goe,
                }
            )
        if not closer_to_goe_than_poisson:
            nulls.append(
                {
                    "id": "closer_to_poisson_or_tie",
                    "dist_goe": dist_goe,
                    "dist_poi": dist_poi,
                }
            )

    contradictory: list[dict[str, Any]] = []
    if in_goe_band and dist_gue < dist_goe:
        contradictory.append(
            {
                "note": "inside GOE band but numerically closer to GUE surmise",
                "dist_goe": dist_goe,
                "dist_gue": dist_gue,
                "rule": "walled — primary remains GOE-band criterion",
            }
        )

    return {
        "config": {
            "class": "cross_domain_rmt",
            "n_dim": N_DIM,
            "seed_range": [SEED_START, SEED_END],
            "n_matrices": SEED_END - SEED_START,
            "spectrum": "eigvalsh((A+A.T)/2)",
            "statistic": "mean nearest-neighbor spacing ratio ⟨r⟩",
            "targets": {"poisson": R_POISSON, "goe": R_GOE, "gue": R_GUE},
            "tol": TOL,
            "primary_rule": "SUPPORTED iff controls OK AND |⟨r⟩-R_GOE|<TOL AND closer to GOE than Poisson",
            "y17_writes": False,
        },
        "controls": {
            "goe_mean_r": goe_mean,
            "poisson_mean_r": poi_mean,
            "goe_control_ok": goe_control_ok,
            "poisson_control_ok": poi_control_ok,
            "n_control_draws": 40,
        },
        "primary": {
            "r_bar": r_bar,
            "r_std": r_std,
            "dist_goe": dist_goe,
            "dist_gue": dist_gue,
            "dist_poisson": dist_poi,
            "in_goe_band": in_goe_band,
            "closer_to_goe_than_poisson": closer_to_goe_than_poisson,
            "per_seed": per_seed,
        },
        "decision": decision,
        "nulls": nulls,
        "contradictory_evidence": contradictory,
        "scope": {
            "qualification": (
                "SUPPORTED means local spacing ratios of this structured B2 family "
                "are GOE-like under the locked band; does NOT prove universal spectral "
                "universality for all non-number-theoretic spectra (P-RIEMANN-RMT remains open)."
            )
        },
    }


def decide_fn(raw: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    return raw["decision"], raw.get("nulls", [])


def deterministic_verify(raw: dict[str, Any]) -> tuple[str, list[str]]:
    checks: list[str] = []
    ok = True
    r_bar = raw["primary"]["r_bar"]
    if not (0.0 < r_bar < 1.0):
        ok = False
        checks.append("r_bar not in (0,1)")
    else:
        checks.append("r_bar in (0,1)")
    expected = (
        "SUPPORTED"
        if (
            raw["controls"]["goe_control_ok"]
            and raw["controls"]["poisson_control_ok"]
            and raw["primary"]["in_goe_band"]
            and raw["primary"]["closer_to_goe_than_poisson"]
        )
        else "REJECTED"
    )
    if raw["decision"] != expected:
        ok = False
        checks.append(f"decision {raw['decision']} != expected {expected}")
    else:
        checks.append("decision matches prereg rule")
    if raw["config"]["seed_range"][0] < 460:
        # soft check: prefer disjoint from Y17-1; hard fail if overlap 400-459
        if raw["config"]["seed_range"][0] < 460 and raw["config"]["seed_range"][0] >= 400:
            ok = False
            checks.append("seed overlap with Y17-1")
        else:
            checks.append("seeds outside Y17-1 confirmatory range")
    else:
        checks.append("seeds outside Y17-1 confirmatory range")
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
                "r_bar": out["primary"]["r_bar"],
                "controls": out["controls"],
                "dists": {
                    "goe": out["primary"]["dist_goe"],
                    "gue": out["primary"]["dist_gue"],
                    "poi": out["primary"]["dist_poisson"],
                },
            },
            indent=2,
        )
    )
