"""Y18 failure-mode dogfood — four distinct failure classes for freeze readiness."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "artifacts" / "hardening" / "dogfood_fm"


def _run(script: Path) -> None:
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    proc = subprocess.run([sys.executable, str(script)], cwd=str(ROOT), env=env, check=False)
    assert proc.returncode == 0, script


def test_y18_1_evidence_invalidation():
    _run(SUITE / "Y18-1-evidence-invalidation" / "execute_mission.py")
    m = json.loads((SUITE / "Y18-1-evidence-invalidation" / "mission.json").read_text())
    assert m["decision"] == "SUPPORTED"


def test_y18_2_effect_discrepancy():
    _run(SUITE / "Y18-2-effect-discrepancy" / "execute_mission.py")
    m = json.loads((SUITE / "Y18-2-effect-discrepancy" / "mission.json").read_text())
    assert m["decision"] == "SUPPORTED"


def test_y18_3_authority_boundary():
    _run(SUITE / "Y18-3-authority-boundary" / "execute_mission.py")
    m = json.loads((SUITE / "Y18-3-authority-boundary" / "mission.json").read_text())
    assert m["decision"] == "SUPPORTED"


def test_y18_4_provider_degradation():
    _run(SUITE / "Y18-4-provider-degradation" / "execute_mission.py")
    m = json.loads((SUITE / "Y18-4-provider-degradation" / "mission.json").read_text())
    assert m["decision"] == "SUPPORTED"
    v = json.loads((SUITE / "Y18-4-provider-degradation" / "verification.json").read_text())
    assert v["deterministic_status"] == "PASS"
    assert v["provider_status"] in {"BLOCKED_ENVIRONMENT", "AVAILABLE"}
    exp = json.loads(
        (SUITE / "Y18-4-provider-degradation" / "experiments" / "metrics" / "run.json").read_text()
    )
    assert exp["fabricated_live_iv"] is False
    assert exp["outage_raised"] is True
    assert exp["null_count"] >= 1
