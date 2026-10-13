"""T3 A/B/C2 outcomes must depend on model decisions — not arm/scenario labels alone.

Regression for measurement defect: worst vs best propose_action stubs must change
material escape totals on arms A and B (tip 2f73107 ignored AgentDecision).
C2: router actions must change (decision-coupled; frozen recovery_router.py untouched).
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


def _worst_best_stubs():
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

    return worst, best


def test_arm_ab_escape_counts_change_when_propose_action_swapped() -> None:
    pack = build_pack_v3_sealed()
    missions = list(pack["l1_missions"] or [])[:12]
    assert len(missions) >= 4
    worst, best = _worst_best_stubs()

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


def test_arm_c2_router_actions_change_when_propose_action_swapped() -> None:
    """C2 must not scenario-force recovery when the model proposal is already GREEN.

    Use ambiguous_effect missions: claim_world_success couples cleanly. Mixing
    stale_evidence (cite-sensitive) can cancel CONTINUE totals across scenarios.
    """
    pack = build_pack_v3_sealed()
    missions = [
        m
        for m in (pack["l1_missions"] or [])
        if m.get("scenario") == "ambiguous_effect"
    ]
    assert len(missions) >= 2
    worst, best = _worst_best_stubs()

    bad = run_t3_arm_once(
        arm_id="C2",
        missions=missions,
        seed=301,
        prefer_live=False,
        propose_action_fn=worst,
    )
    good = run_t3_arm_once(
        arm_id="C2",
        missions=missions,
        seed=301,
        prefer_live=False,
        propose_action_fn=best,
    )
    assert bad.get("router_actions") != good.get("router_actions"), (
        "arm C2: router_actions insensitive to propose_action "
        f"(worst={bad.get('router_actions')}, best={good.get('router_actions')}) "
        "— scenario labels alone drove recovery"
    )
    # Safer model should CONTINUE; worst claim_world_success triggers recovery.
    assert int((good.get("router_actions") or {}).get("CONTINUE", 0)) > int(
        (bad.get("router_actions") or {}).get("CONTINUE", 0)
    )
    assert int((bad.get("router_actions") or {}).get("SAFE_RECOVERY", 0)) > int(
        (good.get("router_actions") or {}).get("SAFE_RECOVERY", 0)
    )
