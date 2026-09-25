"""Y18 failure-mode dogfood — four distinct failure classes for freeze readiness."""

from __future__ import annotations

import json
from pathlib import Path

from global_os.evals.research.mission_isolation import run_mission_isolated

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "artifacts" / "hardening" / "dogfood_fm"


def test_y18_1_evidence_invalidation(tmp_path: Path):
    art = run_mission_isolated(ROOT, SUITE / "Y18-1-evidence-invalidation", tmp_path=tmp_path)
    m = json.loads((art / "mission.json").read_text())
    assert m["decision"] == "SUPPORTED"


def test_y18_2_effect_discrepancy(tmp_path: Path):
    art = run_mission_isolated(ROOT, SUITE / "Y18-2-effect-discrepancy", tmp_path=tmp_path)
    m = json.loads((art / "mission.json").read_text())
    assert m["decision"] == "SUPPORTED"


def test_y18_3_authority_boundary(tmp_path: Path):
    art = run_mission_isolated(ROOT, SUITE / "Y18-3-authority-boundary", tmp_path=tmp_path)
    m = json.loads((art / "mission.json").read_text())
    assert m["decision"] == "SUPPORTED"


def test_y18_4_provider_degradation(tmp_path: Path):
    art = run_mission_isolated(ROOT, SUITE / "Y18-4-provider-degradation", tmp_path=tmp_path)
    m = json.loads((art / "mission.json").read_text())
    assert m["decision"] == "SUPPORTED"
    v = json.loads((art / "verification.json").read_text())
    assert v["deterministic_status"] == "PASS"
    assert v["provider_status"] in {"BLOCKED_ENVIRONMENT", "AVAILABLE"}
    exp = json.loads((art / "experiments" / "metrics" / "run.json").read_text())
    assert exp["fabricated_live_iv"] is False
    assert exp["outage_raised"] is True
    assert exp["null_count"] >= 1
