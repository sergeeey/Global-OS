"""Acceptance guards for MINIMAL-STACK-v1 product contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "artifacts" / "pilot" / "minimal_stack"
CONTRACT = PACK / "MINIMAL_STACK_CONTRACT.md"
LOCK_PATH = PACK / "LOCK.json"


def test_minimal_stack_lock_sealed():
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    assert lock["protocol_id"] == "MINIMAL-STACK-v1"
    assert lock["status"] == "LOCKED"
    assert lock["parent"]["gos_incremental"] == "NOT_SHOWN"
    assert lock["parent"]["m2"] == "CLOSED"
    assert lock["parent"]["production_proven"] == 0
    assert lock["parent"]["ablation_protocol"] == "ARCH-ABLATION-MECH-v1"
    assert lock["role"] == "reliability_substrate_not_mission_endgame"
    assert lock["primary_mission"] == "autonomous_goal_achiever"
    assert lock["default_product_stack"] == ["G1", "G2", "G3"]
    assert "Gfull.durable_runner" in lock["opt_in_layers"]
    assert "soften_pilot3_attr" in lock["forbidden"]
    assert "reopen_m2" in lock["forbidden"]
    assert "claim_gfull_default" in lock["forbidden"]
    assert "replace_mission_with_substrate_only_product" in lock["forbidden"]


def test_contract_maps_failure_classes_and_default_stack():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "MINIMAL-STACK-v1" in text
    assert "DEFAULT = G1 + G2 + G3" in text
    assert "OPT-IN" in text
    for needle in (
        "Silent goal mutation",
        "Negative-result erasure",
        "ToolSuccess treated as WorldSuccess",
        "Privilege expansion",
        "VERIFIED_CURRENT_VALUE",
        "NOT_SHOWN",
        "PROCESS_DISCIPLINE_SUFFICES",
        "M2 (org superiority)",
        "CLOSED",
        "PRODUCTION_PROVEN",
        "Autonomous Work Operating System",
        "reliability substrate",
        "≠ new product mission",
        "autonomous goal-achiever",
    ):
        assert needle in text, needle
    # Must not claim ATTR overturn; must not swap mission for substrate
    assert "overturn Pilot 3 ATTR" in text or "does not** overturn" in text or "do not** overturn" in text
    assert "Forbidden swap" in text or "replace the primary mission" in text


def test_roadmap_points_to_minimal_stack():
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    assert "minimal_stack" in roadmap or "MINIMAL-STACK" in roadmap
    assert "NOT_SHOWN" in roadmap
    assert "CLOSED" in roadmap


def test_capability_matrix_records_minimal_stack():
    matrix = json.loads((ROOT / "docs" / "capability_matrix.json").read_text(encoding="utf-8"))
    entry = matrix["research_campaigns"]["MINIMAL_STACK_V1"]
    assert entry["status"] == "LOCKED"
    assert entry["default_stack"] == ["G1", "G2", "G3"]
    assert entry["pilot3_attr_preserved"] == "NOT_SHOWN"
    assert entry["m2_org_path"] == "CLOSED"
    assert entry["production_proven"] == 0
