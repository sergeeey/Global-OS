"""OpenAI-compatible Chat Completions — shared by OpenAI, OpenRouter, Groq."""

from __future__ import annotations

import os
import time
from typing import Any

from global_os.adapters.models.base import (
    GenerateRequest,
    GenerateResponse,
    ModelProvider,
    ModelProviderError,
    ModelRef,
)
from global_os.adapters.models.http_json import HttpJsonError, post_json
from global_os.adapters.models.pricing import estimate_cost_usd

DEFAULT_OPENAI_BASE = "https://api.openai.com/v1"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


class OpenAICompatProvider(ModelProvider):
    """Calls /chat/completions. Works with OpenAI or compatible gateways."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = DEFAULT_OPENAI_MODEL,
        version: str = "chat-completions",
        base_url: str | None = None,
        timeout_seconds: float = 60.0,
        provider_id: str = "openai",
        api_key_env: str = "OPENAI_API_KEY",
        extra_headers: dict[str, str] | None = None,
        force_cost_usd: float | None = None,
        allow_model_substitution: bool = False,
        scientific: bool = False,
    ) -> None:
        key = api_key if api_key is not None else os.environ.get(api_key_env, "")
        if not key.strip():
            raise ModelProviderError(
                f"{provider_id}: missing {api_key_env} — refuse silent stub fallback"
            )
        if scientific and model in {"openrouter/free", "openrouter/auto"}:
            raise ModelProviderError(
                f"{provider_id}: router model {model!r} forbidden in scientific eval — pin exact model"
            )
        if scientific and not allow_model_substitution:
            # scientific defaults: no silent swap
            allow_model_substitution = False
        self._api_key = key.strip()
        self._model = model
        self._requested_model = model
        self._version = version
        self._provider_id = provider_id
        self._base_url = (
            base_url or os.environ.get(f"{provider_id.upper()}_BASE_URL") or DEFAULT_OPENAI_BASE
        ).rstrip("/")
        # OpenAI uses OPENAI_BASE_URL
        if provider_id == "openai" and base_url is None:
            self._base_url = (os.environ.get("OPENAI_BASE_URL") or DEFAULT_OPENAI_BASE).rstrip("/")
        self._timeout = timeout_seconds
        self._extra_headers = dict(extra_headers or {})
        self._force_cost_usd = force_cost_usd
        self._allow_model_substitution = allow_model_substitution
        self._scientific = scientific
        self.last_substitution: dict[str, str] | None = None

    @property
    def model_ref(self) -> ModelRef:
        return ModelRef(provider=self._provider_id, model=self._model, version=self._version)

    @property
    def requested_model(self) -> str:
        return self._requested_model

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self._requested_model,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        headers = {"Authorization": f"Bearer {self._api_key}", **self._extra_headers}
        started = time.perf_counter()
        try:
            data = post_json(url, payload, headers=headers, timeout_seconds=self._timeout)
        except HttpJsonError as exc:
            # Propagate Retry-After hint in message when present
            raise ModelProviderError(f"{self._provider_id}: {exc}") from exc
        latency_ms = (time.perf_counter() - started) * 1000.0
        return self._parse_response(data, latency_ms=latency_ms)

    def structured_generate(
        self, request: GenerateRequest, schema: dict[str, Any]
    ) -> dict[str, Any]:
        import json

        prompt = (
            f"{request.prompt}\n\nRespond with JSON matching schema title="
            f"{schema.get('title', 'object')}."
        )
        resp = self.generate(
            GenerateRequest(
                prompt=prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                metadata=request.metadata,
            )
        )
        try:
            parsed: object = json.loads(resp.text)
        except json.JSONDecodeError as exc:
            raise ModelProviderError(
                f"{self._provider_id}: structured response not JSON: {resp.text[:200]}"
            ) from exc
        if not isinstance(parsed, dict):
            raise ModelProviderError(
                f"{self._provider_id}: structured response must be a JSON object"
            )
        return parsed

    def _parse_response(self, data: dict[str, Any], *, latency_ms: float) -> GenerateResponse:
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ModelProviderError(f"{self._provider_id}: missing choices in response")
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        if not isinstance(message, dict):
            raise ModelProviderError(f"{self._provider_id}: missing message in choice")
        text = message.get("content")
        if not isinstance(text, str):
            raise ModelProviderError(f"{self._provider_id}: missing content string")
        usage_raw = data.get("usage")
        usage: dict[str, Any] = usage_raw if isinstance(usage_raw, dict) else {}
        in_tok = int(usage.get("prompt_tokens") or 0)
        out_tok = int(usage.get("completion_tokens") or 0)
        actual_model = str(data.get("model") or self._requested_model)
        self.last_substitution = None
        if actual_model != self._requested_model and not _model_compatible(
            self._requested_model, actual_model
        ):
            self.last_substitution = {
                "requested_model": self._requested_model,
                "actual_model": actual_model,
                "provider": self._provider_id,
            }
            if not self._allow_model_substitution:
                raise ModelProviderError(
                    f"{self._provider_id}: model substitution refused "
                    f"(requested={self._requested_model!r} actual={actual_model!r}); "
                    "pin exact model for scientific eval"
                )
        cost: float | None
        if self._force_cost_usd is not None:
            cost = self._force_cost_usd
        else:
            cost = estimate_cost_usd(self._provider_id, actual_model, in_tok, out_tok)
        ref = ModelRef(provider=self._provider_id, model=actual_model, version=self._version)
        return GenerateResponse(
            text=text,
            model=ref,
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency_ms,
            cost_usd=cost,
        )


def _model_compatible(requested: str, actual: str) -> bool:
    if requested == actual:
        return True
    return requested.endswith(":free") and actual == requested[: -len(":free")]
