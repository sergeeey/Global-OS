"""HTTP JSON client + API key sanitization."""

from __future__ import annotations

import pytest

from global_os.adapters.models.base import GenerateRequest, ModelProviderError
from global_os.adapters.models.http_json import (
    HttpJsonError,
    parse_retry_after,
    post_json,
    sanitize_api_key,
)
from global_os.adapters.models.openai_compat import OpenAICompatProvider
from tests.support.model_http_sink import model_http_sink


def test_sanitize_api_key_strips_bom_quotes_zwsp():
    raw = "\ufeff\"sk-or-test\u200b\"\n"
    assert sanitize_api_key(raw) == "sk-or-test"


def test_parse_retry_after_seconds_and_rejects_date():
    assert parse_retry_after("2") == 2.0
    assert parse_retry_after("1.5") == 1.5
    assert parse_retry_after("Wed, 21 Oct 2015 07:28:00 GMT") is None
    assert parse_retry_after(None) is None
    assert parse_retry_after("-1") is None


def test_post_json_retries_429_then_succeeds(monkeypatch: pytest.MonkeyPatch):
    sleeps: list[float] = []
    monkeypatch.setattr(
        "global_os.adapters.models.http_json.time.sleep",
        lambda s: sleeps.append(float(s)),
    )
    with model_http_sink(
        "openai",
        response_text="after-backoff",
        status_sequence=[429, 200],
        retry_after_seconds=0.25,
    ) as sink:
        data = post_json(
            f"{sink.base_url}/v1/chat/completions",
            {"model": "x", "messages": []},
            headers={},
            max_attempts=4,
        )
    assert data["choices"][0]["message"]["content"] == "after-backoff"
    assert len(sink.posts) == 2
    assert sleeps == [0.25]


def test_post_json_exhausts_429_fail_closed(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("global_os.adapters.models.http_json.time.sleep", lambda _s: None)
    with model_http_sink(
        "openai",
        status_sequence=[429, 429, 429],
        retry_after_seconds=1,
    ) as sink, pytest.raises(HttpJsonError) as ei:
        post_json(
            f"{sink.base_url}/v1/chat/completions",
            {"model": "x"},
            headers={},
            max_attempts=3,
        )
    assert ei.value.status == 429
    assert ei.value.attempts == 3
    assert len(sink.posts) == 3


def test_openai_compat_surfaces_retry_exhausted(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("global_os.adapters.models.http_json.time.sleep", lambda _s: None)
    with model_http_sink(
        "openai",
        status_sequence=[429, 429, 429, 429],
        retry_after_seconds=2,
    ) as sink:
        p = OpenAICompatProvider(
            api_key="gsk-test",
            model="openai/gpt-oss-120b",
            base_url=sink.base_url + "/v1",
            provider_id="groq",
            api_key_env="GROQ_API_KEY",
            force_cost_usd=0.0,
        )
        with pytest.raises(ModelProviderError, match="Retry-After|attempt"):
            p.generate(GenerateRequest(prompt="ping"))


def test_post_json_paces_when_min_interval_env_set(monkeypatch: pytest.MonkeyPatch):
    import global_os.adapters.models.http_json as hj

    monkeypatch.setenv("GOS_MODEL_HTTP_MIN_INTERVAL_SECONDS", "0.5")
    hj._next_slot_monotonic = 0.0
    clock = {"t": 1000.0}
    sleeps: list[float] = []

    monkeypatch.setattr(hj.time, "monotonic", lambda: clock["t"])

    def _sleep(seconds: float) -> None:
        sleeps.append(float(seconds))
        clock["t"] += float(seconds)

    monkeypatch.setattr(hj.time, "sleep", _sleep)

    with model_http_sink("openai", response_text="a") as sink:
        url = f"{sink.base_url}/v1/chat/completions"
        post_json(url, {"model": "x"}, headers={})
        clock["t"] += 0.1  # not enough to clear interval
        post_json(url, {"model": "x"}, headers={})

    assert len(sink.posts) == 2
    assert sleeps  # paced on second call
    assert abs(sleeps[0] - 0.4) < 1e-9
