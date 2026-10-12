"""Fair LLM resource scheduler (AIOS-inspired, ADR-0013).

Resource OS only — does not grant Authority. Quota / TPD DENY from providers
must remain fail-closed; this scheduler never bypasses them.
"""

from __future__ import annotations

import itertools
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SchedulerPolicy(str, Enum):
    FIFO = "FIFO"
    RR = "RR"


@dataclass(frozen=True)
class LlmRequest:
    request_id: str
    mission_id: str
    provider: str
    payload: dict[str, Any]
    enqueued_at: float = field(default_factory=time.monotonic)


@dataclass
class LlmResult:
    request_id: str
    mission_id: str
    ok: bool
    output: dict[str, Any] | None = None
    error: str | None = None
    quota_exhausted: bool = False


ExecuteFn = Callable[[LlmRequest], LlmResult]


class FairLlmScheduler:
    """Per-provider queues with FIFO or round-robin across missions."""

    def __init__(
        self,
        *,
        policy: SchedulerPolicy = SchedulerPolicy.RR,
        time_slice_seconds: float = 1.0,
    ) -> None:
        self.policy = policy
        self.time_slice_seconds = time_slice_seconds
        self._lock = threading.Lock()
        # provider -> mission_id -> deque[LlmRequest]
        self._queues: dict[str, dict[str, deque[LlmRequest]]] = {}
        self._mission_cycle: dict[str, itertools.cycle[str] | None] = {}
        self._fifo: dict[str, deque[LlmRequest]] = {}
        self._suspended: dict[str, LlmRequest] = {}
        self._completed: list[LlmResult] = []

    def enqueue(self, req: LlmRequest) -> None:
        with self._lock:
            if self.policy is SchedulerPolicy.FIFO:
                self._fifo.setdefault(req.provider, deque()).append(req)
                return
            by_mission = self._queues.setdefault(req.provider, {})
            by_mission.setdefault(req.mission_id, deque()).append(req)
            self._mission_cycle[req.provider] = None  # rebuild on next pop

    def pending_count(self, provider: str | None = None) -> int:
        with self._lock:
            if provider is None:
                n = sum(len(q) for q in self._fifo.values())
                for pm in self._queues.values():
                    n += sum(len(q) for q in pm.values())
                return n + len(self._suspended)
            n = len(self._fifo.get(provider, ()))
            n += sum(len(q) for q in self._queues.get(provider, {}).values())
            return n

    def _pop_next_unlocked(self, provider: str) -> LlmRequest | None:
        if self.policy is SchedulerPolicy.FIFO:
            q = self._fifo.get(provider)
            if not q:
                return None
            return q.popleft()

        by_mission = self._queues.get(provider) or {}
        # Drop empty mission queues.
        active = [m for m, q in by_mission.items() if q]
        if not active:
            return None
        cycle = self._mission_cycle.get(provider)
        if cycle is None:
            cycle = itertools.cycle(sorted(active))
            self._mission_cycle[provider] = cycle
        # Try up to len(active) missions for a non-empty queue.
        for _ in range(len(active)):
            mission = next(cycle)
            q = by_mission.get(mission)
            if q:
                return q.popleft()
        return None

    def dispatch_one(self, provider: str, execute: ExecuteFn) -> LlmResult | None:
        with self._lock:
            req = self._pop_next_unlocked(provider)
        if req is None:
            return None
        # Time-slice bookkeeping: mark suspend token if execute reports slice expiry
        # via output flag; otherwise complete.
        started = time.monotonic()
        result = execute(req)
        elapsed = time.monotonic() - started
        if (
            result.ok
            and result.output
            and result.output.get("slice_exhausted")
            and elapsed >= self.time_slice_seconds * 0.5
        ):
            # Best-effort suspend/resume token (provider-dependent).
            with self._lock:
                self._suspended[req.request_id] = req
            result.output = {**(result.output or {}), "suspended": True}
        with self._lock:
            self._completed.append(result)
        return result

    def resume(self, request_id: str) -> LlmRequest | None:
        with self._lock:
            req = self._suspended.pop(request_id, None)
            if req is not None:
                self.enqueue(req)
            return req

    def drain(
        self,
        provider: str,
        execute: ExecuteFn,
        *,
        max_n: int = 100,
    ) -> list[LlmResult]:
        out: list[LlmResult] = []
        for _ in range(max_n):
            r = self.dispatch_one(provider, execute)
            if r is None:
                break
            out.append(r)
            if r.quota_exhausted:
                break  # fail-closed: do not burn the queue on TPD
        return out

    def completed(self) -> list[LlmResult]:
        with self._lock:
            return list(self._completed)
