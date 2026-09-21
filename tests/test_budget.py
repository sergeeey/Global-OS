from __future__ import annotations

import pytest

from global_os.kernel.budget import BudgetExhausted, BudgetKernel, BudgetLimits
from global_os.runtime.events import EventLedger


def test_budget_blocks_overspend():
    ledger = EventLedger()
    budget = BudgetKernel(
        ledger,
        tenant_id="t",
        workspace_id="w",
        goal_id="goal_x",
        limits=BudgetLimits(usd=1.0, tokens=100, api_calls=10, wall_time_seconds=60, agent_count=3),
    )
    budget.reserve("r1", usd=0.5, tokens=10)
    budget.commit("r1")
    with pytest.raises(BudgetExhausted):
        budget.reserve("r2", usd=0.6)
