"""OpenRouter free / pinned models (OpenAI-compatible)."""

from __future__ import annotations

import os

from global_os.adapters.models.base import ModelProviderError
from global_os.adapters.models.openai_compat import OpenAICompatProvider

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
# Smoke-only router — forbidden when scientific=True
OPENROUTER_SMOKE_MODEL = "openrouter/free"
# Default scientific pin (free catalog; override via model=)
DEFAULT_OPENROUTER_REASONER = "nvidia/nemotron-3-ultra:free"


class OpenRouterProvider(OpenAICompatProvider):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = DEFAULT_OPENROUTER_REASONER,
        timeout_seconds: float = 60.0,
        scientific: bool = True,
        allow_model_substitution: bool | None = None,
        base_url: str | None = None,
    ) -> None:
        if scientific and model == OPENROUTER_SMOKE_MODEL:
            raise ModelProviderError(
                "openrouter: openrouter/free forbidden for scientific eval — pin exact model:free"
            )
        allow = not scientific
        if allow_model_substitution is not None:
            allow = allow_model_substitution
        extra = {
            "HTTP-Referer": os.environ.get("OPENROUTER_HTTP_REFERER", "https://global-os.dev"),
            "X-Title": os.environ.get("OPENROUTER_APP_TITLE", "Global-OS"),
        }
        super().__init__(
            api_key=api_key,
            model=model,
            base_url=base_url or os.environ.get("OPENROUTER_BASE_URL") or OPENROUTER_BASE,
            timeout_seconds=timeout_seconds,
            provider_id="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            extra_headers=extra,
            force_cost_usd=0.0,
            allow_model_substitution=allow,
            scientific=scientific,
        )
