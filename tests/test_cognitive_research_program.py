"""Acceptance tests for LH-COGNITIVE-v1 (external object ≠ sum harness)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("numpy")
pytest.importorskip("scipy")

from global_os.evals.survival.cognitive_research_program import (
    run_cognitive_research_program,
)
from global_os.evals.survival.research_program import (
    run_persistent_research_program,
)


def test_cognitive_preflight_compressed_passes(tmp_path: Path) -> None:
    root = tmp_path / "cognitive_preflight"
    r = run_cognitive_research_program(
        mode="cognitive_preflight", artifact_root=root, sleep=False
    )
    assert r.m15_claimed is False
    assert r.passed is True, [(c.id, c.passed, c.detail) for c in r.criteria if not c.passed]
    assert r.fidelity.startswith("COGNITIVE_PREFLIGHT")
    assert r.provenance.get("workload_class") == "EXTERNAL_RESEARCH_OBJECT"
    assert (root / "missions" / "object" / "LOCKED_OBJECT.json").is_file()
    assert (root / "missions" / "review" / "TERMINAL_REVIEW_PACK.json").is_file()
    names = {c.id for c in r.criteria}
    assert "primary_mission_not_sum_harness" in names
    assert "min_distinct_evidence_artifacts" in names


def test_durability_harness_still_uses_sum_missions(tmp_path: Path) -> None:
    """Honesty: old program remains deterministic sum-class (Variant A surface)."""
    root = tmp_path / "durability"
    r = run_persistent_research_program(mode="preflight", artifact_root=root, sleep=False)
    assert any(m.get("mission_id") == "LH-1-parity-supported" for m in r.mission_decisions)
    blob = (root / "missions" / "LH-1-parity-supported" / "preregistration.json").read_text(
        encoding="utf-8"
    )
    assert "sum(1..20)" in blob


def test_cognitive_wall_requires_gates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOS_REQUIRE_48H", raising=False)
    monkeypatch.delenv("GOS_START_RESEARCH_48H", raising=False)
    with pytest.raises(RuntimeError, match="GOS_REQUIRE_48H"):
        run_cognitive_research_program(
            mode="cognitive_wall_48h", artifact_root=tmp_path / "w", sleep=False
        )
