"""Remote multi-provider verification adapters (GOS-I10).

Distinct provider/model-family LLM judges + optional deterministic axis.
Same-family stacks are rejected by IndependentVerificationStack.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Any

from global_os.adapters.models.base import GenerateRequest, ModelProvider, ModelProviderError
from global_os.verification.independent_stack import (
    IndependentVerificationStack,
    MethodResult,
    MethodSpec,
)


def _extract_pass_fail(text: str) -> bool:
    """Parse a constrained judge reply. Fail closed on ambiguous output."""
    cleaned = text.strip().upper()
    if re.search(r"\bPASS\b", cleaned) and not re.search(r"\bFAIL\b", cleaned):
        return True
    if re.search(r"\bFAIL\b", cleaned):
        return False
    # JSON {"passed": true/false}
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ModelProviderError(
            f"judge reply not parseable as PASS/FAIL: {text[:120]}"
        ) from exc
    if isinstance(obj, dict) and "passed" in obj:
        return bool(obj["passed"])
    raise ModelProviderError(f"judge reply not parseable as PASS/FAIL: {text[:120]}")


def make_provider_judge(
    provider: ModelProvider,
    *,
    method_id: str,
    provider_name: str,
    model_family: str,
    diversity_axis: str = "different_provider",
) -> MethodSpec:
    """Wrap a ModelProvider as an IndependentVerificationStack LLM judge method."""

    def run(payload: dict[str, Any]) -> MethodResult:
        claim = payload.get("claim", payload.get("statement", ""))
        evidence = payload.get("evidence", payload.get("actual"))
        expected = payload.get("expected")
        prompt = (
            "You are a verification judge. Reply with exactly PASS or FAIL.\n"
            f"Claim: {claim}\n"
            f"Evidence/actual: {evidence}\n"
            f"Expected: {expected}\n"
        )
        try:
            resp = provider.generate(
                GenerateRequest(prompt=prompt, max_tokens=16, temperature=0.0)
            )
            passed = _extract_pass_fail(resp.text)
            details: dict[str, Any] = {
                "provider": provider_name,
                "model": resp.model.model,
                "version": resp.model.version,
                "latency_ms": resp.latency_ms,
                "raw_preview": resp.text[:120],
            }
            return MethodResult(method_id=method_id, passed=passed, details=details)
        except ModelProviderError as exc:
            return MethodResult(
                method_id=method_id,
                passed=False,
                details={"error": str(exc), "provider": provider_name},
            )

    return MethodSpec(
        method_id=method_id,
        family="llm_judge",
        diversity_axis=diversity_axis,
        run=run,
        provider=provider_name,
        model_family=model_family,
    )


def multi_provider_verification_stack(
    *,
    openai: ModelProvider,
    anthropic: ModelProvider,
    extra: MethodSpec | None = None,
) -> IndependentVerificationStack:
    """Build ≥2-provider LLM judge stack with distinct families (GOS-I10)."""
    methods: list[MethodSpec] = [
        make_provider_judge(
            openai,
            method_id="openai_judge",
            provider_name="openai",
            model_family="gpt",
            diversity_axis="different_provider",
        ),
        make_provider_judge(
            anthropic,
            method_id="anthropic_judge",
            provider_name="anthropic",
            model_family="claude",
            diversity_axis="different_model_family",
        ),
    ]
    if extra is not None:
        methods.append(extra)
    return IndependentVerificationStack(tuple(methods))


def scripted_pass_provider(text: str = "PASS") -> ModelProvider:
    """Deterministic fake provider for harness (not a live remote)."""
    from global_os.adapters.models.base import GenerateResponse, ModelRef

    class _Scripted(ModelProvider):
        def generate(self, request: GenerateRequest) -> GenerateResponse:
            return GenerateResponse(
                text=text,
                model=ModelRef("scripted", "judge", "0"),
                input_tokens=1,
                output_tokens=1,
                latency_ms=0.1,
                cost_usd=0.0,
            )

        def structured_generate(
            self, request: GenerateRequest, schema: dict[str, Any]
        ) -> dict[str, Any]:
            return {"passed": text.upper() == "PASS"}

    return _Scripted()


JudgeFactory = Callable[[], ModelProvider]
