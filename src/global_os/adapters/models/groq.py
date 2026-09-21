"""Groq free tier (OpenAI-compatible). Avoid deprecated compound models."""

from __future__ import annotations

import os

from global_os.adapters.models.base import ModelProviderError
from global_os.adapters.models.openai_compat import OpenAICompatProvider

GROQ_BASE = "https://api.groq.com/openai/v1"
# Free/developer models (do not use groq/compound — deprecated 2026-09-21)
DEFAULT_GROQ_MODEL = "qwen/qwen3-32b"
DEPRECATED_GROQ = frozenset({"groq/compound", "groq/compound-mini", "compound", "compound-mini"})


class GroqProvider(OpenAICompatProvider):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = DEFAULT_GROQ_MODEL,
        timeout_seconds: float = 60.0,
        scientific: bool = True,
        base_url: str | None = None,
    ) -> None:
        if model in DEPRECATED_GROQ or model.startswith("compound"):
            raise ModelProviderError(
                f"groq: model {model!r} deprecated — use qwen/qwen3-* or openai/gpt-oss-*"
            )
        super().__init__(
            api_key=api_key,
            model=model,
            base_url=base_url or os.environ.get("GROQ_BASE_URL") or GROQ_BASE,
            timeout_seconds=timeout_seconds,
            provider_id="groq",
            api_key_env="GROQ_API_KEY",
            force_cost_usd=0.0,
            allow_model_substitution=not scientific,
            scientific=scientific,
        )
