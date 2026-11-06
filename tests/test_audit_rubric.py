"""Tests for the frozen user-defined audit rubric runtime."""

from __future__ import annotations

import json
from pathlib import Path

from global_os.cli import main
from global_os.runtime.preprod.audit_rubric import (
    AuditRubricError,
    aggregate,
    evaluate_criterion,
    load_rubric,
    validate_result,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "docs" / "audit_rubric" / "examples"


def _repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "README.md").write_text("# repo\n", encoding="utf-8")
    (path / "contracts" / "schemas").mkdir(parents=True)
    (path / "tests").mkdir()
    (path / "CONSTITUTION.md").write_text("# constitution\n", encoding="utf-8")
    (path / "contracts" / "schemas" / "goal.json").write_text("{}", encoding="utf-8")
    (path / "tests" / "test_x.py").write_text("def test_x(): assert True\n", encoding="utf-8")


def _rubric(*criteria: dict, optional_issues: str = "MIXED") -> dict:
    return {
        "schema_version": "audit-rubric/1",
        "rubric_id": "test-rubric",
        "goal": "test goal",
        "criteria": list(criteria),
        "aggregation_policy": {
            "mode": "required_all_pass",
            "optional_issues": optional_issues,
            "unknown": "UNKNOWN",
            "fail": "FAIL",
        },
    }


def _criterion(
    cid: str,
    kind: str,
    locator: str,
    *,
    required: bool = True,
    on_missing: str = "UNKNOWN",
    rule: str = "evidence_supports",
) -> dict:
    return {
        "id": cid,
        "statement": f"criterion {cid} is supported by evidence",
        "expected_evidence": {"description": cid, "kind": kind, "locator": locator},
        "acceptance_rule": {
            "on_missing_evidence": on_missing,
            "on_conflict": "FAIL",
            "rule": rule,
        },
        "required": required,
    }


def _write(path: Path, value: dict) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_frozen_examples_load() -> None:
    assert load_rubric(EXAMPLES / "y17.rubric.json")["rubric_id"] == "y17-research-handoff-v1"
    assert load_rubric(EXAMPLES / "mcp_bouncer.rubric.json")["rubric_id"] == "mcp-bouncer-operational-v1"


def test_malformed_rubric_rejected_before_mission(tmp_path: Path, capsys) -> None:
    target = tmp_path / "repo"
    _repo(target)
    bad = tmp_path / "bad.json"
    bad.write_text(
        json.dumps(
            {
                "schema_version": "audit-rubric/1",
                "rubric_id": "bad",
                "goal": "bad",
                "criteria": [],
                "aggregation_policy": {
                    "mode": "required_all_pass",
                    "optional_issues": "MIXED",
                    "unknown": "UNKNOWN",
                    "fail": "FAIL",
                },
            }
        ),
        encoding="utf-8",
    )
    gos = tmp_path / ".gos"
    code = main(
        [
            "--root",
            str(gos),
            "mission",
            "run",
            "--goal",
            "bad rubric",
            "--target",
            str(target),
            "--rubric",
            str(bad),
        ]
    )
    assert code == 2
    assert "error:" in capsys.readouterr().out
    assert not gos.exists()


def test_missing_evidence_unknown(tmp_path: Path) -> None:
    criterion = _criterion("missing", "file", "absent.txt")
    result = evaluate_criterion(tmp_path, criterion)
    assert result["verdict"] == "UNKNOWN"
    assert result["missing_evidence"]


def test_file_presence_pass_and_missing_explicit_fail(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("ok", encoding="utf-8")
    present = evaluate_criterion(
        tmp_path, _criterion("present", "file", "README.md")
    )
    assert present["verdict"] == "PASS"
    assert present["evidence_refs"]
    missing = evaluate_criterion(
        tmp_path,
        _criterion("missing", "file", "absent.txt", on_missing="FAIL"),
    )
    assert missing["verdict"] == "FAIL"


def test_conflicting_file_directory_is_not_pass(tmp_path: Path) -> None:
    (tmp_path / "README.md").mkdir()
    result = evaluate_criterion(
        tmp_path, _criterion("conflict", "file", "README.md")
    )
    assert result["verdict"] == "FAIL"
    assert "conflict" in result["reason"].lower()


def test_aggregation_required_pass_fail_unknown_and_optional_mixed() -> None:
    rubric = _rubric(
        _criterion("required-pass", "file", "README.md"),
        _criterion("optional-fail", "file", "missing.txt", required=False),
    )
    results = [
        {"criterion_id": "required-pass", "verdict": "PASS"},
        {"criterion_id": "optional-fail", "verdict": "FAIL"},
    ]
    assert aggregate(rubric, results) == ("MIXED", ["optional-fail"])
    results[0]["verdict"] = "FAIL"
    assert aggregate(rubric, results)[0] == "FAIL"
    results[0]["verdict"] = "UNKNOWN"
    assert aggregate(rubric, results)[0] == "UNKNOWN"


def test_cli_rubric_separates_execution_and_audit(tmp_path: Path, capsys) -> None:
    target = tmp_path / "repo"
    _repo(target)
    rubric = _write(
        tmp_path / "rubric.json",
        _rubric(
            _criterion("readme", "file", "README.md"),
            _criterion("missing", "command", "pytest"),
        ),
    )
    gos = tmp_path / ".gos"
    code = main(
        [
            "--root",
            str(gos),
            "mission",
            "run",
            "--goal",
            "rubric mission",
            "--target",
            str(target),
            "--rubric",
            str(rubric),
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "terminal: SUCCEEDED" in out
    assert "execution_terminal: SUCCEEDED" in out
    assert "audit_verdict: UNKNOWN" in out
    assert "rubric_report:" in out
    run_dir = next(gos.glob("missions/run_*"))
    assert (run_dir / "RUBRIC_REPORT.md").is_file()
    result = json.loads((run_dir / "rubric_result.json").read_text(encoding="utf-8"))
    assert result["execution_terminal"] == "SUCCEEDED"
    assert result["audit_verdict"] == "UNKNOWN"


def test_cli_rubric_fail_does_not_fail_execution(tmp_path: Path, capsys) -> None:
    target = tmp_path / "repo"
    _repo(target)
    rubric = _write(
        tmp_path / "rubric.json",
        _rubric(
            _criterion("required-missing", "file", "absent.txt", on_missing="FAIL"),
        ),
    )
    gos = tmp_path / ".gos"
    code = main(
        [
            "--root",
            str(gos),
            "mission",
            "run",
            "--goal",
            "rubric mission",
            "--target",
            str(target),
            "--rubric",
            str(rubric),
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "execution_terminal: SUCCEEDED" in out
    assert "audit_verdict: FAIL" in out

def test_cli_rubric_pass_is_independent_of_execution(tmp_path: Path, capsys) -> None:
    target = tmp_path / "repo"
    _repo(target)
    rubric = _write(
        tmp_path / "rubric.json",
        _rubric(_criterion("readme", "file", "README.md")),
    )
    gos = tmp_path / ".gos"
    code = main(
        [
            "--root",
            str(gos),
            "mission",
            "run",
            "--goal",
            "rubric pass mission",
            "--target",
            str(target),
            "--rubric",
            str(rubric),
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "execution_terminal: SUCCEEDED" in out
    assert "audit_verdict: PASS" in out

def test_conflict_unknown_has_missing_evidence(tmp_path: Path) -> None:
    (tmp_path / "adir").mkdir()
    criterion = _criterion("conflict", "file", "adir")
    criterion["acceptance_rule"]["on_conflict"] = "UNKNOWN"
    result = evaluate_criterion(tmp_path, criterion)
    assert result["verdict"] == "UNKNOWN"
    assert result["missing_evidence"]


def test_aggregate_unresolved_excludes_required_fail(tmp_path: Path) -> None:
    rubric = _rubric(
        _criterion("required-fail", "file", "missing.txt", on_missing="FAIL"),
        _criterion("optional-unknown", "file", "missing2.txt", required=False),
    )
    results = [
        {"criterion_id": "required-fail", "verdict": "FAIL"},
        {"criterion_id": "optional-unknown", "verdict": "UNKNOWN"},
    ]
    assert aggregate(rubric, results) == ("FAIL", ["optional-unknown"])


def test_validate_result_rejects_forged_or_missing_criterion(tmp_path: Path) -> None:
    rubric = _rubric(_criterion("readme", "file", "README.md"))
    forged = {
        "schema_version": "audit-result/1",
        "rubric_id": "test-rubric",
        "execution_terminal": "SUCCEEDED",
        "audit_verdict": "PASS",
        "criterion_results": [
            {
                "criterion_id": "forged",
                "verdict": "PASS",
                "reason": "forged",
                "evidence_refs": [{"kind": "file", "ref": "README.md"}],
                "missing_evidence": [],
            }
        ],
        "unresolved": [],
    }
    try:
        validate_result(forged, rubric)
    except AuditRubricError:
        pass
    else:
        raise AssertionError("forged criterion was accepted")


def test_cli_conflict_unknown_does_not_crash(tmp_path: Path, capsys) -> None:
    target = tmp_path / "repo"
    _repo(target)
    (target / "adir").mkdir()
    criterion = _criterion("conflict", "file", "adir")
    criterion["acceptance_rule"]["on_conflict"] = "UNKNOWN"
    rubric = _write(tmp_path / "rubric.json", _rubric(criterion))
    gos = tmp_path / ".gos"
    code = main(
        [
            "--root",
            str(gos),
            "mission",
            "run",
            "--goal",
            "conflict rubric",
            "--target",
            str(target),
            "--rubric",
            str(rubric),
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "execution_terminal: SUCCEEDED" in out
    assert "audit_verdict: UNKNOWN" in out
    run_dir = next(gos.glob("missions/run_*"))
    assert (run_dir / "RUBRIC_REPORT.md").is_file()
    assert (run_dir / "rubric_result.json").is_file()


def test_invalid_utf8_rubric_rejected_before_mission(tmp_path: Path, capsys) -> None:
    target = tmp_path / "repo"
    _repo(target)
    bad = tmp_path / "bad.json"
    bad.write_bytes(b"\xff\xfe\x00")
    gos = tmp_path / ".gos"
    code = main(
        [
            "--root",
            str(gos),
            "mission",
            "run",
            "--goal",
            "bad encoding",
            "--target",
            str(target),
            "--rubric",
            str(bad),
        ]
    )
    assert code == 2
    assert "error:" in capsys.readouterr().out
    assert not gos.exists()

def test_unreadable_file_is_unknown(tmp_path: Path, monkeypatch) -> None:
    locked = tmp_path / "locked.bin"
    locked.write_bytes(b"secret")
    original = Path.read_bytes

    def deny(self: Path) -> bytes:
        if self.name == "locked.bin":
            raise PermissionError("share denied")
        return original(self)

    monkeypatch.setattr(Path, "read_bytes", deny)
    result = evaluate_criterion(
        tmp_path, _criterion("locked", "file", "locked.bin")
    )
    assert result["verdict"] == "UNKNOWN"
    assert result["missing_evidence"] == ["unreadable: locked.bin"]
    assert result["evidence_refs"] == []

