"""OpenAI-compatible Chat Completions adapter (HTTP; no openai SDK)."""

from __future__ import annotations

import os
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
    ) -> None:
        key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY", "")
        if not key.strip():
            raise ModelProviderError(
                "openai: missing OPENAI_API_KEY — refuse silent stub fallback"
            )
        self._api_key = key.strip()
        self._model = model
        self._version = version
        self._base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or DEFAULT_OPENAI_BASE).rstrip(
            "/"
        )
        self._timeout = timeout_seconds

    @property
    def model_ref(self) -> ModelRef:
        return ModelRef(provider="openai", model=self._model, version=self._version)

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        import time

        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        started = time.perf_counter()
        try:
            data = post_json(
                url,
                payload,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout_seconds=self._timeout,
            )
        except HttpJsonError as exc:
            raise ModelProviderError(f"openai: {exc}") from exc
        latency_ms = (time.perf_counter() - started) * 1000.0
        return self._parse_response(data, latency_ms=latency_ms)

    def structured_generate(
        self, request: GenerateRequest, schema: dict[str, Any]
    ) -> dict[str, Any]:
        # Structured mode still goes through chat; caller validates against schema.
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
        import json

        try:
            parsed: object = json.loads(resp.text)
        except json.JSONDecodeError as exc:
            raise ModelProviderError(f"openai: structured response not JSON: {resp.text[:200]}") from exc
        if not isinstance(parsed, dict):
            raise ModelProviderError("openai: structured response must be a JSON object")
        return parsed

    def _parse_response(self, data: dict[str, Any], *, latency_ms: float) -> GenerateResponse:
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ModelProviderError("openai: missing choices in response")
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        if not isinstance(message, dict):
            raise ModelProviderError("openai: missing message in choice")
        text = message.get("content")
        if not isinstance(text, str):
            raise ModelProviderError("openai: missing content string")
        usage_raw = data.get("usage")
        usage: dict[str, Any] = usage_raw if isinstance(usage_raw, dict) else {}
        in_tok = int(usage.get("prompt_tokens") or 0)
        out_tok = int(usage.get("completion_tokens") or 0)
        model_name = str(data.get("model") or self._model)
        ref = ModelRef(provider="openai", model=model_name, version=self._version)
        return GenerateResponse(
            text=text,
            model=ref,
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency_ms,
            cost_usd=estimate_cost_usd("openai", model_name, in_tok, out_tok),
        )
