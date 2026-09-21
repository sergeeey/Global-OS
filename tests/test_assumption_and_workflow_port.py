from __future__ import annotations

from datetime import UTC, datetime

import pytest

from global_os.adapters.storage import connect_sqlite
from global_os.adapters.workflows import (
    LocalDurableAdapter,
    TemporalAdapterUnavailable,
    TemporalWorkflowAdapter,
)
from global_os.cognition.clarification import ClarificationEngine
from global_os.common.hashing import content_hash
from global_os.epistemic import EpistemicStore
from global_os.runtime.events import EventLedger
from global_os.runtime.workflows.durable import DurableRunner, WorkflowDefinition, WorkflowStep


def test_clarification_assumption_lands_in_epistemic_and_stales():
    ledger = EventLedger()
    epi = EpistemicStore(ledger)
    now = datetime.now(UTC).isoformat()
    epi.put_evidence(
        {
            "evidence_id": "ev_a1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "status": "SOURCE_CONTENT_VERIFIED",
            "trust_label": "ORG_TRUSTED",
            "recorded_at": now,
            "known_at": now,
            "content_digest": content_hash({"x": 1}),
        }
    )
    epi.put_claim(
        {
            "claim_id": "cl_a1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "Format is JSON",
            "status": "ACTIVE",
            "evidence_ids": ["ev_a1"],
            "confidence": "LOW",
            "confidence_basis": "convention",
            "recorded_at": now,
        }
    )
    engine = ClarificationEngine(ledger, epistemic=epi)
    result = engine.decide(
        {
            "materiality_policy": "materiality_based",
            "ask_when": ["irreversible_action"],
            "assume_when": ["formatting_only", "low_impact"],
            "record_assumption": True,
        },
        situation="formatting_only",
        impact="low",
        probability=0.2,
        irreversibility="none",
        goal_sensitivity=0.1,
        goal_id="goal_x",
        tenant_id="t",
        workspace_id="w",
        assumption_statement="Use JSON output format",
        depends_on_claim_ids=["cl_a1"],
        depends_on_evidence_ids=["ev_a1"],
    )
    asm_id = result["assumption"]["assumption_id"]
    assert epi.get_assumption(asm_id)["status"] == "ACTIVE"
    out = epi.invalidate_evidence("ev_a1", tenant_id="t", workspace_id="w", reason="retract")
    assert asm_id in out["assumptions"]
    assert epi.get_assumption(asm_id)["status"] == "STALE"


def test_workflow_port_local_adapter_not_temporal():
    conn = connect_sqlite(":memory:")
    adapter = LocalDurableAdapter(DurableRunner(conn))
    assert adapter.backend == "local_durable_runner"
    definition = WorkflowDefinition(
        name="demo",
        steps=[
            WorkflowStep("a", lambda s: {**s, "a": 1}),
            WorkflowStep("b", lambda s: {**s, "b": 2}),
        ],
    )
    state = adapter.start_or_resume("run_1", definition, {})
    assert state == {"a": 1, "b": 2}
    with pytest.raises(TemporalAdapterUnavailable, match="ADR-0002"):
        TemporalWorkflowAdapter().start_or_resume("run_x", definition, {})
