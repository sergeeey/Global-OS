"""Scripted action-selection provider for Operator mock cycles (no network, $0)."""

from __future__ import annotations

from typing import Any

from global_os.adapters.models.base import (
    GenerateRequest,
    GenerateResponse,
    ModelProvider,
    ModelRef,
)


class ScriptedActionProvider(ModelProvider):
    """Returns sequential structured actions from a fixed script.

    Each ``structured_generate`` call advances one cycle. After the script is
    exhausted, returns ``{"action": "stop"}``.
    """

    def __init__(self, script: list[dict[str, Any]] | None = None) -> None:
        self._script = list(script or [])
        self._index = 0
        self.cycles = 0
        self.history: list[dict[str, Any]] = []
        self.last_usage: dict[str, Any] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": 0.0,
            "cost_usd": 0.0,
            "cost_forced": False,
        }

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        step = self._next()
        return GenerateResponse(
            text=str(step),
            model=ModelRef("stub", "scripted_action", "1"),
            input_tokens=len(request.prompt.split()),
            output_tokens=1,
            cost_usd=0.0,
        )

    def structured_generate(
        self, request: GenerateRequest, schema: dict[str, Any]
    ) -> dict[str, Any]:
        _ = schema
        step = self._next()
        self.history.append({"prompt_prefix": request.prompt[:120], "step": step})
        return dict(step)

    def _next(self) -> dict[str, Any]:
        self.cycles += 1
        if self._index >= len(self._script):
            return {"action": "stop"}
        step = dict(self._script[self._index])
        self._index += 1
        return step


def default_tool_script(
    allowed_tool_ids: list[str],
    *,
    preferred_tool_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Two-cycle script: propose one permitted tool, then stop.

    Prefers tools that match Goal criteria when provided; never invents ids
    outside ``allowed_tool_ids``.
    """
    if not allowed_tool_ids:
        return [{"action": "stop"}]
    allowed = list(allowed_tool_ids)
    pick = allowed[0]
    if preferred_tool_ids:
        for tid in preferred_tool_ids:
            if tid in allowed:
                pick = tid
                break
    return [
        {"action": "call_tool", "tool_id": pick, "args": {}},
        {"action": "stop"},
    ]
