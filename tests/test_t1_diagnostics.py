"""Acceptance tests for post-T1 diagnostics (REJECT/MCID immutable)."""

from __future__ import annotations

import json
from pathlib import Path

from global_os.evals.trust.pack_v2 import PACK_V2_ID, freeze_pack_v2
from global_os.evals.trust.t1_diagnostics import (
    build_diagnostics,
    wilson_interval,
    write_diagnostics,
)

ROOT = Path(__file__).resolve().parents[1]
T1 = ROOT / "artifacts/safe_autonomy_t1"


def test_wilson_bounds() -> None:
    ci = wilson_interval(0, 150)
    assert ci["point"] == 0.0
    assert ci["low"] == 0.0
    assert ci["high"] is not None and float(ci["high"]) < 0.05


def test_diagnostics_do_not_change_reject(tmp_path: Path) -> None:
    # Copy minimal T1 artifacts
    import shutil

    src = T1
    dst = tmp_path / "t1"
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("POST_T1_DIAGNOSTICS", "PACK_V2", "__pycache__"),
    )
    report = build_diagnostics(artifact_root=dst)
    assert report["t1_verdict_unchanged"] == "REJECT"
    assert report["mcid_unchanged"] is True
    assert report["m15_reopened"] is False
    assert "A" in report["confidence_intervals"]["arms"]
    assert report["overblocking"]["summary"]["arm_C_fault_escaped"] == 0
    assert report["cost_decomposition"]["reject_link"]["frozen_reason"] == (
        "verifier_tax_2_0_completion"
    )
    paths = write_diagnostics(artifact_root=dst)
    assert paths["md"].is_file()


def test_pack_v2_sealed_freeze(tmp_path: Path) -> None:
    man = freeze_pack_v2(root=tmp_path)
    assert man["pack_id"] == PACK_V2_ID
    assert man["status"] == "FROZEN_UNSEEN"
    assert man["t1_rescoring_forbidden"] is True
    assert man["mcid_from_t1_residuals_forbidden"] is True
    sealed = tmp_path / "PACK_V2" / "sealed" / "sealed_pack.json"
    assert sealed.is_file()
    warning = (tmp_path / "PACK_V2" / "sealed" / "WARNING.txt").read_text(encoding="utf-8")
    assert "SEALED" in warning


def test_repo_revival_and_evidence_table_present() -> None:
    assert (T1 / "REVIVAL_TRIGGERS.json").is_file()
    assert (T1 / "T1_EVIDENCE_TABLE.md").is_file()
    trig = json.loads((T1 / "REVIVAL_TRIGGERS.json").read_text(encoding="utf-8"))
    assert trig["current_verdict"] == "REJECTED_IN_TESTED_SCOPE"
    assert "rewrite_t1_mcid_from_residuals" in trig["forbidden"]
