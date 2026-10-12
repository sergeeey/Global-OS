"""P1a: progressive disclosure + commit boundary (ADR-0013)."""

from __future__ import annotations

import pytest

from global_os.cognition.context.assembler import ContextAssembler
from global_os.memory.progressive import ROOT_INDEX_PATH, ProgressiveMemoryStore
from global_os.runtime.events.ledger import EventLedger


def test_silent_tool_promote_forbidden() -> None:
    store = ProgressiveMemoryStore(EventLedger())
    with pytest.raises(PermissionError):
        store.reject_silent_promote_from_tool({"success": True, "text": "nice"})


def test_draft_propose_commit_and_root_only_context() -> None:
    ledger = EventLedger()
    store = ProgressiveMemoryStore(ledger)
    store.draft(
        path="notes/fact.md",
        body="The sky is blue.",
        epistemic_kind="claim",
        tenant_id="t",
        workspace_id="w",
        goal_id="g1",
        token_cost=40,
    )
    with pytest.raises(ValueError):
        store.commit("notes/fact.md", tenant_id="t", workspace_id="w", goal_id="g1")
    store.propose("notes/fact.md", tenant_id="t", workspace_id="w", goal_id="g1")
    store.commit("notes/fact.md", tenant_id="t", workspace_id="w", goal_id="g1")

    cands = store.context_candidates(root_only=True)
    assert len(cands) == 1
    assert cands[0]["content_ref"] == ROOT_INDEX_PATH
    assembled = ContextAssembler().assemble(
        goal_id="g1", token_budget=100, candidates=cands
    )
    assert len(assembled) == 1

    # On-demand retrieve of committed body
    body = store.retrieve("notes/fact.md")
    assert "blue" in body["body"]

    types = {e["event_type"] for e in ledger.list_events()}
    assert "memory.committed" in types
