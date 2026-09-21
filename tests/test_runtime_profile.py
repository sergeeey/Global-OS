from __future__ import annotations

import pytest

from global_os.adapters.authority.rust_client import find_gos_authority_bin
from global_os.runtime.context import RuntimeContext
from global_os.runtime.profile import (
    ProductionProfileError,
    apply_production_guards,
    resolve_authority_backend,
    resolve_profile,
)


def test_dev_profile_defaults_to_python(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GOS_PROFILE", raising=False)
    monkeypatch.delenv("GOS_AUTHORITY_BACKEND", raising=False)
    assert resolve_profile() == "dev"
    assert resolve_authority_backend(profile="dev") == "python"
    ctx = RuntimeContext(profile="dev")
    assert ctx.authority_backend == "python"
    assert ctx.authority._backend == "python"


def test_production_defaults_to_rust_and_probes_binary(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GOS_AUTHORITY_BACKEND", raising=False)
    assert resolve_authority_backend(profile="production") == "rust"
    if find_gos_authority_bin() is None:
        with pytest.raises(ProductionProfileError, match="gos-authority"):
            RuntimeContext(profile="production")
        return
    ctx = RuntimeContext(profile="production")
    assert ctx.authority_backend == "rust"
    assert ctx.authority._backend == "rust"


def test_production_forbids_python_backend():
    with pytest.raises(ProductionProfileError, match="forbids python"):
        apply_production_guards(profile="production", backend="python")


def test_env_gos_authority_backend_wins_in_dev(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GOS_AUTHORITY_BACKEND", "rust")
    if find_gos_authority_bin() is None:
        pytest.skip("gos-authority not built")
    assert resolve_authority_backend(profile="dev") == "rust"
    ctx = RuntimeContext(profile="dev")
    assert ctx.authority_backend == "rust"


def test_explicit_backend_overrides_profile(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GOS_AUTHORITY_BACKEND", raising=False)
    assert resolve_authority_backend(profile="production", explicit="python") == "python"
