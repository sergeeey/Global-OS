from __future__ import annotations

import pytest

from global_os.adapters.storage import (
    PostgresUnavailable,
    connect_durable_store,
    connect_sqlite,
)
from global_os.evals.environment import summarize_h_env_001, summarize_h_rsn_001


def test_h_env_001_harness_inconclusive_not_confirmed():
    report = summarize_h_env_001()
    assert report["id"] == "H-ENV-001"
    assert report["fidelity"] == "synthetic_deterministic"
    assert report["verdict"] == "INCONCLUSIVE_NEEDS_REAL_MODEL"
    assert len(report["environment_sweep"]) == 5
    assert report["metrics"]["env_marginal_A_to_E"] > 0
    # Must not claim scientific confirmation
    assert report["verdict"] != "CONFIRMED"


def test_h_rsn_001_harness_preserves_verification_tier():
    report = summarize_h_rsn_001()
    assert report["id"] == "H-RSN-001"
    assert report["gos_i23_holds"] is True
    assert report["verdict"] == "INCONCLUSIVE_NEEDS_REAL_MODEL"
    assert report["trials"]["adaptive_easy"]["verification_tier"] == 3
    assert report["trials"]["fixed_high"]["verification_tier"] == 3


def test_postgres_url_fails_closed_without_server(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    conn = connect_durable_store(None)
    assert conn is not None
    conn.close()
    # psycopg may be installed — still must not fall back to SQLite on unreachable Postgres
    with pytest.raises(PostgresUnavailable, match="refusing silent SQLite fallback"):
        connect_durable_store("postgresql://127.0.0.1:1/gos")
    # sqlite explicit still works
    s = connect_durable_store("sqlite:///:memory:")
    assert s is not None
    s.close()
    # connect_sqlite still the local path
    assert connect_sqlite(":memory:") is not None


def test_postgres_url_fails_closed_without_psycopg(monkeypatch: pytest.MonkeyPatch):
    import builtins
    import sys

    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        if name == "psycopg" or name.startswith("psycopg."):
            raise ImportError("mocked missing psycopg")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", fake_import)
    # Drop cached module so import path is exercised
    sys.modules.pop("psycopg", None)
    with pytest.raises(PostgresUnavailable, match="psycopg is not installed"):
        connect_durable_store("postgresql://localhost/gos")
