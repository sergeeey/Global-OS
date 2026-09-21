"""Free-tier model catalog for Capability Registry (volatile; GOS-I25)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from global_os.adapters.capabilities.registry import CapabilityRegistry

FREE_MODEL_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "cap_model.openrouter.nemotron3ultra_free",
        "role": "general_reasoner",
        "provider": "openrouter",
        "implementation": "nvidia/nemotron-3-ultra:free",
        "capabilities": ["reasoning", "orchestration", "long_context", "research"],
        "privacy": {
            "free_tier": True,
            "training_allowed": "possible",
            "zero_data_retention": False,
        },
        "scientific_use": {"pinned": True, "smoke_router_ok": False},
    },
    {
        "id": "cap_model.openrouter.north_mini_code_free",
        "role": "coding_worker",
        "provider": "openrouter",
        "implementation": "openrouter/north-mini-code:free",
        "capabilities": ["coding", "tool_use", "agentic_swe"],
        "privacy": {
            "free_tier": True,
            "training_allowed": "possible",
            "zero_data_retention": False,
        },
        "scientific_use": {"pinned": True, "smoke_router_ok": False},
    },
    {
        "id": "cap_model.openrouter.smoke_free",
        "role": "smoke_fallback",
        "provider": "openrouter",
        "implementation": "openrouter/free",
        "capabilities": ["smoke"],
        "privacy": {
            "free_tier": True,
            "training_allowed": "possible",
            "zero_data_retention": False,
        },
        "scientific_use": {"pinned": False, "smoke_router_ok": True},
    },
    {
        "id": "cap_model.groq.qwen3",
        "role": "independent_verifier",
        "provider": "groq",
        "implementation": "qwen/qwen3-32b",
        "capabilities": ["reasoning", "verification"],
        "privacy": {
            "free_tier": True,
            "training_allowed": "unknown",
            "zero_data_retention": False,
        },
        "scientific_use": {"pinned": True, "smoke_router_ok": False},
    },
    {
        "id": "cap_model.gemini.flash_free",
        "role": "independent_verifier",
        "provider": "gemini",
        "implementation": "gemini-2.0-flash",
        "capabilities": ["reasoning", "verification"],
        "privacy": {
            "free_tier": True,
            "training_allowed": "possible",
            "zero_data_retention": False,
        },
        "scientific_use": {"pinned": True, "smoke_router_ok": False},
    },
)


def register_free_models(registry: CapabilityRegistry) -> list[str]:
    now = datetime.now(UTC).isoformat()
    ids: list[str] = []
    for entry in FREE_MODEL_CATALOG:
        desc = {
            "id": entry["id"],
            "schema_version": "0.1.0",
            "kind": "model",
            "provider": entry["provider"],
            "implementation": entry["implementation"],
            "risk": "low",
            "cost_usd_per_unit": 0.0,
            "verified_at": now,
            "capabilities": list(entry["capabilities"]),
            "privacy": dict(entry["privacy"]),
            "scientific_use": dict(entry["scientific_use"]),
            "role": entry["role"],
        }
        registry.register(desc)
        ids.append(entry["id"])
    return ids


def allow_provider_for_classification(
    *,
    data_classification: str,
    privacy: dict[str, Any],
) -> bool:
    """Confidential data cannot go to training-possible free providers."""
    if data_classification != "confidential":
        return True
    training = privacy.get("training_allowed")
    return training in {False, "false", "denied", "no"}
