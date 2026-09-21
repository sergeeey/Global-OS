from __future__ import annotations

import pytest

from global_os.epistemic.hypotheses import HypothesisError, HypothesisState, HypothesisStore
from global_os.runtime.events import EventLedger


def test_hypothesis_lifecycle_and_null_result():
    ledger = EventLedger()
    store = HypothesisStore(ledger)
    h = store.propose(
        goal_id="goal_x",
        statement="Lead time is capacity constrained",
        kill_criteria=["schedule shows spare capacity"],
        alternative_explanations=["logistics delay"],
        reopen_conditions=["new supplier data"],
        tenant_id="t",
        workspace_id="w",
    )
    assert h.state == HypothesisState.PROPOSED
    store.activate(h.hypothesis_id, tenant_id="t", workspace_id="w")
    killed = store.resolve(
        h.hypothesis_id,
        HypothesisState.KILLED,
        tenant_id="t",
        workspace_id="w",
        null_result=True,
    )
    assert killed.state == HypothesisState.KILLED
    closed = store.close(h.hypothesis_id, tenant_id="t", workspace_id="w")
    assert closed.state == HypothesisState.CLOSED
    types = [e["event_type"] for e in ledger.list_events()]
    assert "null_result.recorded" in types
    with pytest.raises(HypothesisError):
        store.propose(
            goal_id="goal_x",
            statement="x",
            kill_criteria=[],
            alternative_explanations=[],
            reopen_conditions=[],
            tenant_id="t",
            workspace_id="w",
        )
