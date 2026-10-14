"""Acceptance + adversarial tests for GE-STUDY post-audit harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.evals.goal_engineering.agent_view import AgentView, OracleLeakError
from global_os.evals.goal_engineering.agents import run_episode
from global_os.evals.goal_engineering.independent_evaluator import evaluate
from global_os.evals.goal_engineering.runner import (
    hypothesis_verdicts,
    run_and_seal,
    run_suite,
    run_trial,
    summarize,
)
from global_os.evals.goal_engineering.stats import (
    bootstrap_paired_diff_ci,
    fnv1a32,
)
from global_os.evals.goal_engineering.strategies import (
    STRATEGY_IDS,
    build_ge,
    build_trad,
)
from global_os.evals.goal_engineering.tasks import all_task_specs, build_world


def test_four_strategies_defined() -> None:
    assert set(STRATEGY_IDS) == {
        "S_TRAD",
        "S_DETAIL",
        "S_DETAIL_VERIFIED",
        "S_GE",
    }
    for spec in all_task_specs():
        packets = spec.packets()
        assert set(packets) == set(STRATEGY_IDS)
        assert packets["S_GE"].definition_of_done
        assert packets["S_DETAIL_VERIFIED"].procedural_steps
        assert packets["S_TRAD"].definition_of_done == []


def test_three_domains_present() -> None:
    domains = {s.domain for s in all_task_specs()}
    assert domains == {"coding", "research", "multi_step"}


def test_agent_view_blocks_oracle() -> None:
    world = build_world("coding", 1)
    view = AgentView(world)
    with pytest.raises(OracleLeakError):
        _ = view.oracle


def test_agents_do_not_reference_oracle_attr() -> None:
    src = Path("src/global_os/evals/goal_engineering/agents.py").read_text(
        encoding="utf-8"
    )
    assert "world.oracle" not in src
    assert '["oracle"]' not in src
    assert ".oracle[" not in src


def test_independent_evaluator_rejects_false_claim_coding() -> None:
    from global_os.evals.goal_engineering.agents import EpisodeResult

    world = build_world("coding", 1)
    ep = EpisodeResult(
        strategy_id="S_TRAD",
        task_id=world.task_id,
        domain="coding",
        claimed_success=True,
        claimed_blocked=False,
        final_artifacts={
            "files": world.state["files"],
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


def test_fnv_stable_across_calls() -> None:
    assert fnv1a32("S_GE|oracle_success|mean") == fnv1a32("S_GE|oracle_success|mean")
    assert fnv1a32("a") != fnv1a32("b")


def test_paired_bootstrap_requires_equal_length() -> None:
    with pytest.raises(ValueError):
        bootstrap_paired_diff_ci([1.0, 0.0], [1.0])


def test_summary_paired_contrasts_and_detail_verified() -> None:
    rows = run_suite(n_seeds=8, master_seed=2907)
    summary = summarize(rows)
    assert summary["n_trials"] == 8 * 3 * 4
    assert summary["contrast_method"] == "paired_bootstrap_on_seed_task_cells"
    key = "S_GE_minus_S_DETAIL_VERIFIED__oracle_success"
    assert key in summary["contrasts_GE_minus_baseline"]
    ci = summary["contrasts_GE_minus_baseline"][key]
    assert ci["method"] == "bootstrap_paired_diff"
    hyps = hypothesis_verdicts(summary)
    assert "H2b_GE_oracle_gt_DETAIL_VERIFIED" in hyps
    for hid, body in hyps.items():
        if hid == "meta":
            continue
        assert body["verdict"] in {
            "MECHANISM_SUPPORTED",
            "MECHANISM_CONTRADICTED",
            "INCONCLUSIVE",
        }
        assert body["causal_status"] == "NOT_CAUSAL"
        assert body["verdict"] != "CONFIRMED"


def test_seal_refuses_immutable_dir(tmp_path: Path) -> None:
    bad = tmp_path / "v1_immutable"
    bad.mkdir()
    with pytest.raises(RuntimeError, match="immutable"):
        run_and_seal(bad, n_seeds=2, master_seed=1)


def test_seal_writes_appendix(tmp_path: Path) -> None:
    out = tmp_path / "v1_1_post_audit"
    report = run_and_seal(out, n_seeds=5, master_seed=42)
    assert (out / "results.json").is_file()
    data = json.loads((out / "results.json").read_text(encoding="utf-8"))
    assert data["execution_class"] == "EXECUTED_DETERMINISTIC_POST_AUDIT"
    assert data["live_llm_class"] == "PROTOCOL_ONLY_NOT_EXECUTED"
    assert report["hypotheses"]["meta"]["v1_seal_labels"] == (
        "SUPERSEDED_SEE_POST_HOC_AUDIT"
    )


def test_trad_prompt_is_vague() -> None:
    p = build_trad("x", "do the thing")
    assert "best you can" in p.prompt_text.lower()


def test_adversarial_detail_incomplete_multi_step() -> None:
    row = run_trial("S_DETAIL", "multi_step_pipeline", seed=2907)
    assert row.domain == "multi_step"
    assert row.oracle_success == 0.0
    assert row.false_claim == 1.0


def test_detail_verified_passes_multi_step() -> None:
    row = run_trial("S_DETAIL_VERIFIED", "multi_step_pipeline", seed=2907)
    assert row.oracle_success == 1.0
    assert row.false_claim == 0.0


def test_episode_uses_agent_view_end_to_end() -> None:
    world = build_world("research", 7)
    packet = next(s for s in all_task_specs() if s.domain == "research").packets()[
        "S_GE"
    ]
    ep = run_episode(world, packet, seed=7)
    assert ep.strategy_id == "S_GE"
    v = evaluate(world, ep)
    assert isinstance(v.oracle_success, bool)


def test_v1_immutable_seal_present_and_untouched() -> None:
    root = Path("artifacts/goal_engineering/results/v1_immutable")
    assert (root / "results.json").is_file()
    assert (root / "IMMUTABLE.md").is_file()
    data = json.loads((root / "results.json").read_text(encoding="utf-8"))
    # Original seal kept its historical labels; audit demotes them in docs
    assert data["protocol_version"] == "GE-STUDY-v1"
    assert data["summary"]["n_trials"] == 180
