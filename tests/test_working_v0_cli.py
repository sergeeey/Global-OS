"""User-level CLI acceptance for the read-only supervised repo-audit v0."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from global_os.cli import main


def _snapshot(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for child in sorted(path.rglob("*")):
        if child.is_file():
            rows.append(
                (
                    child.relative_to(path).as_posix(),
                    hashlib.sha256(child.read_bytes()).hexdigest(),
                )
            )
    return rows


def _repo(path: Path) -> None:
    (path / "contracts" / "schemas").mkdir(parents=True)
    (path / "tests").mkdir()
    (path / "CONSTITUTION.md").write_text("# constitution\n", encoding="utf-8")
    (path / "contracts" / "schemas" / "goal.json").write_text("{}", encoding="utf-8")
    (path / "tests" / "test_x.py").write_text("def test_x(): assert True\n", encoding="utf-8")


def test_cli_mission_run_valid_repo(tmp_path: Path, capsys) -> None:
    target = tmp_path / "repo"
    _repo(target)
    gos = tmp_path / ".gos"
    code = main(
        [
            "--root",
            str(gos),
            "mission",
            "run",
            "--goal",
            "Провести проверяемый read-only аудит репозитория",
            "--target",
            str(target),
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "terminal: SUCCEEDED" in out
    assert "verdict: SUCCEEDED" in out
    assert "report:" in out
    assert "trace:" in out
    run_id = next(gos.glob("missions/run_*")).name
    run_dir = gos / "missions" / run_id
    assert (run_dir / "REPORT.md").is_file()
    assert (run_dir / "delivery.json").is_file()
    assert (run_dir / "events.json").is_file()
    delivery = json.loads((run_dir / "delivery.json").read_text(encoding="utf-8"))
    assert delivery["terminal_status"] == "SUCCEEDED"


def test_cli_mission_run_empty_target_is_not_success(tmp_path: Path, capsys) -> None:
    target = tmp_path / "empty"
    target.mkdir()
    gos = tmp_path / ".gos"
    code = main(
        [
            "--root",
            str(gos),
            "mission",
            "run",
            "--goal",
            "audit empty target",
            "--target",
            str(target),
        ]
    )
    assert code == 3
    out = capsys.readouterr().out
    assert "terminal: INCONCLUSIVE" in out
    assert "verdict: INCONCLUSIVE" in out
    assert "SUCCEEDED" not in out


def test_cli_mission_run_missing_target_is_invalid(tmp_path: Path, capsys) -> None:
    gos = tmp_path / ".gos"
    code = main(
        [
            "--root",
            str(gos),
            "mission",
            "run",
            "--goal",
            "audit missing target",
            "--target",
            str(tmp_path / "missing"),
        ]
    )
    assert code == 3
    out = capsys.readouterr().out
    assert "terminal: INCONCLUSIVE" in out
    assert "verdict: INVALID_TARGET" in out
    assert "target is missing" in out

def test_cli_default_root_inside_target_is_rejected(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    target = tmp_path / "repo"
    _repo(target)
    before = _snapshot(target)
    monkeypatch.chdir(target)
    code = main(
        [
            "mission",
            "run",
            "--goal",
            "audit current target",
            "--target",
            ".",
        ]
    )
    assert code == 2
    out = capsys.readouterr().out
    assert "--root must be outside --target" in out
    assert not (target / ".gos").exists()
    assert _snapshot(target) == before


def test_cli_explicit_root_inside_target_is_rejected(
    tmp_path: Path, capsys
) -> None:
    target = tmp_path / "repo"
    _repo(target)
    before = _snapshot(target)
    code = main(
        [
            "--root",
            str(target / ".gos"),
            "mission",
            "run",
            "--goal",
            "audit current target",
            "--target",
            str(target),
        ]
    )
    assert code == 2
    assert "--root must be outside --target" in capsys.readouterr().out
    assert not (target / ".gos").exists()
    assert _snapshot(target) == before


def test_cli_external_root_keeps_target_unchanged(tmp_path: Path, capsys) -> None:
    target = tmp_path / "repo"
    _repo(target)
    before = _snapshot(target)
    code = main(
        [
            "--root",
            str(tmp_path / "state"),
            "mission",
            "run",
            "--goal",
            "audit repo",
            "--target",
            str(target),
        ]
    )
    assert code == 0
    assert "terminal: SUCCEEDED" in capsys.readouterr().out
    assert _snapshot(target) == before

def test_cli_mission_start_guard_rejects_inside_root(tmp_path: Path, capsys) -> None:
    target = tmp_path / "repo"
    _repo(target)
    before = _snapshot(target)
    goal = Path(__file__).resolve().parents[1] / "examples" / "goal_repo_audit.json"
    code = main(
        [
            "--root",
            str(target / ".gos"),
            "mission",
            "start",
            "--goal",
            str(goal),
            "--target",
            str(target),
        ]
    )
    assert code == 2
    assert "--root must be outside --target" in capsys.readouterr().out
    assert not (target / ".gos").exists()
    assert _snapshot(target) == before
