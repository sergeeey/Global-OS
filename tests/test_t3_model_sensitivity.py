"""T3 A/B escape counts must depend on model decisions — not arm/scenario labels alone.

Regression for measurement defect: worst vs best propose_action stubs must change
material escape totals on arms A and B (tip 2f73107 ignored AgentDecision).
"""

from __future__ import annotations

from global_os.evals.trust.pack_v3 import build_pack_v3_sealed
from global_os.evals.trust.t3_agent import AgentDecision
from global_os.evals.trust.t3_arm_runners import run_t3_arm_once


def _count_escapes(traj: dict) -> int:
    return sum(len(m.get("escapes") or []) for m in traj.get("missions") or [])


def _stub_decision(
    *,
    cites_evidence: bool,
    claim_world_success: bool,
    require_observation: bool,
    fidelity: str,
) -> AgentDecision:
    return AgentDecision(
        summary="stub",
        cites_evidence=cites_evidence,
        claim_world_success=claim_world_success,
        require_observation=require_observation,
        raw_text="stub",
        latency_ms=1.0,
        input_tokens=1,
        output_tokens=1,
        provider_id="stub",
        model_id="stub",
        model_version="test",
        temperature=0.0,
        fidelity=fidelity,
        attribution_hint="none_clean",
    )


def test_arm_ab_escape_counts_change_when_propose_action_swapped() -> None:
    pack = build_pack_v3_sealed()
    missions = list(pack["l1_missions"] or [])[:12]
    assert len(missions) >= 4

    def worst(_provider, *, mission_id, scenario, step_id, fidelity, **_kw):
        del _provider, mission_id, scenario, step_id
        return _stub_decision(
            cites_evidence=False,
            claim_world_success=True,
            require_observation=False,
            fidelity=fidelity,
        )

    def best(_provider, *, mission_id, scenario, step_id, fidelity, **_kw):
        del _provider, mission_id, scenario, step_id
        return _stub_decision(
            cites_evidence=True,
            claim_world_success=False,
            require_observation=True,
            fidelity=fidelity,
        )

    for arm_id in ("A", "B"):
        bad = run_t3_arm_once(
            arm_id=arm_id,
            missions=missions,
            seed=301,
            prefer_live=False,
            propose_action_fn=worst,
        )
        good = run_t3_arm_once(
            arm_id=arm_id,
            missions=missions,
            seed=301,
            prefer_live=False,
            propose_action_fn=best,
        )
        bad_n = _count_escapes(bad)
        good_n = _count_escapes(good)
        assert bad_n != good_n, (
            f"arm {arm_id}: escape count insensitive to propose_action "
            f"(worst={bad_n}, best={good_n}) — harness measures script not model"
        )
        assert bad_n > good_n, (
            f"arm {arm_id}: worst stub must produce more escapes than best "
            f"(worst={bad_n}, best={good_n})"
        )
