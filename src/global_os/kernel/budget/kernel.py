"""Budget Kernel — cost is part of reasoning (GOS-I17)."""

from __future__ import annotations

from dataclasses import dataclass

from global_os.runtime.events.ledger import EventLedger


class BudgetError(Exception):
    pass


class BudgetExhausted(BudgetError):
    pass


@dataclass
class BudgetLimits:
    usd: float
    tokens: int
    api_calls: int
    wall_time_seconds: int
    agent_count: int


@dataclass
class BudgetUsage:
    usd: float = 0.0
    tokens: int = 0
    api_calls: int = 0
    wall_time_seconds: int = 0
    agent_count: int = 0


class BudgetKernel:
    def __init__(
        self,
        ledger: EventLedger,
        *,
        tenant_id: str,
        workspace_id: str,
        goal_id: str,
        limits: BudgetLimits,
    ) -> None:
        self._ledger = ledger
        self._tenant_id = tenant_id
        self._workspace_id = workspace_id
        self._goal_id = goal_id
        self.limits = limits
        self.usage = BudgetUsage()
        self._reservations: dict[str, dict[str, float | int]] = {}

    def remaining(self) -> dict[str, float | int]:
        return {
            "usd": self.limits.usd - self.usage.usd,
            "tokens": self.limits.tokens - self.usage.tokens,
            "api_calls": self.limits.api_calls - self.usage.api_calls,
            "wall_time_seconds": self.limits.wall_time_seconds - self.usage.wall_time_seconds,
            "agent_count": self.limits.agent_count - self.usage.agent_count,
        }

    def reserve(self, reservation_id: str, **amounts: float) -> None:
        projected = BudgetUsage(
            usd=self.usage.usd + float(amounts.get("usd", 0)),
            tokens=self.usage.tokens + int(amounts.get("tokens", 0)),
            api_calls=self.usage.api_calls + int(amounts.get("api_calls", 0)),
            wall_time_seconds=self.usage.wall_time_seconds
            + int(amounts.get("wall_time_seconds", 0)),
            agent_count=self.usage.agent_count + int(amounts.get("agent_count", 0)),
        )
        self._assert_within(projected)
        self._reservations[reservation_id] = dict(amounts)
        self._ledger.append(
            event_type="budget.reserved",
            tenant_id=self._tenant_id,
            workspace_id=self._workspace_id,
            goal_id=self._goal_id,
            payload={"reservation_id": reservation_id, "amounts": amounts},
            producer="kernel.budget",
        )

    def commit(self, reservation_id: str) -> None:
        amounts = self._reservations.pop(reservation_id, None)
        if amounts is None:
            raise BudgetError(f"unknown reservation: {reservation_id}")
        self.usage.usd += float(amounts.get("usd", 0))
        self.usage.tokens += int(amounts.get("tokens", 0))
        self.usage.api_calls += int(amounts.get("api_calls", 0))
        self.usage.wall_time_seconds += int(amounts.get("wall_time_seconds", 0))
        self.usage.agent_count += int(amounts.get("agent_count", 0))
        self._assert_within(self.usage)
        self._ledger.append(
            event_type="budget.consumed",
            tenant_id=self._tenant_id,
            workspace_id=self._workspace_id,
            goal_id=self._goal_id,
            payload={"reservation_id": reservation_id, "usage": self.usage.__dict__},
            producer="kernel.budget",
        )

    def _assert_within(self, usage: BudgetUsage) -> None:
        if usage.usd > self.limits.usd + 1e-9:
            raise BudgetExhausted("usd budget exhausted")
        if usage.tokens > self.limits.tokens:
            raise BudgetExhausted("token budget exhausted")
        if usage.api_calls > self.limits.api_calls:
            raise BudgetExhausted("api_calls budget exhausted")
        if usage.wall_time_seconds > self.limits.wall_time_seconds:
            raise BudgetExhausted("wall_time budget exhausted")
        if usage.agent_count > self.limits.agent_count:
            raise BudgetExhausted("agent_count budget exhausted")
        if usage.usd < 0 or usage.tokens < 0:
            raise BudgetError("budget cannot become negative")
