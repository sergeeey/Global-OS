"""Anthropic Messages API adapter (HTTP; no anthropic SDK)."""

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

DEFAULT_ANTHROPIC_BASE = "https://api.anthropic.com"
DEFAULT_ANTHROPIC_MODEL = "claude-3-5-haiku-latest"
ANTHROPIC_VERSION = "2023-06-01"


class AnthropicProvider(ModelProvider):
    """Calls /v1/messages."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = DEFAULT_ANTHROPIC_MODEL,
        version: str = ANTHROPIC_VERSION,
        base_url: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        key = api_key if api_key is not None else os.environ.get("ANTHROPIC_API_KEY", "")
        if not key.strip():
            raise ModelProviderError(
                "anthropic: missing ANTHROPIC_API_KEY — refuse silent stub fallback"
            )
        self._api_key = key.strip()
        self._model = model
        self._version = version
        self._base_url = (
            base_url or os.environ.get("ANTHROPIC_BASE_URL") or DEFAULT_ANTHROPIC_BASE
        ).rstrip("/")
        self._timeout = timeout_seconds

    @property
    def model_ref(self) -> ModelRef:
        return ModelRef(provider="anthropic", model=self._model, version=self._version)

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        import time

        url = f"{self._base_url}/v1/messages"
        payload: dict[str, Any] = {
            "model": self._model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        started = time.perf_counter()
        try:
            data = post_json(
                url,
                payload,
                headers={
                    "x-api-key": self._api_key,
                    "anthropic-version": self._version,
                },
                timeout_seconds=self._timeout,
            )
        except HttpJsonError as exc:
            raise ModelProviderError(f"anthropic: {exc}") from exc
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
                f"anthropic: structured response not JSON: {resp.text[:200]}"
            ) from exc
        if not isinstance(parsed, dict):
            raise ModelProviderError("anthropic: structured response must be a JSON object")
        return parsed

    def _parse_response(self, data: dict[str, Any], *, latency_ms: float) -> GenerateResponse:
        content = data.get("content")
        if not isinstance(content, list) or not content:
            raise ModelProviderError("anthropic: missing content blocks")
        texts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(str(block.get("text", "")))
        if not texts:
            raise ModelProviderError("anthropic: no text blocks in response")
        text = "".join(texts)
        usage_raw = data.get("usage")
        usage: dict[str, Any] = usage_raw if isinstance(usage_raw, dict) else {}
        in_tok = int(usage.get("input_tokens") or 0)
        out_tok = int(usage.get("output_tokens") or 0)
        model_name = str(data.get("model") or self._model)
        ref = ModelRef(provider="anthropic", model=model_name, version=self._version)
        return GenerateResponse(
            text=text,
            model=ref,
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency_ms,
            cost_usd=estimate_cost_usd("anthropic", model_name, in_tok, out_tok),
        )
