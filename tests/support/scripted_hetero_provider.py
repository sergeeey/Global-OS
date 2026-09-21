"""Scripted provider that answers H-ORG micro-tasks correctly (wire measurement)."""

from __future__ import annotations

from global_os.adapters.models.base import (
    GenerateRequest,
    GenerateResponse,
    ModelProvider,
    ModelRef,
)


class ScriptedHeterogeneousProvider(ModelProvider):
    """Deterministic answers for HETEROGENEOUS_TASKS — not a scientific model."""

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        p = request.prompt.upper()
        if "17*19" in p or "17×19" in p:
            text = "323"
        elif "SENTIMENT" in p or "TERRIBLE" in p:
            text = "NEGATIVE"
        elif "ISO DATE" in p or "YYYY-MM-DD" in p or "2026-09-21" in request.prompt:
            text = "2026-09-21"
        elif "A>B" in p or "A>C" in p:
            text = "YES"
        else:
            text = "OK"
        return GenerateResponse(
            text=text,
            model=ModelRef("scripted", "hetero", "0"),
            input_tokens=len(request.prompt.split()),
            output_tokens=1,
            latency_ms=1.0,
            cost_usd=0.0001,
        )

    def structured_generate(
        self, request: GenerateRequest, schema: dict[str, object]
    ) -> dict[str, object]:
        return {"echo": self.generate(request).text}
