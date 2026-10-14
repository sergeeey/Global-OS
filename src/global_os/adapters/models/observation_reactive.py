"""Mock provider whose next action depends on prior observation in the prompt."""

from __future__ import annotations

import re
from typing import Any

from global_os.adapters.models.base import (
    GenerateRequest,
    GenerateResponse,
    ModelProvider,
    ModelRef,
)

_ALLOWED_RE = re.compile(r"allowed_tool_ids=(\[[^\]]*\])")
_EXECUTED_RE = re.compile(r"executed=(\[[^\]]*\])")
_OBS_RE = re.compile(r"observation_status=([a-z_]+)")
_PREFERRED_RE = re.compile(r"preferred_tool_ids=(\[[^\]]*\])")


def _parse_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    inner = raw.strip()[1:-1].strip()
    if not inner:
        return []
    out: list[str] = []
    for part in inner.split(","):
        token = part.strip().strip("'\"")
        if token:
            out.append(token)
    return out


class ObservationReactiveProvider(ModelProvider):
    """Deterministic mock: choose tools from context, react to observations.

    Demonstrates that the next decision can change after a new observation
    without a human writing the next prompt.
    """

    def __init__(self) -> None:
        self.cycles = 0
        self.history: list[dict[str, Any]] = []

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        step = self.structured_generate(request, {"title": "OperatorAction"})
        return GenerateResponse(
            text=str(step),
            model=ModelRef("stub", "observation_reactive", "1"),
            input_tokens=len(request.prompt.split()),
            output_tokens=1,
            cost_usd=0.0,
        )

    def structured_generate(
        self, request: GenerateRequest, schema: dict[str, Any]
    ) -> dict[str, Any]:
        _ = schema
        self.cycles += 1
        prompt = request.prompt
        allowed = _parse_list(
            _ALLOWED_RE.search(prompt).group(1) if _ALLOWED_RE.search(prompt) else None
        )
        executed = _parse_list(
            _EXECUTED_RE.search(prompt).group(1) if _EXECUTED_RE.search(prompt) else None
        )
        preferred = _parse_list(
            
                _PREFERRED_RE.search(prompt).group(1)
                if _PREFERRED_RE.search(prompt)
                else None
            
        )
        obs_m = _OBS_RE.search(prompt)
        obs = obs_m.group(1) if obs_m else "none"

        step = self._decide(allowed, executed, preferred, obs)
        self.history.append(
            {
                "prompt_prefix": prompt[:160],
                "observation_status": obs,
                "executed": executed,
                "step": step,
            }
        )
        return dict(step)

    def _decide(
        self,
        allowed: list[str],
        executed: list[str],
        preferred: list[str],
        obs: str,
    ) -> dict[str, Any]:
        if not allowed:
            return {"action": "stop"}
        # After a failed observation, stop (fail-closed mock policy).
        if obs in {"fail", "discrepancy", "error"}:
            return {"action": "stop"}

        # Prefer criterion-matching tools. Do not spray every allowed tool.
        order = [t for t in preferred if t in allowed]
        if not order:
            # No semantic match — one exploratory allowed tool, then stop.
            order = list(allowed[:1])
        for tid in order:
            if tid not in executed:
                args: dict[str, Any] = {}
                if tid == "workspace.read_text":
                    args = {"path": "README.md"}
                if tid == "workspace.write_text":
                    args = {
                        "path": "FIX_APPLIED.txt",
                        "content": "preprod_supervised_fix_marker\n",
                    }
                return {"action": "call_tool", "tool_id": tid, "args": args}
        return {"action": "stop"}
