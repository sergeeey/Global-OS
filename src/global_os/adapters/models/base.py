"""Model provider abstraction — core never imports vendor SDKs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelRef:
    provider: str
    model: str
    version: str


@dataclass(frozen=True)
class GenerateRequest:
    prompt: str
    max_tokens: int = 1024
    temperature: float = 0.0
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class GenerateResponse:
    text: str
    model: ModelRef
    input_tokens: int
    output_tokens: int


class ModelProvider(ABC):
    """All model calls go through adapters implementing this interface."""

    @abstractmethod
    def generate(self, request: GenerateRequest) -> GenerateResponse:
        raise NotImplementedError

    @abstractmethod
    def structured_generate(
        self, request: GenerateRequest, schema: dict[str, Any]
    ) -> dict[str, Any]:
        raise NotImplementedError


class EchoModelProvider(ModelProvider):
    """Deterministic stub for tests — not a production provider."""

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        return GenerateResponse(
            text=f"echo:{request.prompt[:200]}",
            model=ModelRef("stub", "echo", "0"),
            input_tokens=len(request.prompt.split()),
            output_tokens=1,
        )

    def structured_generate(
        self, request: GenerateRequest, schema: dict[str, Any]
    ) -> dict[str, Any]:
        return {"echo": request.prompt, "schema_title": schema.get("title")}


class ModelProviderError(Exception):
    """Provider-level failure (outage, timeout) — must not invent success."""


class OutageModelProvider(ModelProvider):
    """Simulates API outage — always fails closed."""

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        raise ModelProviderError("api_outage: provider unreachable")

    def structured_generate(
        self, request: GenerateRequest, schema: dict[str, Any]
    ) -> dict[str, Any]:
        raise ModelProviderError("api_outage: provider unreachable")


class SwappableModelProvider(ModelProvider):
    """Allows mid-run model swap while callers keep the same interface."""

    def __init__(self, primary: ModelProvider) -> None:
        self._current = primary
        self.swap_count = 0

    @property
    def current(self) -> ModelProvider:
        return self._current

    def swap(self, provider: ModelProvider) -> None:
        self._current = provider
        self.swap_count += 1

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        return self._current.generate(request)

    def structured_generate(
        self, request: GenerateRequest, schema: dict[str, Any]
    ) -> dict[str, Any]:
        return self._current.structured_generate(request, schema)


class SlowModelProvider(ModelProvider):
    """Simulates slow dependency by exceeding a wall budget check."""

    def __init__(self, *, delay_seconds: float = 10.0, budget_seconds: float = 0.01) -> None:
        self.delay_seconds = delay_seconds
        self.budget_seconds = budget_seconds

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        if self.delay_seconds > self.budget_seconds:
            raise ModelProviderError(
                f"slow_dependency: delay {self.delay_seconds}s exceeds budget {self.budget_seconds}s"
            )
        return EchoModelProvider().generate(request)

    def structured_generate(
        self, request: GenerateRequest, schema: dict[str, Any]
    ) -> dict[str, Any]:
        if self.delay_seconds > self.budget_seconds:
            raise ModelProviderError("slow_dependency: exceeded wall budget")
        return EchoModelProvider().structured_generate(request, schema)
