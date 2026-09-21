"""Real model provider Reality Contact — fail-closed + dual-provider wire path."""

from __future__ import annotations

import os

import pytest

from global_os.adapters.models import (
    AnthropicProvider,
    GenerateRequest,
    ModelProviderError,
    OpenAICompatProvider,
    RecordingModelProvider,
    live_keys_present,
    open_model_provider,
    require_live_providers,
)
from global_os.runtime.events.ledger import EventLedger
from tests.support.model_http_sink import model_http_sink


def test_openai_fail_closed_without_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ModelProviderError, match="OPENAI_API_KEY"):
        OpenAICompatProvider(api_key="")
    with pytest.raises(ModelProviderError, match="OPENAI_API_KEY"):
        open_model_provider("openai", api_key="")


def test_anthropic_fail_closed_without_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ModelProviderError, match="ANTHROPIC_API_KEY"):
        AnthropicProvider(api_key="")
    with pytest.raises(ModelProviderError, match="ANTHROPIC_API_KEY"):
        open_model_provider("anthropic", api_key="")


def test_dual_provider_wire_path_records_event_trail():
    """Two distinct providers over real HTTP + model.invoked trail (no vendor SDK)."""
    ledger = EventLedger()
    with (
        model_http_sink("openai", response_text="openai-wire") as oai,
        model_http_sink("anthropic", response_text="anthropic-wire") as ant,
    ):
        openai = RecordingModelProvider(
            OpenAICompatProvider(api_key="sk-test", base_url=oai.base_url + "/v1"),
            ledger,
            goal_id="goal_model_wire",
            tenant_id="t",
            workspace_id="w",
        )
        anthropic = RecordingModelProvider(
            AnthropicProvider(api_key="ant-test", base_url=ant.base_url),
            ledger,
            goal_id="goal_model_wire",
            tenant_id="t",
            workspace_id="w",
        )
        r1 = openai.generate(GenerateRequest(prompt="ping-openai", max_tokens=32))
        r2 = anthropic.generate(GenerateRequest(prompt="ping-anthropic", max_tokens=32))

    assert r1.text == "openai-wire"
    assert r1.model.provider == "openai"
    assert r1.input_tokens == 11
    assert r1.output_tokens == 3
    assert r1.latency_ms >= 0
    assert r1.cost_usd is not None

    assert r2.text == "anthropic-wire"
    assert r2.model.provider == "anthropic"
    assert r2.input_tokens == 9
    assert r2.output_tokens == 4
    assert r2.cost_usd is not None

    assert len(oai.posts) == 1
    assert "/chat/completions" in oai.posts[0]["path"]
    assert len(ant.posts) == 1
    assert "/v1/messages" in ant.posts[0]["path"]

    events = ledger.list_events(goal_id="goal_model_wire")
    invoked = [e for e in events if e["event_type"] == "model.invoked"]
    assert len(invoked) == 2
    providers = {e["payload"]["provider"] for e in invoked}
    assert providers == {"openai", "anthropic"}
    for e in invoked:
        p = e["payload"]
        assert p["status"] == "ok"
        assert p.get("model")
        assert p.get("version")
        assert "latency_ms" in p
        assert "cost_usd" in p
        assert "output_digest" in p or "output_preview" in p
        assert p["output_preview"] in {"openai-wire", "anthropic-wire"}


def test_live_remote_providers_when_keys_present():
    keys = live_keys_present()
    if not (keys["openai"] and keys["anthropic"]):
        if require_live_providers():
            pytest.fail(
                "GOS_REQUIRE_MODELS=1 but OPENAI_API_KEY and/or ANTHROPIC_API_KEY missing"
            )
        pytest.skip("live model keys not set (OPENAI_API_KEY + ANTHROPIC_API_KEY)")

    ledger = EventLedger()
    openai = RecordingModelProvider(
        open_model_provider("openai"),
        ledger,
        goal_id="goal_model_live",
    )
    anthropic = RecordingModelProvider(
        open_model_provider("anthropic"),
        ledger,
        goal_id="goal_model_live",
    )
    prompt = "Reply with exactly the word PONG and nothing else."
    r1 = openai.generate(GenerateRequest(prompt=prompt, max_tokens=16, temperature=0.0))
    r2 = anthropic.generate(GenerateRequest(prompt=prompt, max_tokens=16, temperature=0.0))
    assert r1.text.strip()
    assert r2.text.strip()
    assert r1.model.provider == "openai"
    assert r2.model.provider == "anthropic"
    assert r1.latency_ms > 0
    assert r2.latency_ms > 0
    invoked = [e for e in ledger.list_events() if e["event_type"] == "model.invoked"]
    assert len(invoked) >= 2
    # Silence unused in CI without keys path
    _ = os.environ.get("CI")
