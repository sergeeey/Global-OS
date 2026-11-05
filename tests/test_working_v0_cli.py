"""User-level CLI acceptance for the read-only supervised repo-audit v0."""

from __future__ import annotations

import json
from pathlib import Path

from global_os.cli import main


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
