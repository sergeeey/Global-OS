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
