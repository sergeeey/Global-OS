"""Tool contract interface — MCP is an adapter, not the domain."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    version: str
    operations: tuple[str, ...]
    trust_level: str
    side_effect_class: str
    required_capabilities: tuple[str, ...]
    reversibility: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


@dataclass(frozen=True)
class ToolInvocation:
    tool_id: str
    operation: str
    arguments: dict[str, Any]
    execution_token: str
    idempotency_key: str


@dataclass(frozen=True)
class ToolOutcome:
    success: bool
    payload: dict[str, Any]


class ToolAdapter(ABC):
    @abstractmethod
    def spec(self) -> ToolSpec:
        raise NotImplementedError

    @abstractmethod
    def invoke(self, invocation: ToolInvocation) -> ToolOutcome:
        raise NotImplementedError


class FakeReadTool(ToolAdapter):
    """Canary read-only tool for gateway tests."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            tool_id="fake.read",
            version="0.1.0",
            operations=("fetch",),
            trust_level="LOW",
            side_effect_class="read",
            required_capabilities=("web.read",),
            reversibility="full",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )

    def invoke(self, invocation: ToolInvocation) -> ToolOutcome:
        return ToolOutcome(True, {"echo": invocation.arguments, "op": invocation.operation})


class FakePaymentTool(ToolAdapter):
    """Canary side-effect tool — must not run under a web.read token (audit N1)."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            tool_id="payment.fake",
            version="0.1.0",
            operations=("charge",),
            trust_level="HIGH",
            side_effect_class="payment",
            required_capabilities=("payment.send",),
            reversibility="none",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )

    def invoke(self, invocation: ToolInvocation) -> ToolOutcome:
        return ToolOutcome(True, {"charged": invocation.arguments})
