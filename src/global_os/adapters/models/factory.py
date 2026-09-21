"""Factory for live model providers — fail closed without credentials."""

from __future__ import annotations

import os
from typing import Literal

from global_os.adapters.models.anthropic import AnthropicProvider
from global_os.adapters.models.base import ModelProvider, ModelProviderError
from global_os.adapters.models.openai_compat import OpenAICompatProvider

ProviderName = Literal["openai", "anthropic"]


def open_model_provider(
    name: ProviderName,
    *,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    timeout_seconds: float = 60.0,
) -> ModelProvider:
    """Open a remote provider. Never silently falls back to Echo/stub."""
    if name == "openai":
        return OpenAICompatProvider(
            api_key=api_key if api_key is not None else None,
            model=model or "gpt-4o-mini",
            base_url=base_url,
            timeout_seconds=timeout_seconds,
        )
    if name == "anthropic":
        return AnthropicProvider(
            api_key=api_key if api_key is not None else None,
            model=model or "claude-3-5-haiku-latest",
            base_url=base_url,
            timeout_seconds=timeout_seconds,
        )
    raise ModelProviderError(f"unknown provider: {name}")


def require_live_providers() -> bool:
    """True when env demands live remote calls (CI optional gate)."""
    return os.environ.get("GOS_REQUIRE_MODELS", "") == "1"


def live_keys_present() -> dict[str, bool]:
    return {
        "openai": bool(os.environ.get("OPENAI_API_KEY", "").strip()),
        "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
    }
