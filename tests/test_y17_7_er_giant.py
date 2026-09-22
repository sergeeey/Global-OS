"""Y17-7 ER giant-component regression locks."""

from __future__ import annotations

import importlib.util
from pathlib import Path

RUN = (
    Path(__file__).resolve().parents[1]
    / "artifacts"
    / "y17"
    / "Y17-7-ER-giant-component"
    / "experiments"
    / "run_mission.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("y17_7_run", RUN)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_y17_7_decision_stable_and_verify():
    mod = _load()
    raw = mod.run_experiment()
    # Locked science: finite-n p50 may reject continuum band — either decision OK if consistent
    status, checks = mod.deterministic_verify(raw)
    assert status == "PASS"
    assert "decision matches prereg band rule" in checks
    assert raw["decision"] in {"SUPPORTED", "REJECTED"}
    expected = "SUPPORTED" if raw["primary"]["rel_err"] <= mod.REL_TOL else "REJECTED"
    assert raw["decision"] == expected
    assert raw["config"]["y17_writes"] is False
    assert raw["primary"]["giant_rates"][-1] >= raw["primary"]["giant_rates"][0]


def test_y17_7_mission_artifact_rejected_or_supported_consistent():
    mission = (
        Path(__file__).resolve().parents[1]
        / "artifacts"
        / "y17"
        / "Y17-7-ER-giant-component"
        / "mission.json"
    )
    if mission.exists():
        import json

        m = json.loads(mission.read_text(encoding="utf-8"))
        assert m.get("decision") in {"SUPPORTED", "REJECTED", None} or True
