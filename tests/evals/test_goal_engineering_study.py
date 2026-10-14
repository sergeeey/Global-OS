"""Acceptance + adversarial tests for GE-STUDY-v1."""

from __future__ import annotations

import json
from pathlib import Path

from global_os.evals.goal_engineering.independent_evaluator import evaluate
from global_os.evals.goal_engineering.runner import (
    hypothesis_verdicts,
    run_and_seal,
    run_suite,
    run_trial,
    summarize,
)
from global_os.evals.goal_engineering.strategies import STRATEGY_IDS, build_ge, build_trad
from global_os.evals.goal_engineering.tasks import all_task_specs, build_world


def test_three_strategies_defined() -> None:
    assert set(STRATEGY_IDS) == {"S_TRAD", "S_DETAIL", "S_GE"}
    for spec in all_task_specs():
        packets = spec.packets()
        assert set(packets) == set(STRATEGY_IDS)
        assert packets["S_GE"].definition_of_done
        assert packets["S_GE"].evidence_requirements
        assert packets["S_TRAD"].definition_of_done == []


def test_three_domains_present() -> None:
    domains = {s.domain for s in all_task_specs()}
    assert domains == {"coding", "research", "multi_step"}


def test_independent_evaluator_rejects_false_claim_coding() -> None:
    world = build_world("coding", 1)
    # Craft a fake episode-like object via real trial then mutate — use run_trial paths
    from global_os.evals.goal_engineering.agents import EpisodeResult

    ep = EpisodeResult(
        strategy_id="S_TRAD",
        task_id=world.task_id,
        domain="coding",
        claimed_success=True,
        claimed_blocked=False,
        final_artifacts={
            "files": world.state["files"],  # still buggy
            "tests_run": False,
            "test_passed": False,
            "other_unchanged": True,
        },
        evidence_ledger=[],
        steps=1,
        token_cost=10,
        wall_ms=10,
        human_interventions=0,
    )
    v = evaluate(world, ep)
    assert v.oracle_success is False
    assert v.false_claim is True


def test_ge_packet_requires_dod() -> None:
    p = build_ge(
        "t",
        "obj",
        [{"id": "sc_1", "description": "done"}],
        [{"criterion_id": "sc_1", "kind": "test", "tier": "2"}],
    )
    assert "Definition of Done" in p.prompt_text
    assert p.goal_contract["success_criteria"]


def test_suite_reproducible() -> None:
    a = run_suite(n_seeds=5, master_seed=123)
    b = run_suite(n_seeds=5, master_seed=123)
    assert [r.trial_id for r in a] == [r.trial_id for r in b]
    assert [r.oracle_success for r in a] == [r.oracle_success for r in b]


def test_summary_has_contrasts_and_cis() -> None:
    rows = run_suite(n_seeds=8, master_seed=2907)
    summary = summarize(rows)
    assert summary["n_trials"] == 8 * 3 * 3
    assert "S_GE_minus_S_TRAD__oracle_success" in summary["contrasts_GE_minus_baseline"]
    ci = summary["contrasts_GE_minus_baseline"]["S_GE_minus_S_TRAD__oracle_success"]
    assert "ci90_low" in ci and "ci90_high" in ci
    hyps = hypothesis_verdicts(summary)
    assert set(hyps) >= {
        "H1_GE_oracle_gt_TRAD",
        "H2_GE_oracle_gt_DETAIL",
        "H3_GE_false_claim_lt_TRAD",
        "H4_GE_evidence_gt_baselines",
        "H5_GE_not_free",
    }
    for body in hyps.values():
        assert body["verdict"] in {"CONFIRMED", "REJECTED", "INCONCLUSIVE"}


def test_seal_writes_artifacts(tmp_path: Path) -> None:
    report = run_and_seal(tmp_path, n_seeds=5, master_seed=42)
    assert (tmp_path / "results.json").is_file()
    assert (tmp_path / "RESULTS_SEAL.md").is_file()
    data = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert data["execution_class"] == "EXECUTED_DETERMINISTIC"
    assert data["live_llm_class"] == "PROTOCOL_ONLY_NOT_EXECUTED"
    assert report["summary"]["live_llm"] == "NOT_EXECUTED"


def test_trad_prompt_is_vague() -> None:
    p = build_trad("x", "do the thing")
    assert "as best you can" in p.prompt_text.lower() or "best you can" in p.prompt_text


def test_adversarial_detail_incomplete_multi_step() -> None:
    """DETAIL omitting verify must not oracle-succeed (brittleness condition)."""
    # Find a seed where DETAIL fails multi_step — should be all seeds by construction
    row = run_trial("S_DETAIL", "multi_step_pipeline", seed=2907)
    assert row.domain == "multi_step"
    assert row.oracle_success == 0.0
    assert row.false_claim == 1.0
