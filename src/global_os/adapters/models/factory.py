"""Factory for live model providers — fail closed without credentials."""

from __future__ import annotations

import os
from typing import Literal

from global_os.adapters.models.anthropic import AnthropicProvider
from global_os.adapters.models.base import ModelProvider, ModelProviderError
from global_os.adapters.models.gemini import GeminiProvider
from global_os.adapters.models.groq import GroqProvider
from global_os.adapters.models.openai_compat import OpenAICompatProvider
from global_os.adapters.models.openrouter import OpenRouterProvider
from global_os.adapters.models.zero_cost import scientific_eval_mode, zero_cost_mode_enabled

ProviderName = Literal["openai", "anthropic", "openrouter", "groq", "gemini"]


def open_model_provider(
    name: ProviderName,
    *,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    timeout_seconds: float = 60.0,
    scientific: bool | None = None,
) -> ModelProvider:
    """Open a remote provider. Never silently falls back to Echo/stub."""
    sci = scientific_eval_mode() if scientific is None else scientific
    if zero_cost_mode_enabled() and name in {"openai", "anthropic"}:
        raise ModelProviderError(
            f"GOS_ZERO_COST_MODE=1: paid provider {name!r} DENY — use openrouter/groq/gemini"
        )
    if name == "openai":
        return OpenAICompatProvider(
            api_key=api_key if api_key is not None else None,
            model=model or "gpt-4o-mini",
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            scientific=sci,
        )
    if name == "anthropic":
        return AnthropicProvider(
            api_key=api_key if api_key is not None else None,
            model=model or "claude-3-5-haiku-latest",
            base_url=base_url,
            timeout_seconds=timeout_seconds,
        )
    if name == "openrouter":
        return OpenRouterProvider(
            api_key=api_key,
            model=model or "nvidia/nemotron-3-ultra:free",
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            scientific=sci,
        )
    if name == "groq":
        return GroqProvider(
            api_key=api_key,
            model=model or "qwen/qwen3-32b",
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            scientific=sci,
        )
    if name == "gemini":
        return GeminiProvider(
            api_key=api_key,
            model=model or "gemini-2.0-flash",
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            scientific=sci,
        )
    raise ModelProviderError(f"unknown provider: {name}")


def require_live_providers() -> bool:
    return os.environ.get("GOS_REQUIRE_MODELS", "") == "1"


def live_keys_present() -> dict[str, bool]:
    return {
        "openai": bool(os.environ.get("OPENAI_API_KEY", "").strip()),
        "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
        "openrouter": bool(os.environ.get("OPENROUTER_API_KEY", "").strip()),
        "groq": bool(os.environ.get("GROQ_API_KEY", "").strip()),
        "gemini": bool(
            os.environ.get("GEMINI_API_KEY", "").strip()
            or os.environ.get("GOOGLE_API_KEY", "").strip()
        ),
    }


def free_live_ready() -> bool:
    """Enough free providers for diversity smoke (≥1)."""
    keys = live_keys_present()
    return keys["openrouter"] or keys["groq"] or keys["gemini"]
