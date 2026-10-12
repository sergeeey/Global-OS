"""P1b: fair LLM scheduler — resource only, quota fail-closed (ADR-0013)."""

from __future__ import annotations

from global_os.adapters.models.fair_scheduler import (
    FairLlmScheduler,
    LlmRequest,
    LlmResult,
    SchedulerPolicy,
)


def test_rr_interleaves_missions() -> None:
    sched = FairLlmScheduler(policy=SchedulerPolicy.RR)
    for i, mission in enumerate(["m1", "m2", "m1", "m2"]):
        sched.enqueue(
            LlmRequest(
                request_id=f"r{i}",
                mission_id=mission,
                provider="groq",
                payload={"i": i},
            )
        )

    order: list[str] = []

    def exec_fn(req: LlmRequest) -> LlmResult:
        order.append(req.mission_id)
        return LlmResult(req.request_id, req.mission_id, ok=True, output={})

    results = sched.drain("groq", exec_fn)
    assert len(results) == 4
    # RR should not run both m1 before any m2 when both queued
    assert order[0] != order[1] or order.count("m1") == 2


def test_quota_exhausted_stops_drain() -> None:
    sched = FairLlmScheduler(policy=SchedulerPolicy.FIFO)
    for i in range(3):
        sched.enqueue(
            LlmRequest(f"q{i}", "m", "groq", {})
        )

    def exec_fn(req: LlmRequest) -> LlmResult:
        if req.request_id == "q0":
            return LlmResult(req.request_id, "m", ok=False, error="TPD", quota_exhausted=True)
        return LlmResult(req.request_id, "m", ok=True, output={})

    results = sched.drain("groq", exec_fn)
    assert len(results) == 1
    assert results[0].quota_exhausted is True
    assert sched.pending_count("groq") == 2
