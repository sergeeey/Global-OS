"""Acceptance: Pilot 3 terminal decision pack exists and is honest."""

from __future__ import annotations

import json
from pathlib import Path

PACK = Path("artifacts/pilot/pilot3_independent")


def test_pilot3_decision_terminal() -> None:
    decision = (PACK / "DECISION.md").read_text(encoding="utf-8")
    assert "TERMINAL" in decision
    assert "PROCESS_DISCIPLINE_SUFFICES" in decision
    assert "NOT_SHOWN" in decision
    assert "H-PILOT3-EPI" in decision
    assert "H-PILOT3-ENG" in decision
    assert "INCONCLUSIVE" in decision
    lock = json.loads((PACK / "LOCK.json").read_text(encoding="utf-8"))
    assert lock["status"] == "TERMINAL"
    score = json.loads((PACK / "score/SCOREBOARD.json").read_text(encoding="utf-8"))
    assert score["hypotheses"]["H-PILOT3-ATTR"]["gos_incremental"] == "NOT_SHOWN"
    assert score["blind_map"] == {"P1": "C", "P2": "A", "P3": "B"}
    seal = json.loads((PACK / "arms/out_D/EVAL_SEAL.json").read_text(encoding="utf-8"))
    assert seal["summary"]["confirmed"] == 16
    assert (PACK / "arms/out_A/FINDINGS.md").is_file()
    assert (PACK / "arms/out_B/FINDINGS.md").is_file()
    assert (PACK / "arms/out_C/FINDINGS.md").is_file()
    accept = (PACK / "OPERATOR_ACCEPTANCE.md").read_text(encoding="utf-8")
    assert "NOT_SHOWN" in accept
    assert "CLOSED" in accept and "M2" in accept
    assert (PACK / "NEXT_ARCHITECTURE_ABLATION.md").is_file()
    assert "M2=CLOSED" in decision or "M2 = CLOSED" in decision
