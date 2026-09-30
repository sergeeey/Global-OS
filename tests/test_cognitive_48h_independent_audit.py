"""Tests for LH-COGNITIVE freeze + independent audit contour."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

MOD_PATH = (
    Path(__file__).resolve().parents[1]
    / "artifacts"
    / "hardening"
    / "audit_cognitive_48h"
    / "freeze_and_audit.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("freeze_and_audit", MOD_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def fa():
    return _load()


def _minimal_wall(root: Path, fa, *, wall_s: float = 172801.0, passed: bool = True) -> None:
    wall = root / "artifacts/hardening/long_horizon_48h/windows_cognitive_wall_48h"
    pre = root / "artifacts/hardening/long_horizon_48h/windows_cognitive_preflight"
    smoke = root / "artifacts/hardening/long_horizon_48h/os_kill_smoke_windows_cognitive"
    for d in (wall, pre, smoke):
        d.mkdir(parents=True)
    criteria = [{"id": f"c{i}", "passed": True, "detail": "ok"} for i in range(5)]
    report = {
        "mode": "cognitive_wall_48h",
        "fidelity": "COGNITIVE_WALL_CLOCK_48H",
        "passed": passed,
        "wall_seconds": wall_s,
        "m15_claimed": False,
        "criteria": criteria,
        "notes": "LH-COGNITIVE-v1. M1.5 not claimed by this report alone.",
        "contract": {"workload_class": "EXTERNAL_RESEARCH_OBJECT"},
        "provenance": {
            "git_sha": fa.EXAM_SHA,
            "workload_class": "EXTERNAL_RESEARCH_OBJECT",
        },
    }
    (wall / "program_report.json").write_text(json.dumps(report), encoding="utf-8")
    (wall / "PASS_CRITERIA.json").write_text(
        json.dumps({"passed": passed, "criteria": criteria, "m15_claimed": False}),
        encoding="utf-8",
    )
    (wall / "EXAM_START.json").write_text("{}", encoding="utf-8")
    (wall / "missions" / "object").mkdir(parents=True)
    (wall / "missions" / "review").mkdir(parents=True)
    (wall / "missions" / "evidence").mkdir(parents=True)
    (wall / "missions" / "object" / "LOCKED_OBJECT.json").write_text(
        json.dumps(
            {
                "object_id": "EXT-JAIN-WALLACE-2019-ATTN-EXPLAIN",
                "forbidden_primary_criterion": "sum(1..20)==210",
            }
        ),
        encoding="utf-8",
    )
    (wall / "missions" / "review" / "TERMINAL_REVIEW_PACK.json").write_text("{}", encoding="utf-8")
    for i in range(5):
        (wall / "missions" / "evidence" / f"e{i}.json").write_text("{}", encoding="utf-8")
    (pre / "program_report.json").write_text(
        json.dumps(
            {
                "passed": True,
                "fidelity": "COGNITIVE_PREFLIGHT_WALL",
                "m15_claimed": False,
            }
        ),
        encoding="utf-8",
    )
    (smoke / "os_kill_result.json").write_text(json.dumps({"passed": True}), encoding="utf-8")


def test_freeze_and_audit_pass(tmp_path: Path, fa) -> None:
    _minimal_wall(tmp_path, fa)
    freeze_root = tmp_path / "freeze"
    fa.freeze_pack(
        repo_root=tmp_path,
        freeze_root=freeze_root,
        sources=[
            "artifacts/hardening/long_horizon_48h/windows_cognitive_wall_48h",
            "artifacts/hardening/long_horizon_48h/windows_cognitive_preflight",
            "artifacts/hardening/long_horizon_48h/os_kill_smoke_windows_cognitive",
        ],
    )
    review = fa.audit_freeze(freeze_root)
    fa.write_audit_outputs(tmp_path / "out", review)
    assert review["summary"]["all_gates_passed"] is True
    assert review["m15_recommendation"] == "M1.5_CANDIDATE_SCOPE_LIMITED"
    assert review["m15_claimed_by_auditor"] is False
    assert (tmp_path / "out" / "INDEPENDENT_REVIEW.json").is_file()


def test_audit_fails_short_wall(tmp_path: Path, fa) -> None:
    _minimal_wall(tmp_path, fa, wall_s=1000.0)
    freeze_root = tmp_path / "freeze"
    fa.freeze_pack(
        repo_root=tmp_path,
        freeze_root=freeze_root,
        sources=[
            "artifacts/hardening/long_horizon_48h/windows_cognitive_wall_48h",
            "artifacts/hardening/long_horizon_48h/windows_cognitive_preflight",
            "artifacts/hardening/long_horizon_48h/os_kill_smoke_windows_cognitive",
        ],
    )
    review = fa.audit_freeze(freeze_root)
    assert review["summary"]["all_gates_passed"] is False
    assert review["m15_recommendation"] == "M1.5_NOT_CLAIMED"
    failed = {g["id"] for g in review["gates"] if not g["passed"]}
    assert "wall_seconds_hard_gate" in failed
