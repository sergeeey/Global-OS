from __future__ import annotations

from pathlib import Path

from global_os.world.tools import run_repo_audit


def test_repo_audit_read_only_on_self():
    root = Path(__file__).resolve().parents[1]
    report = run_repo_audit(root)
    assert report["read_only"] is True
    assert report["modified_target"] is False
    assert report["scan"]["has_constitution"] is True
    assert report["scan"]["has_schemas"] is True
    ids = {f["id"] for f in report["findings"]}
    assert "f_constitution" in ids
    assert "f_schemas" in ids
