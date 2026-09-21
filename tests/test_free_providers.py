"""Zero-cost free providers — OpenRouter / Groq / Gemini."""

from __future__ import annotations

import pytest

from global_os.adapters.capabilities import CapabilityRegistry
from global_os.adapters.models import (
    GeminiProvider,
    GenerateRequest,
    GroqProvider,
    ModelProviderError,
    OpenRouterProvider,
    RecordingModelProvider,
    allow_provider_for_classification,
    assert_zero_cost_allowed,
    open_model_provider,
    register_free_models,
)
from global_os.adapters.models.openai_compat import OpenAICompatProvider
from global_os.runtime.events.ledger import EventLedger
from tests.support.model_http_sink import model_http_sink


def test_openrouter_scientific_rejects_smoke_router():
    with pytest.raises(ModelProviderError, match="forbidden for scientific"):
        OpenRouterProvider(api_key="sk-or-test", model="openrouter/free", scientific=True)


def test_openrouter_smoke_allowed_when_not_scientific():
    p = OpenRouterProvider(api_key="sk-or-test", model="openrouter/free", scientific=False)
    assert p.requested_model == "openrouter/free"


def test_groq_rejects_deprecated_compound():
    with pytest.raises(ModelProviderError, match="deprecated"):
        GroqProvider(api_key="gsk-test", model="groq/compound")


def test_zero_cost_mode_denies_paid_openai(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GOS_ZERO_COST_MODE", "1")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with pytest.raises(ModelProviderError, match="ZERO_COST"):
        open_model_provider("openai")


def test_zero_cost_assert_denies_positive_cost(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GOS_ZERO_COST_MODE", "1")
    with pytest.raises(ModelProviderError, match="cost_usd"):
        assert_zero_cost_allowed(cost_usd=0.01, free_tier=True)


def test_confidential_denies_training_possible():
    assert (
        allow_provider_for_classification(
            data_classification="confidential",
            privacy={"training_allowed": "possible"},
        )
        is False
    )
    assert (
        allow_provider_for_classification(
            data_classification="public",
            privacy={"training_allowed": "possible"},
        )
        is True
    )


def test_free_catalog_registers_with_privacy():
    reg = CapabilityRegistry()
    ids = register_free_models(reg)
    assert len(ids) >= 4
    nemo = reg.get("cap_model.openrouter.nemotron3ultra_free")
    assert nemo["cost_usd_per_unit"] == 0.0
    assert nemo["privacy"]["free_tier"] is True
    assert nemo["scientific_use"]["pinned"] is True


def test_openrouter_and_groq_wire_path_zero_cost():
    ledger = EventLedger()
    with (
        model_http_sink("openai", response_text="or-ok") as oai,
        model_http_sink("openai", response_text="groq-ok") as gq,
    ):
        or_p = RecordingModelProvider(
            OpenAICompatProvider(
                api_key="sk-or",
                model="nvidia/nemotron-3-ultra:free",
                base_url=oai.base_url + "/v1",
                provider_id="openrouter",
                api_key_env="OPENROUTER_API_KEY",
                force_cost_usd=0.0,
                scientific=True,
            ),
            ledger,
            goal_id="goal_free",
        )
        groq_p = RecordingModelProvider(
            OpenAICompatProvider(
                api_key="gsk",
                model="qwen/qwen3-32b",
                base_url=gq.base_url + "/v1",
                provider_id="groq",
                api_key_env="GROQ_API_KEY",
                force_cost_usd=0.0,
                scientific=True,
            ),
            ledger,
            goal_id="goal_free",
        )
        r1 = or_p.generate(GenerateRequest(prompt="ping"))
        r2 = groq_p.generate(GenerateRequest(prompt="ping"))
    assert r1.cost_usd == 0.0
    assert r2.cost_usd == 0.0
    assert r1.model.provider == "openrouter"
    assert r2.model.provider == "groq"
    assert r1.text == "or-ok"
    invoked = [e for e in ledger.list_events() if e["event_type"] == "model.invoked"]
    assert len(invoked) == 2


def test_scientific_refuses_model_substitution():
    with model_http_sink("openai", response_text="x") as sink:
        # Override sink to return a different model id
        sink.posts.clear()

        class _Forced(OpenAICompatProvider):
            def _parse_response(self, data, *, latency_ms):  # type: ignore[no-untyped-def]
                data = dict(data)
                data["model"] = "totally-different-model"
                return OpenAICompatProvider._parse_response(self, data, latency_ms=latency_ms)

        p = _Forced(
            api_key="sk",
            model="nvidia/nemotron-3-ultra:free",
            base_url=sink.base_url + "/v1",
            provider_id="openrouter",
            force_cost_usd=0.0,
            allow_model_substitution=False,
            scientific=True,
        )
        with pytest.raises(ModelProviderError, match="substitution refused"):
            p.generate(GenerateRequest(prompt="hi"))


def test_gemini_fail_closed_without_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(ModelProviderError, match="GEMINI_API_KEY"):
        GeminiProvider(api_key="")
