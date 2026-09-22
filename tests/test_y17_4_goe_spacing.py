"""Regression lock for Y17-4 B2 GOE-spacing cross-domain probe."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

RUN = Path("/workspace/artifacts/y17/Y17-4-B2-GOE-spacing/experiments/run_mission.py")


def _load():
    spec = importlib.util.spec_from_file_location("y17_4_run_mission", RUN)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_r_stat_identity_on_equal_spacings():
    mod = _load()
    levels = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    assert mod.mean_r(levels) == 1.0


def test_y17_4_decision_stable_and_controls():
    mod = _load()
    raw = mod.run_experiment()
    assert raw["controls"]["goe_control_ok"] is True
    assert raw["controls"]["poisson_control_ok"] is True
    status, checks = mod.deterministic_verify(raw)
    assert status == "PASS"
    assert raw["decision"] in {"SUPPORTED", "REJECTED"}
    # replay lock: current committed population should stay SUPPORTED
    assert raw["decision"] == "SUPPORTED"
    assert raw["primary"]["in_goe_band"] is True
    assert "decision matches prereg rule" in checks
