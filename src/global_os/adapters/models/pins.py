"""Pinned free-tier model IDs for Empirical Science ($0 path).

Update when providers deprecate models — never use openrouter/free for science.
"""

from __future__ import annotations

# OpenRouter free reasoner (exact slug; $0)
OPENROUTER_REASONER = "nvidia/nemotron-3-ultra-550b-a55b:free"
OPENROUTER_SMOKE = "openrouter/free"

# Groq free/dev — qwen/qwen3-32b deprecated 2026-07-17; use gpt-oss-120b
GROQ_VERIFIER = "openai/gpt-oss-120b"

# Gemini free — gemini-2.0-flash deprecated 2026-06-01
GEMINI_FLASH = "gemini-3.6-flash"
