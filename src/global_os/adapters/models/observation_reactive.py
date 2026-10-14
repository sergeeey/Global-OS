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
_WRITE_FILE_RE = re.compile(r"((?:FIX_|ACCEPT_)[A-Za-z0-9_.-]+\.txt)")
_ACCEPT_LINE_RE = re.compile(r"exact line ([A-Za-z0-9_-]+)")


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
        self.last_usage: dict[str, Any] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": 0.0,
            "cost_usd": 0.0,
            "cost_forced": False,
        }

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
        allowed_m = _ALLOWED_RE.search(prompt)
        executed_m = _EXECUTED_RE.search(prompt)
        preferred_m = _PREFERRED_RE.search(prompt)
        allowed = _parse_list(allowed_m.group(1) if allowed_m else None)
        executed = _parse_list(executed_m.group(1) if executed_m else None)
        preferred = _parse_list(preferred_m.group(1) if preferred_m else None)
        obs_m = _OBS_RE.search(prompt)
        obs = obs_m.group(1) if obs_m else "none"

        step = self._decide(allowed, executed, preferred, obs, prompt)
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
        prompt: str,
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
        write_name = "FIX_APPLIED.txt"
        write_hit = _WRITE_FILE_RE.search(prompt)
        if write_hit:
            write_name = write_hit.group(1)
        accept_line = "preprod_supervised_fix_marker"
        line_hit = _ACCEPT_LINE_RE.search(prompt)
        if line_hit:
            accept_line = line_hit.group(1)
        for tid in order:
            if tid not in executed:
                args: dict[str, Any] = {}
                if tid == "workspace.read_text":
                    args = {"path": "README.md"}
                if tid == "workspace.write_text":
                    args = {
                        "path": write_name,
                        "content": accept_line + "\n",
                    }
                return {"action": "call_tool", "tool_id": tid, "args": args}
        return {"action": "stop"}
