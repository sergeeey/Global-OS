"""Multi-provider verification adapters — Reality Contact."""

from __future__ import annotations

from global_os.adapters.models import (
    AnthropicProvider,
    OpenAICompatProvider,
    RecordingModelProvider,
)
from global_os.runtime.events.ledger import EventLedger
from global_os.verification.independent_stack import MethodResult, MethodSpec
from global_os.verification.multi_provider import (
    multi_provider_verification_stack,
    scripted_pass_provider,
)
from global_os.verification.router import VerificationTier
from tests.support.model_http_sink import model_http_sink


def test_multi_provider_stack_builds_distinct_families():
    stack = multi_provider_verification_stack(
        openai=scripted_pass_provider("PASS"),
        anthropic=scripted_pass_provider("PASS"),
    )
    families = {m.model_family for m in stack.methods}
    providers = {m.provider for m in stack.methods}
    assert families == {"gpt", "claude"}
    assert providers == {"openai", "anthropic"}


def test_multi_provider_wire_verification_consensus():
    ledger = EventLedger()
    with (
        model_http_sink("openai", response_text="PASS") as oai,
        model_http_sink("anthropic", response_text="PASS") as ant,
    ):
        openai = RecordingModelProvider(
            OpenAICompatProvider(api_key="sk-test", base_url=oai.base_url + "/v1"),
            ledger,
            goal_id="goal_mp_verify",
        )
        anthropic = RecordingModelProvider(
            AnthropicProvider(api_key="ant-test", base_url=ant.base_url),
            ledger,
            goal_id="goal_mp_verify",
        )
        stack = multi_provider_verification_stack(openai=openai, anthropic=anthropic)
        out = stack.verify(
            {"claim": "2+2=4", "expected": 4, "actual": 4},
            required_tier=VerificationTier.INDEPENDENT.value,
        )
    assert out.passed is True
    assert out.consensus == "unanimous_pass"
    assert "different_provider" in out.diversity_factors
    assert "different_model_family" in out.diversity_factors
    invoked = [e for e in ledger.list_events() if e["event_type"] == "model.invoked"]
    assert len(invoked) == 2
    assert {e["payload"]["provider"] for e in invoked} == {"openai", "anthropic"}


def test_multi_provider_conflicted_when_judges_disagree():
    stack = multi_provider_verification_stack(
        openai=scripted_pass_provider("PASS"),
        anthropic=scripted_pass_provider("FAIL"),
    )
    out = stack.verify(
        {"claim": "x", "expected": 1, "actual": 1},
        required_tier=VerificationTier.INDEPENDENT.value,
    )
    assert out.passed is False
    assert out.consensus == "conflicted"


def test_multi_provider_with_deterministic_extra_axis():
    def det(payload: dict[str, object]) -> MethodResult:
        return MethodResult(
            "det_eq",
            payload.get("expected") == payload.get("actual"),
            {"check": "eq"},
        )

    extra = MethodSpec(
        method_id="det_eq",
        family="deterministic",
        diversity_axis="deterministic_recompute",
        run=det,
    )
    stack = multi_provider_verification_stack(
        openai=scripted_pass_provider("PASS"),
        anthropic=scripted_pass_provider("PASS"),
        extra=extra,
    )
    out = stack.verify(
        {"claim": "ok", "expected": 7, "actual": 7},
        required_tier=VerificationTier.INDEPENDENT.value,
    )
    assert out.passed is True
    assert len(out.method_results) == 3
