"""Acceptance: org A/B dogfood dataset reaches N≥5 with decomposability tags."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/workspace")
DATASET = ROOT / "artifacts" / "hardening" / "org_ab_dataset.json"


def test_org_ab_dataset_n_at_least_5_with_decomposability():
    assert DATASET.exists(), "org_ab_dataset.json missing — run artifacts/hardening/run_org_ab_dataset.py"
    report = json.loads(DATASET.read_text(encoding="utf-8"))
    assert report["n_tasks"] >= 5, f"need N≥5, got {report['n_tasks']}"
    assert report["scientific_claim_accepted"] is False
    assert "H_ORG" not in report["verdict"] or "NOT_CLAIMED" in report["verdict"]
    assert report["verdict"] != "SUPPORTED"
    tasks = report["tasks"]
    assert len(tasks) == report["n_tasks"]
    for t in tasks:
        assert t["decomposability"] in {"HIGH", "MEDIUM", "LOW"}
        assert "class" in t
        assert t["A"]["mode"] == "A_single_solver"
        assert t["B"]["mode"] == "B_manager_specialized_workers"
        assert "same_decision" in t["comparison"]
    assert "by_decomposability" in report
    assert set(report["by_decomposability"].keys()) >= {"HIGH"}
    # must include REJECTED scientific path (Y17-2) so org does not only see wins
    decisions = {t["A"]["decision"] for t in tasks}
    assert "REJECTED" in decisions or any("Y17-2" in t["task"] for t in tasks)


def test_org_ab_aggregate_rates_in_unit_interval():
    report = json.loads(DATASET.read_text(encoding="utf-8"))
    agg = report["aggregate"]
    for key in ("same_decision_rate", "B_information_loss_rate", "B_duplicate_work_rate"):
        assert 0.0 <= agg[key] <= 1.0
