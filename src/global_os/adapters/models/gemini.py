"""Google Gemini Free tier via Generative Language API (no SDK)."""

from __future__ import annotations

import os
import time
from typing import Any
from urllib.parse import urlencode

from global_os.adapters.models.base import (
    GenerateRequest,
    GenerateResponse,
    ModelProvider,
    ModelProviderError,
    ModelRef,
)
from global_os.adapters.models.http_json import HttpJsonError, post_json

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


class GeminiProvider(ModelProvider):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = DEFAULT_GEMINI_MODEL,
        timeout_seconds: float = 60.0,
        scientific: bool = True,
        base_url: str | None = None,
    ) -> None:
        key = api_key if api_key is not None else os.environ.get("GEMINI_API_KEY", "")
        if not key.strip():
            # Also accept GOOGLE_API_KEY alias
            key = os.environ.get("GOOGLE_API_KEY", "")
        if not key.strip():
            raise ModelProviderError(
                "gemini: missing GEMINI_API_KEY — refuse silent stub fallback"
            )
        self._api_key = key.strip()
        self._model = model
        self._scientific = scientific
        self._timeout = timeout_seconds
        self._base_url = (base_url or os.environ.get("GEMINI_BASE_URL") or GEMINI_BASE).rstrip("/")
        self.last_substitution: dict[str, str] | None = None

    @property
    def model_ref(self) -> ModelRef:
        return ModelRef(provider="gemini", model=self._model, version="generateContent")

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        # Key in query string is Gemini's documented pattern; never log the URL with key.
        qs = urlencode({"key": self._api_key})
        url = f"{self._base_url}/models/{self._model}:generateContent?{qs}"
        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": request.prompt}]}],
            "generationConfig": {
                "maxOutputTokens": request.max_tokens,
                "temperature": request.temperature,
            },
        }
        started = time.perf_counter()
        try:
            # Do not put API key in headers that might be mirrored into events
            data = post_json(url, payload, headers={}, timeout_seconds=self._timeout)
        except HttpJsonError as exc:
            # Strip any accidental key echo from error body
            msg = str(exc).replace(self._api_key, "***")
            raise ModelProviderError(f"gemini: {msg}") from exc
        latency_ms = (time.perf_counter() - started) * 1000.0
        return self._parse(data, latency_ms=latency_ms)

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
            raise ModelProviderError(f"gemini: structured not JSON: {resp.text[:200]}") from exc
        if not isinstance(parsed, dict):
            raise ModelProviderError("gemini: structured response must be object")
        return parsed

    def _parse(self, data: dict[str, Any], *, latency_ms: float) -> GenerateResponse:
        cands = data.get("candidates")
        if not isinstance(cands, list) or not cands:
            raise ModelProviderError("gemini: missing candidates")
        content = cands[0].get("content") if isinstance(cands[0], dict) else None
        if not isinstance(content, dict):
            raise ModelProviderError("gemini: missing content")
        parts = content.get("parts")
        if not isinstance(parts, list) or not parts:
            raise ModelProviderError("gemini: missing parts")
        texts = [
            str(p.get("text", "")) for p in parts if isinstance(p, dict) and "text" in p
        ]
        if not texts:
            raise ModelProviderError("gemini: no text parts")
        usage_raw = data.get("usageMetadata")
        usage: dict[str, Any] = usage_raw if isinstance(usage_raw, dict) else {}
        in_tok = int(usage.get("promptTokenCount") or 0)
        out_tok = int(usage.get("candidatesTokenCount") or 0)
        return GenerateResponse(
            text="".join(texts),
            model=ModelRef("gemini", self._model, "generateContent"),
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency_ms,
            cost_usd=0.0,
        )
