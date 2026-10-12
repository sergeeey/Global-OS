from __future__ import annotations

import pytest

from global_os.adapters.authority.rust_client import find_gos_authority_bin
from global_os.kernel.action_gateway import LegacyExecutionTokenForbidden, ToolGateway
from global_os.runtime.context import RuntimeContext
from global_os.runtime.events.ledger import EventLedger
from global_os.runtime.profile import (
    ProductionProfileError,
    apply_production_guards,
    require_production_secrets,
    resolve_authority_backend,
    resolve_profile,
)


def _set_production_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOS_EXECUTION_TOKEN_SECRET", "prod-exec-secret-test-only-32b!!")
    monkeypatch.setenv("GOS_APPROVAL_SIGNING_SECRET", "prod-approval-secret-test-only!!")


def test_dev_profile_defaults_to_python(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GOS_PROFILE", raising=False)
    monkeypatch.delenv("GOS_AUTHORITY_BACKEND", raising=False)
    assert resolve_profile() == "dev"
    assert resolve_authority_backend(profile="dev") == "python"
    ctx = RuntimeContext(profile="dev")
    assert ctx.authority_backend == "python"
    assert ctx.authority._backend == "python"
    assert ctx.gateway._allow_legacy_tokens is True


def test_production_defaults_to_rust_and_probes_binary(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GOS_AUTHORITY_BACKEND", raising=False)
    _set_production_secrets(monkeypatch)
    assert resolve_authority_backend(profile="production") == "rust"
    if find_gos_authority_bin() is None:
        with pytest.raises(ProductionProfileError, match="gos-authority"):
            RuntimeContext(profile="production")
        return
    ctx = RuntimeContext(profile="production")
    assert ctx.authority_backend == "rust"
    assert ctx.authority._backend == "rust"
    assert ctx.gateway._allow_legacy_tokens is False


def test_production_forbids_python_backend(monkeypatch: pytest.MonkeyPatch):
    _set_production_secrets(monkeypatch)
    with pytest.raises(ProductionProfileError, match="forbids python"):
        apply_production_guards(profile="production", backend="python")


def test_production_requires_execution_token_secret(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GOS_EXECUTION_TOKEN_SECRET", raising=False)
    monkeypatch.setenv("GOS_APPROVAL_SIGNING_SECRET", "prod-approval-secret-test-only!!")
    with pytest.raises(ProductionProfileError, match="GOS_EXECUTION_TOKEN_SECRET"):
        require_production_secrets()


def test_production_requires_approval_signing_secret(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GOS_EXECUTION_TOKEN_SECRET", "prod-exec-secret-test-only-32b!!")
    monkeypatch.delenv("GOS_APPROVAL_SIGNING_SECRET", raising=False)
    with pytest.raises(ProductionProfileError, match="GOS_APPROVAL_SIGNING_SECRET"):
        require_production_secrets()


def test_production_forbids_dev_default_secrets(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GOS_EXECUTION_TOKEN_SECRET", "gos-dev-execution-token-key-not-for-prod")
    monkeypatch.setenv("GOS_APPROVAL_SIGNING_SECRET", "prod-approval-secret-test-only!!")
    with pytest.raises(ProductionProfileError, match="dev default"):
        require_production_secrets()


def test_gateway_defaults_deny_legacy_accept_token():
    """AUTH-001b: boundary object defaults DENY; not only RuntimeContext wiring."""
    ledger = EventLedger()
    gw = ToolGateway(ledger)
    assert gw._allow_legacy_tokens is False
    with pytest.raises(LegacyExecutionTokenForbidden, match="legacy accept_token forbidden"):
        gw.accept_token("opaque")


def test_dev_runtime_context_opts_in_legacy_tokens(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GOS_PROFILE", raising=False)
    ctx = RuntimeContext(profile="dev")
    assert ctx.gateway._allow_legacy_tokens is True
    ctx.gateway.accept_token("dev_only_legacy")


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
