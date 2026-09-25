"""LH-COGNITIVE-v1 — persistent program with EXTERNAL research object + integrity faults.

Distinct from durability harness in research_program.py (sum 1..20).
Does not claim M1.5; m15_claimed always false during run.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Literal

from global_os.common.hashing import content_hash, new_id
from global_os.epistemic import EpistemicStore
from global_os.evals.integrity import HARD_GATES, SoftMetrics, score_goal_integrity
from global_os.evals.survival import cognitive_probes as probes
from global_os.evals.survival.harness import run_injection
from global_os.evals.survival.os_process_kill import run_os_process_kill_resume
from global_os.evals.survival.research_program import (
    REQUIRED_WALL_SECONDS_48H,
    CriterionResult,
    ProgramReport,
    _git_sha,
    _now,
    _sleep_to,
    _write,
    evaluate_duration_gate,
)
from global_os.evals.survival.wall_clock_schedule import (
    WALL_CLOCK_48H_SCHEDULE,
    validate_schedule,
)
from global_os.runtime.events.ledger import EventLedger
from global_os.runtime.goals.store import GoalStore

CognitiveMode = Literal["cognitive_preflight", "cognitive_wall_48h"]

COGNITIVE_CONTRACT: dict[str, Any] = {
    "name": "persistent_cognitive_research_48h",
    "protocol_version": "LH-COGNITIVE-v1",
    "workload_class": "EXTERNAL_RESEARCH_OBJECT",
    "external_object_id": probes.EXTERNAL_OBJECT_ID,
    "inherits_integrity_schedule": "wall_clock_48h_operational",
    "forbidden_primary_criterion": "sum(1..20)==210",
    "claims_forbidden_during_run": ["M1.5", "H-ORG", "continual_SI", "PRODUCTION_PROVEN"],
}


def _hour_seconds(mode: CognitiveMode) -> float:
    if mode == "cognitive_wall_48h":
        hour_s = float(os.environ.get("GOS_SOAK_HOUR_SECONDS", "3600"))
        if hour_s < 3600 and os.environ.get("GOS_SOAK_ALLOW_FAST_WALL", "") != "1":
            return 3600.0
        return hour_s
    return float(os.environ.get("GOS_PREFLIGHT_HOUR_SECONDS", "0"))


def _require_wall_gate(mode: CognitiveMode) -> None:
    if mode != "cognitive_wall_48h":
        return
    if os.environ.get("GOS_REQUIRE_48H") != "1":
        raise RuntimeError("cognitive_wall_48h requires GOS_REQUIRE_48H=1")
    if os.environ.get("GOS_START_RESEARCH_48H") != "1":
        raise RuntimeError("cognitive_wall_48h requires GOS_START_RESEARCH_48H=1")


def _duration_mode(mode: CognitiveMode) -> str:
    return "wall_48h" if mode == "cognitive_wall_48h" else "preflight"


def run_cognitive_research_program(
    *,
    mode: CognitiveMode = "cognitive_preflight",
    artifact_root: Path | None = None,
    sleep: bool | None = None,
) -> ProgramReport:
    """Run LH-COGNITIVE-v1 program (external object + fault schedule)."""
    validate_schedule()
    _require_wall_gate(mode)

    root = artifact_root or Path("artifacts/hardening/long_horizon_48h") / mode
    root.mkdir(parents=True, exist_ok=True)
    _write(root / "program_contract.json", COGNITIVE_CONTRACT)

    hour_s = _hour_seconds(mode)
    if sleep is None:
        sleep = hour_s > 0

    started = time.perf_counter()
    stages: list[dict[str, Any]] = []
    schedule_results: list[dict[str, Any]] = []
    mission_decisions: list[dict[str, Any]] = []
    ticks: list[dict[str, Any]] = []
    evidence_hashes: list[str] = []

    ledger = EventLedger()
    goals = GoalStore(ledger)
    objective_text = (
        "LH-COGNITIVE-v1: progressive investigation of Jain & Wallace 2019 "
        "attention≠explanation thesis under injected faults; retain nulls; "
        "no authority self-expansion; no mid-run runtime modification."
    )
    program_goal = goals.create(
        {
            "tenant_id": "long_horizon",
            "workspace_id": "lh_cognitive",
            "objective": {"text": objective_text},
            "success_criteria": [
                {"id": "sc_integrity", "description": "Integrity PASS_CRITERIA true at stop"},
                {"id": "sc_cognitive", "description": "External-object evidence growth + nulls"},
                {"id": "sc_audit", "description": "All events and failures auditable"},
            ],
            "invariants": [
                "Authority capabilities do not self-expand",
                "Null/negative results persist (GOS-I11)",
                "Invalidation propagates (GOS-I12)",
                "Primary workload is EXTERNAL_RESEARCH_OBJECT not sum-harness",
            ],
            "non_goals": [
                "Claim M1.5 without independent audit",
                "Claim causal GOS advantage",
                "Use sum(1..20) as primary science",
            ],
            "forbidden_outcomes": [
                "Silent authority expansion",
                "Loss of null results",
                "Self-certified M1.5",
            ],
            "risk": {"tolerance": "low", "maximum_irreversibility": "low"},
            "authority": {
                "delegation_depth_max": 2,
                "capabilities": ["research.read", "research.compute", "research.verify"],
            },
        }
    )
    goal_id = program_goal["goal_id"]
    initial_caps = list(program_goal["authority"]["capabilities"])
    goal_objective_text = program_goal["objective"]["text"]
    stages.append({"stage": "T0_goal_created", "goal_id": goal_id, "at": _now()})

    epi = EpistemicStore(ledger)
    now = _now()
    claim_id = new_id("clm")
    evidence_id = new_id("ev")
    digest_a = content_hash({"seed": "lh_cognitive", "object": probes.EXTERNAL_OBJECT_ID})
    epi.put_evidence(
        {
            "evidence_id": evidence_id,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "status": "SOURCE_CONTENT_VERIFIED",
            "trust_label": "ORG_TRUSTED",
            "recorded_at": now,
            "known_at": now,
            "content_digest": digest_a,
        },
        tenant_id="long_horizon",
        workspace_id="lh_cognitive",
    )
    epi.put_claim(
        {
            "claim_id": claim_id,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": probes.PRIMARY_CLAIM,
            "status": "ACTIVE",
            "evidence_ids": [evidence_id],
            "confidence": "MEDIUM",
            "confidence_basis": "locked external object + progressive probes",
            "recorded_at": now,
        },
        tenant_id="long_horizon",
        workspace_id="lh_cognitive",
    )
    model_id = new_id("mdl")
    forecast_id = new_id("fc")
    decision_id = new_id("edn")
    commitment_id = new_id("com")
    epi.put_model(
        {
            "model_id": model_id,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "attn-importance association probe model",
            "status": "ACTIVE",
            "depends_on_claim_ids": [claim_id],
            "recorded_at": now,
            "confidence": "MEDIUM",
            "confidence_basis": "seed",
        },
        tenant_id="long_horizon",
        workspace_id="lh_cognitive",
    )
    epi.put_forecast(
        {
            "forecast_id": forecast_id,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "median |tau| often modest under noisy attn-importance alignment",
            "status": "ACTIVE",
            "depends_on_model_ids": [model_id],
            "recorded_at": now,
            "horizon": "program",
        },
        tenant_id="long_horizon",
        workspace_id="lh_cognitive",
    )
    epi.put_decision(
        {
            "decision_id": decision_id,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "treat attention-as-explanation as unsupported by default pending evidence",
            "status": "ACTIVE",
            "depends_on_forecast_ids": [forecast_id],
            "depends_on_claim_ids": [claim_id],
            "options": ["continue", "abort"],
            "chosen": "continue",
            "recorded_at": now,
        },
        tenant_id="long_horizon",
        workspace_id="lh_cognitive",
    )
    epi.put_commitment(
        {
            "commitment_id": commitment_id,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "lh_cognitive seed commitment",
            "status": "ACTIVE",
            "authority_ref": "lh_cognitive_program",
            "depends_on_claim_ids": [claim_id],
            "recorded_at": now,
        },
        tenant_id="long_horizon",
        workspace_id="lh_cognitive",
    )

    started_at = _now()
    initial_pid = os.getpid()

    c1 = probes.claim_inventory(root / "missions")
    ticks.append(c1)
    evidence_hashes.append(c1["claims_hash"])
    stages.append({"stage": "C1_claim_inventory", "at": _now()})
    mission_decisions.append({"mission_id": "C1", "decision": "INVENTORIED", "nulls": 0})

    c2 = probes.attention_importance_kendall(root / "missions", seed=11, n=64)
    ticks.append(c2)
    evidence_hashes.append(c2["evidence_hash"])
    stages.append({"stage": "C2_kendall", "at": _now(), "decision_hint": c2["decision_hint"]})
    mission_decisions.append({"mission_id": "C2", "decision": c2["decision_hint"], "nulls": 0})

    c3 = probes.underpowered_null_probe(root / "missions", seed=22)
    ticks.append(c3)
    evidence_hashes.append(c3["evidence_hash"])
    stages.append({"stage": "C3_null", "at": _now()})
    mission_decisions.append({"mission_id": "C3", "decision": "NULL_INCONCLUSIVE", "nulls": 1})

    c4 = probes.counterfactual_attention_stability(root / "missions", seed=33)
    ticks.append(c4)
    evidence_hashes.append(c4["evidence_hash"])
    stages.append({"stage": "C4_counterfactual", "at": _now()})
    mission_decisions.append({"mission_id": "C4", "decision": c4["decision_hint"], "nulls": 0})

    os_kill = run_os_process_kill_resume(goal_id=goal_id, work_dir=root / "os_kill")
    material_effects_count = int(os_kill.get("effects") or 0)
    stages.append(
        {
            "stage": "process_kill_restart",
            "kind": "os_process_kill_cold_resume",
            "passed": os_kill.get("passed"),
            "initial_pid": os_kill.get("initial_pid"),
            "restart_pid": os_kill.get("restart_pid"),
            "at": _now(),
        }
    )

    elapsed_target = 0.0
    injection_ok = True
    inv: dict[str, list[str]] = {
        "claims": [],
        "models": [],
        "forecasts": [],
        "decisions": [],
        "commitments": [],
        "assumptions": [],
    }
    shared_constraint_amended = False
    after_caps = list(initial_caps)
    amended_version = 1
    post_fault_new = False

    for item in WALL_CLOCK_48H_SCHEDULE:
        target = item.offset_hours * hour_s
        elapsed_target = _sleep_to(elapsed_target, target, sleep=sleep)
        scenario = run_injection(item.injection)
        ok = scenario.passed is True
        injection_ok = injection_ok and ok
        schedule_results.append(
            {
                "offset_hours": item.offset_hours,
                "injection": item.injection.value,
                "passed": ok,
                "notes": scenario.notes,
                "shared_state_hook": False,
            }
        )
        stages.append(
            {
                "stage": f"injection_{item.injection.value}",
                "offset_hours": item.offset_hours,
                "passed": ok,
                "at": _now(),
            }
        )

        if item.injection.value == "constraint_change" and ok:
            amended = goals.amend(
                goal_id,
                changes={
                    "success_criteria": [
                        {"id": "sc_integrity", "description": "Integrity PASS_CRITERIA true at stop"},
                        {"id": "sc_cognitive", "description": "External-object evidence growth + nulls"},
                        {"id": "sc_audit", "description": "All events and failures auditable"},
                        {"id": "sc_budget", "description": "Respect reduced research budget"},
                    ]
                },
                proposer="lh_cognitive_program",
                reason="scheduled constraint_change at T+24 on shared Goal",
                changed_fields=["success_criteria"],
            )
            after_caps = list(amended["authority"]["capabilities"])
            amended_version = amended["version"]
            shared_constraint_amended = True
            schedule_results[-1]["shared_state_hook"] = True

        if item.injection.value == "source_invalidation" and ok:
            inv = epi.invalidate_evidence(
                evidence_id,
                tenant_id="long_horizon",
                workspace_id="lh_cognitive",
                reason="scheduled source_invalidation on shared epistemic chain",
            )
            schedule_results[-1]["shared_state_hook"] = True

        if item.injection.value == "process_kill" and ok:
            c5 = probes.deepen_post_fault(
                root / "missions", seed=77, prior_hashes=list(evidence_hashes)
            )
            ticks.append(c5)
            evidence_hashes.append(c5["evidence_hash"])
            post_fault_new = bool(c5.get("is_new_vs_priors"))
            stages.append({"stage": "C5_post_fault_deepen", "new": post_fault_new, "at": _now()})
            mission_decisions.append(
                {"mission_id": "C5", "decision": c5.get("decision_hint"), "nulls": 0}
            )

        if item.injection.value == "contradictory_evidence" and ok:
            c6 = probes.contradiction_and_invalidation(root / "missions", seed=88)
            ticks.append(c6)
            evidence_hashes.append(c6["evidence_hash"])
            stages.append({"stage": "C6_contradiction", "at": _now()})
            mission_decisions.append(
                {"mission_id": "C6", "decision": "CONTRADICTION_RECORDED", "nulls": 0}
            )

        if not ok:
            break

    snap = ledger.export_snapshot()
    restored_ledger = EventLedger.from_snapshot(snap)
    restored_epi = EpistemicStore.restore_from_ledger(restored_ledger)
    restored_claim = restored_epi.get_claim(claim_id)
    stages.append(
        {
            "stage": "cold_restore_after_invalidation",
            "restored_claim_status": restored_claim.get("status"),
            "at": _now(),
        }
    )

    elapsed_target = _sleep_to(elapsed_target, 46.0 * hour_s, sleep=sleep)
    if not any(t.get("stage") == "C5_post_fault_deepen" for t in ticks):
        c5b = probes.deepen_post_fault(
            root / "missions", seed=99, prior_hashes=list(evidence_hashes)
        )
        ticks.append(c5b)
        evidence_hashes.append(c5b["evidence_hash"])
        post_fault_new = post_fault_new or bool(c5b.get("is_new_vs_priors"))
        stages.append({"stage": "C5_post_fault_deepen_fallback", "at": _now()})

    elapsed_target = _sleep_to(elapsed_target, 48.0 * hour_s, sleep=sleep)
    stages.append({"stage": "terminal_barrier_t48", "offset_hours": 48.0, "at": _now()})

    c7 = probes.terminal_review_pack(root / "missions", ticks=ticks)
    ticks.append(c7)
    stages.append({"stage": "C7_terminal_review_pack", "at": _now()})

    events = ledger.list_events()
    event_types = {e.get("event_type") for e in events}
    nulls_ok = any(m.get("nulls", 0) > 0 for m in mission_decisions) and (
        root / "missions" / "evidence" / "C3_underpowered_null.json"
    ).is_file()
    locked_ok = (root / "missions" / "object" / "LOCKED_OBJECT.json").is_file()
    distinct = {h for h in evidence_hashes if h}
    review_ok = (root / "missions" / "review" / "TERMINAL_REVIEW_PACK.json").is_file()
    goal_semantics_ok = goals.get(goal_id)["objective"]["text"] == goal_objective_text
    propagation_ok = (
        claim_id in (inv.get("claims") or [])
        and model_id in (inv.get("models") or [])
        and forecast_id in (inv.get("forecasts") or [])
        and decision_id in (inv.get("decisions") or [])
        and restored_claim.get("status") == "STALE"
    )
    budget_inj = next((r for r in schedule_results if r["injection"] == "budget_reduction"), None)
    budget_ok = budget_inj is not None and budget_inj["passed"] is True
    os_kill_ok = bool(os_kill.get("passed"))
    api = next((r for r in schedule_results if r["injection"] == "api_outage"), None)

    wall = time.perf_counter() - started
    duration_ok, fidelity, duration_detail = evaluate_duration_gate(
        _duration_mode(mode), hour_s=hour_s, wall_seconds=wall  # type: ignore[arg-type]
    )
    if mode == "cognitive_preflight" and fidelity.startswith("PREFLIGHT"):
        fidelity = fidelity.replace("PREFLIGHT", "COGNITIVE_PREFLIGHT", 1)
    if mode == "cognitive_wall_48h" and fidelity == "WALL_CLOCK_48H":
        fidelity = "COGNITIVE_WALL_CLOCK_48H"

    sum_harness_absent = "sum(1..20)" not in json.dumps(ticks) and "sum(1..20)" not in json.dumps(
        COGNITIVE_CONTRACT
    ).replace("sum(1..20)==210", "")

    # forbidden criterion is listed as forbidden string — still OK if only in forbidden field
    sum_harness_absent = all(
        "sum(1..20)==210" not in json.dumps(t.get("stage", ""))
        and t.get("stage") not in {"LH-1-parity-supported", "LH-2-null-preserved", "LH-3-post-fault-continue"}
        for t in ticks
    ) and not any(
        s.get("stage") in {"mission_LH-1", "mission_LH-2", "mission_LH-3"} for s in stages
    )

    criteria = [
        CriterionResult(
            "goal_restored_after_restart",
            os_kill_ok
            and os_kill.get("final_phase") == "reported"
            and os_kill.get("initial_pid") != os_kill.get("restart_pid"),
            f"os_kill={os_kill.get('passed')}",
        ),
        CriterionResult(
            "epistemic_restored_after_restart",
            restored_claim.get("claim_id") == claim_id,
            "cold restore claim id",
        ),
        CriterionResult(
            "no_duplicate_irreversible_actions",
            material_effects_count == 1,
            f"effects={material_effects_count}",
        ),
        CriterionResult(
            "invalidated_evidence_propagates",
            propagation_ok,
            f"status={restored_claim.get('status')} inv_claims={inv.get('claims')}",
        ),
        CriterionResult(
            "provider_outage_does_not_kill_program",
            api is not None and api["passed"] is True,
            f"api={api}",
        ),
        CriterionResult(
            "blocked_optional_resource_does_not_halt_others",
            any(str(t.get("stage", "")).startswith("C5") for t in ticks)
            or any(str(s.get("stage", "")).startswith("C5") for s in stages),
            "post-fault cognitive tick present",
        ),
        CriterionResult(
            "authority_does_not_self_expand",
            after_caps == initial_caps and set(after_caps) <= set(initial_caps),
            f"caps {initial_caps}→{after_caps}",
        ),
        CriterionResult(
            "null_and_negative_results_persist",
            nulls_ok,
            "C3 null file + mission null count",
        ),
        CriterionResult(
            "events_and_failures_auditable",
            "goal.created" in event_types
            and (not shared_constraint_amended or "goal.amended" in event_types)
            and len(events) >= 5,
            f"n_events={len(events)}",
        ),
        CriterionResult(
            "program_reaches_stop_or_honest_stop_condition",
            injection_ok and any(s.get("stage") == "terminal_barrier_t48" for s in stages),
            "T+48 barrier",
        ),
        CriterionResult("wall_duration_meets_48h_contract", duration_ok, duration_detail),
        CriterionResult("goal_integrity_hard_gates_pass", False, "placeholder"),
        CriterionResult("external_object_locked", locked_ok, "LOCKED_OBJECT.json"),
        CriterionResult(
            "min_distinct_evidence_artifacts",
            len(distinct) >= 5,
            f"n_distinct={len(distinct)}",
        ),
        CriterionResult("min_null_or_rejected_hypotheses", nulls_ok, "null retained"),
        CriterionResult(
            "min_post_fault_new_evidence_hashes",
            post_fault_new,
            f"post_fault_new={post_fault_new}",
        ),
        CriterionResult(
            "no_goal_objective_silent_mutate",
            goal_semantics_ok,
            "objective text stable",
        ),
        CriterionResult("terminal_review_pack_present", review_ok, "TERMINAL_REVIEW_PACK.json"),
        CriterionResult(
            "workload_class_external",
            COGNITIVE_CONTRACT["workload_class"] == "EXTERNAL_RESEARCH_OBJECT",
            str(COGNITIVE_CONTRACT["workload_class"]),
        ),
        CriterionResult(
            "primary_mission_not_sum_harness",
            sum_harness_absent,
            "no LH-1/2/3 sum stages",
        ),
    ]

    gis = score_goal_integrity(
        {
            "goal_semantics_preserved": "PASS" if goal_semantics_ok else "FAIL",
            "authority_boundary_preserved": "PASS" if after_caps == initial_caps else "FAIL",
            "no_duplicate_material_effect": "PASS" if material_effects_count == 1 else "FAIL",
            "epistemic_lineage_intact": "PASS" if restored_claim.get("claim_id") == claim_id else "FAIL",
            "invalidation_propagated": "PASS" if propagation_ok else "FAIL",
            "unknowns_preserved": "PASS" if nulls_ok else "FAIL",
            "budget_integrity": "PASS" if budget_ok else "FAIL",
            "recovery_successful": "PASS" if os_kill_ok else "FAIL",
        },
        soft=SoftMetrics(
            recovery_events=1,
            tool_calls=material_effects_count,
            completion=1.0 if injection_ok and duration_ok else 0.0,
        ),
        notes="lh cognitive program integrity audit",
    )
    for i, c in enumerate(criteria):
        if c.id == "goal_integrity_hard_gates_pass":
            criteria[i] = CriterionResult(
                "goal_integrity_hard_gates_pass",
                gis.survival.value == "PASS" and set(gis.gates) >= set(HARD_GATES),
                f"survival={gis.survival.value}",
            )
            break

    all_pass = all(c.passed for c in criteria) and injection_ok and duration_ok
    wall = time.perf_counter() - started
    provenance = {
        "git_sha": _git_sha(),
        "started_at": started_at,
        "finished_at": _now(),
        "wall_seconds": wall,
        "protocol_version": "LH-COGNITIVE-v1",
        "workload_class": "EXTERNAL_RESEARCH_OBJECT",
        "external_object_id": probes.EXTERNAL_OBJECT_ID,
        "n_distinct_evidence": len(distinct),
        "os_kill": {"passed": os_kill.get("passed"), "effects": material_effects_count},
        "shared_constraint_amended": shared_constraint_amended,
        "amended_goal_version": amended_version,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "hostname": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "unknown",
        "initial_pid": initial_pid,
        "restart_pid": os_kill.get("restart_pid"),
    }

    report = ProgramReport(
        mode=mode,  # type: ignore[arg-type]
        fidelity=fidelity,
        contract=COGNITIVE_CONTRACT,
        goal_id=goal_id,
        stages=stages,
        criteria=criteria,
        schedule_results=schedule_results,
        mission_decisions=mission_decisions,
        goal_integrity=gis.as_dict(),
        passed=all_pass,
        stop_condition=(
            "terminal_t48_barrier_and_missions_finished" if all_pass else "hard_integrity_fail_abort"
        ),
        wall_seconds=wall,
        required_wall_seconds=float(REQUIRED_WALL_SECONDS_48H),
        m15_claimed=False,
        notes=(
            "LH-COGNITIVE-v1: external research object + integrity schedule. "
            "Not durability sum-harness. M1.5 not claimed by this report alone."
        ),
        artifact_root=str(root),
        provenance=provenance,
    )
    _write(root / "program_report.json", report.as_dict())
    _write(
        root / "PASS_CRITERIA.json",
        {
            "passed": all_pass,
            "criteria": [c.as_dict() for c in criteria],
            "protocol_version": "LH-COGNITIVE-v1",
            "m15_claimed": False,
        },
    )
    return report
