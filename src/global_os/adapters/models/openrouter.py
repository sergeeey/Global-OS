"""OpenRouter free / pinned models (OpenAI-compatible)."""

from __future__ import annotations

import os

from global_os.adapters.models.base import ModelProviderError
from global_os.adapters.models.openai_compat import OpenAICompatProvider
from global_os.adapters.models.pins import OPENROUTER_REASONER, OPENROUTER_SMOKE

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_SMOKE_MODEL = OPENROUTER_SMOKE
DEFAULT_OPENROUTER_REASONER = OPENROUTER_REASONER


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
        # Resolve key early for format check (also loaded again in parent).
        raw = api_key if api_key is not None else os.environ.get("OPENROUTER_API_KEY", "")
        from global_os.adapters.models.http_json import sanitize_api_key

        cleaned = sanitize_api_key(raw)
        if cleaned and not cleaned.startswith("sk-or-"):
            raise ModelProviderError(
                "openrouter: OPENROUTER_API_KEY must start with 'sk-or-' "
                f"(got prefix={cleaned[:7]!r}… len={len(cleaned)}) — "
                "re-copy full key from openrouter.ai/settings/keys"
            )
        extra = {
            "HTTP-Referer": os.environ.get("OPENROUTER_HTTP_REFERER", "https://global-os.dev"),
            "X-Title": os.environ.get("OPENROUTER_APP_TITLE", "Global-OS"),
            "X-OpenRouter-Title": os.environ.get("OPENROUTER_APP_TITLE", "Global-OS"),
        }
        super().__init__(
            api_key=cleaned or api_key,
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
