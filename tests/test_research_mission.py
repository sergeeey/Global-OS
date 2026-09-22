"""Tests for research mission orchestration (Y17-FC-001/002/003 productization)."""

from __future__ import annotations

from pathlib import Path

from global_os.evals.research import PriorWorkReframe, provider_iv_status, run_research_mission


def test_provider_iv_blocked_without_keys(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    status, _, keys = provider_iv_status()
    assert status == "BLOCKED_ENVIRONMENT"
    assert keys["openrouter"] is False


def test_research_mission_degraded_iv_still_completes(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    def experiment() -> dict:
        return {"fisher_p": 0.01, "slice_ps": [0.01, 0.02, 0.4]}

    def decide(raw: dict):
        decision = "SUPPORTED" if raw["fisher_p"] < 0.05 else "REJECTED"
        nulls = [{"slice": 2, "p": raw["slice_ps"][2]}]
        return decision, nulls

    def det_verify(raw: dict):
        ok = 0.0 <= raw["fisher_p"] <= 1.0
        return ("PASS" if ok else "FAIL", ["fisher_p in [0,1]"])

    report = run_research_mission(
        mission_id="TEST-RM-1",
        artifact_root=tmp_path / "m1",
        objective_text="Test degraded IV path",
        hypothesis_statement="fisher_p < 0.05 on toy data",
        preregistration={
            "primary_criterion": {"statistic": "fisher_p", "alpha": 0.05},
            "kill_criterion": "REJECTED if fisher_p >= 0.05",
        },
        plan={"steps": ["compute", "verify", "decide"]},
        experiment_fn=experiment,
        decide_fn=decide,
        deterministic_verify_fn=det_verify,
        kill_criteria=["REJECTED if fisher_p >= 0.05"],
        alternative_explanations=["noise"],
        reopen_conditions=["new seeds"],
        reframe=PriorWorkReframe(
            discovered_prior_id="PRIOR-1",
            original_intent="first confirmatory",
            reframed_intent="independent replication",
            rationale="prior already ran same design",
        ),
        request_provider_iv=True,
    )
    assert report.decision == "SUPPORTED"
    assert report.verification.provider_status == "BLOCKED_ENVIRONMENT"
    assert report.scientific_claim_accepted is False
    assert (tmp_path / "m1" / "decision.md").exists()
    assert (tmp_path / "m1" / "null_results.json").exists()
    assert (tmp_path / "m1" / "reframe.json").exists()
    assert any(fc["class"] == "ENVIRONMENT_GAP" for fc in report.failure_cases)
