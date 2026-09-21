"""H-ORG-001 measured path — pipeline proof + optional live keys."""

from __future__ import annotations

import os

import pytest

from global_os.evals.organization.measured import (
    measure_h_org_001,
    summarize_h_org_001_measured,
)
from tests.support.scripted_hetero_provider import ScriptedHeterogeneousProvider


def test_h_org_measured_wire_pipeline_honest_verdict():
    report = measure_h_org_001(
        provider=ScriptedHeterogeneousProvider(),
        fidelity="PROVIDER_WIRE",
    )
    assert report["hypothesis"] == "H-ORG-001"
    assert report["fidelity"] == "PROVIDER_WIRE"
    assert report["verdict"] == "WIRE_MEASURED_PIPELINE_OK_NOT_SCIENTIFIC"
    assert report["scientific_claim_accepted"] is False
    assert report["metrics"]["single_solver"]["success_count"] == 4
    assert report["metrics"]["manager_workers"]["success_count"] == 4
    assert report["metrics"]["model_invoked_events"] >= 5
    assert "kill_criteria" in report
    assert report["baseline"] == "single_solver"
    assert report["intervention"] == "manager_workers"


def test_summarize_measured_without_keys_stays_inconclusive(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GOS_REQUIRE_MODELS", raising=False)
    report = summarize_h_org_001_measured()
    assert report["verdict"] == "INCONCLUSIVE_NEEDS_REAL_MODEL"
    assert report["scientific_claim_accepted"] is False


def test_summarize_measured_with_injected_provider():
    report = summarize_h_org_001_measured(
        openai_provider=ScriptedHeterogeneousProvider(),
    )
    assert report["verdict"] == "WIRE_MEASURED_PIPELINE_OK_NOT_SCIENTIFIC"


def test_live_h_org_when_keys_present():
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")):
        if os.environ.get("GOS_REQUIRE_MODELS") == "1":
            pytest.fail("GOS_REQUIRE_MODELS=1 but no model keys for H-ORG live")
        pytest.skip("no live model keys for H-ORG measured")
    report = summarize_h_org_001_measured()
    assert report["fidelity"].startswith("LIVE_MODEL")
    assert report["scientific_claim_accepted"] is False
    assert report["metrics"]["model_invoked_events"] >= 1
