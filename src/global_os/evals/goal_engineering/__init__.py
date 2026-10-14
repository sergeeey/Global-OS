"""Goal Engineering comparative study (GE-STUDY-v1).

Deterministic harness comparing tasking strategies. Does not assume
Goal Engineering superiority a priori. Live-LLM arms are protocol-only
unless explicitly executed and sealed.
"""

from __future__ import annotations

PROTOCOL_VERSION = "GE-STUDY-v1"
MASTER_SEED = 29_07_2026

__all__ = ["PROTOCOL_VERSION", "MASTER_SEED"]
