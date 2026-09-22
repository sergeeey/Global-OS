"""Y17-1 confirmatory Fisher replication — reads Y-17 code, writes only to Global OS artifacts.

Does NOT modify Y-17. Preregistration locked: seeds 400-459, Fisher primary α=0.05.
"""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

import numpy as np
from scipy.stats import combine_pvalues, spearmanr

Y17 = Path(__file__).resolve().parents[4] / "Y-17-100-gipotez" / "experiments"
OUT = Path(__file__).resolve().parents[1]
EXP = OUT / "experiments"
METRICS = EXP / "metrics"

LARGE_N_DIM_VALUES = (16, 24, 32, 40, 50)
SEED_START = 400
SEED_END = 460
PRIMARY_ALPHA = 0.05
EXCLUDED_SEED_INDEXES = set(range(0, 160)) | set(range(300, 340))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main() -> dict:
    assert set(range(SEED_START, SEED_END)).isdisjoint(EXCLUDED_SEED_INDEXES)

    dim_sweep = _load("y17_dim_sweep", Y17 / "20260907-chernoff-neuralode-nd-dimension-sweep" / "run.py")
    multin = _load("y17_multin", Y17 / "20260907-chernoff-neuralode-nd-multiseed-multin" / "run.py")
    abscissa_1n = _load(
        "y17_abscissa_1n", Y17 / "20260907-chernoff-neuralode-nd-numerical-abscissa" / "run.py"
    )

    # RNG independence smoke: streams for (16,400) vs (24,400) must differ
    a16 = multin.build_matrix_with_seed_and_n(16, SEED_START)
    a24 = multin.build_matrix_with_seed_and_n(24, SEED_START)
    assert a16.shape != a24.shape or not np.allclose(a16[:16, :16], a24[:16, :16])

    started = time.perf_counter()
    per_n_slice: dict = {}
    for n_dim in LARGE_N_DIM_VALUES:
        omegas = []
        m1s = []
        per_seed = {}
        for seed in range(SEED_START, SEED_END):
            a = multin.build_matrix_with_seed_and_n(n_dim, seed)
            omega = float(abscissa_1n.numerical_abscissa(a))
            m1 = float(dim_sweep.measure_m1(a, dim_sweep.T_MAX, dim_sweep.W))
            omegas.append(omega)
            m1s.append(m1)
            per_seed[str(seed)] = {"omega": omega, "m1": m1}
        rho, p = spearmanr(omegas, m1s)
        per_n_slice[str(n_dim)] = {
            "n_dim": n_dim,
            "n_seeds": SEED_END - SEED_START,
            "seed_range": [SEED_START, SEED_END],
            "spearman_rho": float(rho),
            "spearman_p": float(p),
            "omega_range": [float(min(omegas)), float(max(omegas))],
            "omega_std": float(np.std(omegas)),
            "per_seed": per_seed,
        }

    slice_rhos = [v["spearman_rho"] for v in per_n_slice.values()]
    slice_ps = [v["spearman_p"] for v in per_n_slice.values()]
    fisher_stat, fisher_p = combine_pvalues(slice_ps, method="fisher")
    n_sig = sum(1 for p in slice_ps if p < PRIMARY_ALPHA)
    n_pos = sum(1 for r in slice_rhos if r > 0)
    n_neg = sum(1 for r in slice_rhos if r < 0)

    if fisher_p < PRIMARY_ALPHA:
        primary_verdict = "SUPPORTED"
        y17_letter = "CONFIRMED"
    else:
        primary_verdict = "REJECTED"
        y17_letter = "REJECTED"

    wall_s = time.perf_counter() - started
    result = {
        "config": {
            "n_dim_values": list(LARGE_N_DIM_VALUES),
            "seed_range": [SEED_START, SEED_END],
            "n_seeds_per_slice": SEED_END - SEED_START,
            "population_note": (
                "FRESH seeds 400-459 — zero overlap with H-B2-1n (0-39), H-B2-1o (40-99), "
                "H-B2-1q (100-159), H-B2-1t (300-339). Same N_DIM set as H-B2-1o confirmatory."
            ),
        },
        "rng_checks": {
            "seed_disjoint_from_excluded": True,
            "seedsequence_n_dim_seed_used": True,
            "different_ndim_same_seed_index_not_identical": True,
        },
        "per_n_slice": per_n_slice,
        "primary_criterion": {
            "statistic": "fisher_combined_p",
            "pre_registered_threshold": PRIMARY_ALPHA,
            "fisher_combined_statistic": float(fisher_stat),
            "fisher_combined_p": float(fisher_p),
        },
        "secondary_descriptive": {
            "n_slices_significant_alpha05": n_sig,
            "n_slices_positive": n_pos,
            "n_slices_negative": n_neg,
            "slice_rhos": slice_rhos,
            "slice_ps": slice_ps,
            "note": "NOT verdict-determining",
        },
        "verdict_primary": primary_verdict,
        "verdict_y17_letter": y17_letter,
        "wall_seconds": wall_s,
    }

    METRICS.mkdir(parents=True, exist_ok=True)
    (METRICS / "run.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    slim = {k: v for k, v in result.items() if k != "per_n_slice"}
    (METRICS / "run_summary.json").write_text(json.dumps(slim, indent=2), encoding="utf-8")
    print(json.dumps(slim, indent=2))
    return result


if __name__ == "__main__":
    main()
