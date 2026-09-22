"""Regression locks for Y17-5 forecasting holdout protocol."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

from global_os.common.paths import y17_available

RUN = Path(__file__).resolve().parents[1] / "artifacts" / "y17" / "Y17-5-B2-omega-forecast-holdout" / "experiments" / "run_mission.py"


def _load():
    spec = importlib.util.spec_from_file_location("y17_5_run_mission", RUN)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_seed_ranges_disjoint_from_priors():
    mod = _load()
    assert set(mod.TRAIN_SEEDS).isdisjoint(set(mod.HOLD_SEEDS))
    assert set(mod.TRAIN_SEEDS).isdisjoint(mod.EXCLUDED_PREVIOUS)
    assert set(mod.HOLD_SEEDS).isdisjoint(mod.EXCLUDED_PREVIOUS)


def test_mean_baseline_cannot_beat_itself_on_identical_data():
    """Sanity: baseline RMSE on its own train mean is the train std of log_m1."""
    mod = _load()
    y = np.array([1.0, 2.0, 3.0])
    pred = np.full_like(y, y.mean())
    assert mod._rmse(y, pred) == np.std(y, ddof=0)


@pytest.mark.skipif(not y17_available(), reason="Y-17 clone not present")
def test_y17_5_real_holdout_stable():
    mod = _load()
    raw = mod.run_experiment()
    status, checks = mod.deterministic_verify(raw)
    assert status == "PASS"
    assert "train/hold seeds disjoint" in checks
    assert raw["decision"] in {"SUPPORTED", "REJECTED"}
    # replay lock for current locked split
    assert raw["decision"] == "SUPPORTED"
    assert raw["holdout"]["ratio_model_over_baseline"] <= mod.MCID_RATIO


def test_docs_subsystem_gate_rule_present():
    text = (Path(__file__).resolve().parents[1] / "artifacts" / "hardening" / "DEVELOPMENT_RULES_DOGFOOD.md").read_text(
        encoding="utf-8"
    )
    assert "≥2 independent real missions" in text or ">=2 independent real missions" in text
    assert "training information" in text.lower() or "≠" in text or "holdout" in text.lower()
