"""Y17-6 game-theoretic fictitious-play regression locks."""

from __future__ import annotations

import importlib.util
from pathlib import Path

RUN = (
    Path(__file__).resolve().parents[1]
    / "artifacts"
    / "y17"
    / "Y17-6-RPS-fictitious-play"
    / "experiments"
    / "run_mission.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("y17_6_run", RUN)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_y17_6_fp_beats_pure_baseline():
    mod = _load()
    raw = mod.run_experiment()
    assert raw["decision"] == "SUPPORTED"
    assert raw["primary"]["ratio_fp_over_pure"] <= mod.MCID_RATIO
    status, checks = mod.deterministic_verify(raw)
    assert status == "PASS"
    assert "decision matches prereg MCID rule" in checks
    assert raw["config"]["y17_writes"] is False


def test_y17_6_pure_more_exploitable_than_nash():
    mod = _load()
    pure = mod.pure_baseline(0, mod.T_ROUNDS)
    assert mod.exploitability(pure) > mod.exploitability(mod.NASH)
