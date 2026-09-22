"""Regression lock for Y17-3 independent H-B7-2 permanent-clamp recompute."""

from __future__ import annotations

import importlib.util
from pathlib import Path

RUN = Path("/workspace/artifacts/y17/Y17-3-HB7-2-permanent-clamp/experiments/run_mission.py")


def _load():
    spec = importlib.util.spec_from_file_location("y17_3_run_mission", RUN)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_y17_3_rb_complex_p27_point_and_matches_prior():
    mod = _load()
    raw = mod.run_experiment()
    assert raw["decision"] == "SUPPORTED"
    assert raw["interventions"]["do(Rb=0)"]["cycd0_reaches_complex_attractor"] is True
    assert raw["interventions"]["do(Rb=0)"]["cycd0_attractor_periods"] == [8]
    assert raw["p27_secondary_point_preserved"] is True
    assert raw["prior_match"]["types_rb_match"] is True
    assert raw["prior_match"]["types_p27_match"] is True
    status, checks = mod.deterministic_verify(raw)
    assert status == "PASS"
    assert "decision matches kill criterion" in checks
    assert raw["config"]["y17_writes"] is False
