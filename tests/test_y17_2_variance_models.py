"""Regression tests for Y17-2 nested Var model comparison logic."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

RUN = Path("/workspace/artifacts/y17/Y17-2-HCAT31-V3-variance-models/experiments/run_mission.py")


def _load():
    spec = importlib.util.spec_from_file_location("y17_2_run_mission", RUN)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_nested_f_recovers_known_two_param_signal():
    mod = _load()
    rng = np.random.default_rng(0)
    ns = np.array([32, 64, 128, 256, 512, 1024, 1536, 2048, 3000], dtype=float)
    c_true, d_true = 4.0, 40.0
    rows = []
    for n in ns:
        var = c_true / n + d_true / (n**2)
        # tiny noise so F is still decisive
        var = float(var * (1.0 + rng.normal(0, 0.002)))
        se = max(0.01 * var, 1e-12)
        rows.append({"n": float(n), "var": var, "reps": 100.0, "se_var": se, "weight": 1.0 / se**2})
    primary = mod.analyze_population(rows, "synthetic_two_param")
    decision, nulls = mod.decide_primary(primary)
    assert decision == "SUPPORTED"
    assert nulls == []
    assert primary["nested_f"]["p"] < 0.05
    assert primary["fit_M1_C_over_n_plus_D_over_n2"]["D"] > 0


def test_nested_f_rejects_pure_c_over_n():
    mod = _load()
    ns = np.array([32, 64, 128, 256, 512, 1024, 1536, 2048, 3000], dtype=float)
    c_true = 4.0
    rows = []
    for n in ns:
        var = float(c_true / n)
        se = max(0.01 * var, 1e-12)
        rows.append({"n": float(n), "var": var, "reps": 100.0, "se_var": se, "weight": 1.0 / se**2})
    primary = mod.analyze_population(rows, "synthetic_m0")
    decision, _ = mod.decide_primary(primary)
    assert decision == "REJECTED"
    assert primary["nested_f"]["p"] >= 0.05 or primary["fit_M1_C_over_n_plus_D_over_n2"]["D"] <= 0


def test_y17_2_real_artifacts_decision_stable():
    """Replay lock: committed Y-17 rows must keep REJECTED under locked rule."""
    mod = _load()
    raw = mod.run_experiment()
    assert raw["decision"] == "REJECTED"
    status, checks = mod.deterministic_verify(raw)
    assert status == "PASS"
    assert "decision matches prereg rule" in checks
    assert raw["primary"]["nested_f"]["p"] >= 0.05
