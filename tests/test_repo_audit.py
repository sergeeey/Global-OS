from __future__ import annotations

from pathlib import Path

from global_os.world.tools import run_repo_audit
from global_os.world.tools.repo_audit import (
    scan_forbidden_patterns,
    scan_invariant_coverage,
    scan_provider_boundary,
    scan_schema_inventory,
)


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


def test_repo_audit_deep_invariant_and_boundary():
    root = Path(__file__).resolve().parents[1]
    report = run_repo_audit(root, depth="deep")
    assert report["depth"] == "deep"
    assert report["audit_kind"] == "deterministic_static"
    assert report["deep"] is not None
    assert report["deep"]["invariants"]["coverage"] == 1.0
    assert report["deep"]["invariants"]["missing"] == []
    assert report["deep"]["schemas"]["count"] >= 1
    assert report["deep"]["provider_boundary"]["violation_count"] == 0
    assert report["deep"]["forbidden_patterns"]["hit_count"] == 0
    ids = {f["id"] for f in report["findings"]}
    assert "f_invariants_complete" in ids
    assert "f_provider_boundary_clean" in ids
    assert "f_schema_inventory" in ids


def test_repo_audit_structure_skips_deep():
    root = Path(__file__).resolve().parents[1]
    report = run_repo_audit(root, depth="structure")
    assert report["depth"] == "structure"
    assert report["deep"] is None
    ids = {f["id"] for f in report["findings"]}
    assert "f_invariants_complete" not in ids


def test_deep_scanners_on_fixture_tree(tmp_path: Path):
    (tmp_path / "CONSTITUTION.md").write_text("# partial\nGOS-I01\n", encoding="utf-8")
    (tmp_path / "contracts" / "schemas").mkdir(parents=True)
    (tmp_path / "contracts" / "schemas" / "goal.schema.json").write_text("{}", encoding="utf-8")
    bad = tmp_path / "src" / "evil.py"
    bad.parent.mkdir(parents=True)
    bad.write_text("import openai\nagent.execute_anything()\n", encoding="utf-8")

    inv = scan_invariant_coverage(tmp_path)
    assert "GOS-I01" in inv["found"]
    assert "GOS-I25" in inv["missing"]

    forbidden = scan_forbidden_patterns(tmp_path)
    assert forbidden["hit_count"] >= 1

    boundary = scan_provider_boundary(tmp_path)
    assert boundary["violation_count"] >= 1

    schemas = scan_schema_inventory(tmp_path)
    assert schemas["count"] == 1

    report = run_repo_audit(tmp_path, depth="deep")
    ids = {f["id"] for f in report["findings"]}
    assert "f_invariants_missing" in ids
    assert any(i.startswith("f_forbidden_") for i in ids)
    assert any(i.startswith("f_provider_boundary_") and i != "f_provider_boundary_clean" for i in ids)
