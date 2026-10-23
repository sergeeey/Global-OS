"""Acceptance: wheel-packaged schemas/migrations/cedar resolve without repo checkout."""

from __future__ import annotations

from pathlib import Path

from global_os.adapters.storage.sql import _migrations_dir
from global_os.contracts.validate import SCHEMAS_DIR
from global_os.kernel.policy.engine import PolicyEngine, _resolve_cedar_path


def test_schemas_dir_resolves_with_json_schemas() -> None:
    assert SCHEMAS_DIR.is_dir()
    assert any(SCHEMAS_DIR.glob("*.schema.json"))


def test_migrations_dir_resolves_with_sql() -> None:
    root = _migrations_dir()
    assert root.is_dir()
    assert any(root.glob("*.sql"))


def test_cedar_policy_resolves_and_engine_loads() -> None:
    path = _resolve_cedar_path()
    assert path.exists(), f"missing cedar at {path}"
    engine = PolicyEngine()
    assert engine.cedar_path.exists()
    # Checkout or packaged: file must be non-empty bootstrap.
    assert Path(engine.cedar_path).stat().st_size > 0
