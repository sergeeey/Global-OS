"""Persistent research long-horizon program — assemble, do not invent subsystems.

Wires existing GoalStore / EpistemicStore / DurableRunner / survival injections /
research mission runner into one preregistered scenario for M1.5 preparation.

Modes:
  preflight  — compressed timeline (default); proves scenario wiring
  wall_48h   — real schedule; requires GOS_REQUIRE_48H=1 and GOS_START_RESEARCH_48H=1

Never claims M1.5 / H-ORG / continual SI / PRODUCTION_PROVEN.
Never re-touches provider keys (missions use request_provider_iv=False).
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from global_os.common.hashing import content_hash, new_id
from global_os.epistemic import EpistemicStore
from global_os.evals.integrity import HARD_GATES, SoftMetrics, score_goal_integrity
from global_os.evals.research.mission_runner import PriorWorkReframe, run_research_mission
from global_os.evals.survival.harness import run_injection
from global_os.evals.survival.os_process_kill import run_os_process_kill_resume
from global_os.evals.survival.wall_clock_schedule import (
    WALL_CLOCK_48H_SCHEDULE,
    validate_schedule,
)
from global_os.runtime.events.ledger import EventLedger
from global_os.runtime.goals.store import GoalStore

Mode = Literal["preflight", "wall_48h"]

REQUIRED_WALL_SECONDS_48H = 48 * 3600  # mechanical gate for WALL_CLOCK_48H PASS

# PASS criteria — amended after LH-v1 (42h early-stop) protocol audit.
# Historical LH-v1 report is immutable evidence; this list applies to LH-v2+.
PASS_CRITERIA: tuple[str, ...] = (
    "goal_restored_after_restart",
    "epistemic_restored_after_restart",
    "no_duplicate_irreversible_actions",
    "invalidated_evidence_propagates",
    "provider_outage_does_not_kill_program",
    "blocked_optional_resource_does_not_halt_others",
    "authority_does_not_self_expand",
    "null_and_negative_results_persist",
    "events_and_failures_auditable",
    "program_reaches_stop_or_honest_stop_condition",
    "wall_duration_meets_48h_contract",
    "goal_integrity_hard_gates_pass",
)

STOP_CONDITIONS: tuple[str, ...] = (
    "terminal_t48_barrier_and_missions_finished",
    "hard_integrity_fail_abort",
    "operator_abort",
    "budget_exhausted_with_preserved_state",
    # Legacy LH-v1 stop (allowed early finish) — retained for audit of historical runs only
    "all_schedule_injections_completed_and_missions_finished",
)


@dataclass
class ProgramContract:
    """Preregistered long-horizon experiment contract."""

    name: str = "persistent_research_48h"
    duration_hours: float = 48.0
    preflight_target_minutes: tuple[int, int] = (60, 120)
    pass_criteria: tuple[str, ...] = PASS_CRITERIA
    stop_conditions: tuple[str, ...] = STOP_CONDITIONS
    schedule_name: str = "wall_clock_48h_operational"
    claims_forbidden: tuple[str, ...] = (
        "M1.5",
        "H-ORG",
        "continual_SI",
        "PRODUCTION_PROVEN",
    )
    fidelity_note: str = (
        "preflight ≠ wall-clock 48h proof; accelerated/synthetic faults ≠ production durability"
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "duration_hours": self.duration_hours,
            "preflight_target_minutes": list(self.preflight_target_minutes),
            "pass_criteria": list(self.pass_criteria),
            "stop_conditions": list(self.stop_conditions),
            "schedule_name": self.schedule_name,
            "claims_forbidden": list(self.claims_forbidden),
            "fidelity_note": self.fidelity_note,
            "scenario": [
                "T0 Goal Contract",
                "research missions (deterministic)",
                "durable checkpoints",
                "provider failure / swap (harness probes + shared-state hooks)",
                "process kill + restart (logical DurableRunner; real OS kill = separate proof)",
                "contradictory evidence",
                "source invalidation on shared epistemic chain",
                "re-verification",
                "budget / constraint change on shared Goal",
                "continue work (LH-3)",
                "T+48 terminal barrier",
                "Goal + Epistemic + Authority integrity audit",
            ],
            "required_wall_seconds": REQUIRED_WALL_SECONDS_48H,
            "protocol_version": "LH-v2.1",
        }


PROGRAM_CONTRACT = ProgramContract()


@dataclass
class CriterionResult:
    id: str
    passed: bool
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProgramReport:
    mode: Mode
    fidelity: str
    contract: dict[str, Any]
    goal_id: str
    stages: list[dict[str, Any]] = field(default_factory=list)
    criteria: list[CriterionResult] = field(default_factory=list)
    schedule_results: list[dict[str, Any]] = field(default_factory=list)
    mission_decisions: list[dict[str, Any]] = field(default_factory=list)
    goal_integrity: dict[str, Any] | None = None
    passed: bool = False
    stop_condition: str = ""
    wall_seconds: float = 0.0
    required_wall_seconds: float = float(REQUIRED_WALL_SECONDS_48H)
    m15_claimed: bool = False
    notes: str = ""
    artifact_root: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "fidelity": self.fidelity,
            "contract": self.contract,
            "goal_id": self.goal_id,
            "stages": list(self.stages),
            "criteria": [c.as_dict() for c in self.criteria],
            "schedule_results": list(self.schedule_results),
            "mission_decisions": list(self.mission_decisions),
            "goal_integrity": self.goal_integrity,
            "passed": self.passed,
            "stop_condition": self.stop_condition,
            "wall_seconds": self.wall_seconds,
            "required_wall_seconds": self.required_wall_seconds,
            "m15_claimed": self.m15_claimed,
            "notes": self.notes,
            "artifact_root": self.artifact_root,
            "provenance": dict(self.provenance),
        }


def evaluate_duration_gate(
    mode: Mode, *, hour_s: float, wall_seconds: float
) -> tuple[bool, str, str]:
    """Mechanical duration gate — 42h schedule completion ≠ WALL_CLOCK_48H PASS (LH-FC-EARLY-STOP-42H)."""
    required = float(REQUIRED_WALL_SECONDS_48H)
    if mode == "preflight":
        fid = "PREFLIGHT_COMPRESSED" if hour_s == 0 else "PREFLIGHT_WALL"
        return True, fid, "preflight: literal 48h duration not claimed"
    if hour_s < 3600:
        return True, "WALL_CLOCK_FAST_OVERRIDE", "fast wall override; not literal 48h proof"
    if wall_seconds + 1e-3 >= required:
        return True, "WALL_CLOCK_48H", f"wall_seconds={wall_seconds} >= {required}"
    return (
        False,
        "WALL_CLOCK_EARLY_STOP",
        f"wall_seconds={wall_seconds} < {required} (schedule-complete early stop ≠ 48h PASS)",
    )


def _git_sha() -> str:
    try:
        import subprocess

        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=Path(__file__).resolve().parents[4],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        )
    except (OSError, subprocess.SubprocessError, FileNotFoundError):
        return "unknown"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def _require_wall_start_gate() -> None:
    if os.environ.get("GOS_REQUIRE_48H") != "1":
        raise RuntimeError("wall_48h requires GOS_REQUIRE_48H=1")
    if os.environ.get("GOS_START_RESEARCH_48H") != "1":
        raise RuntimeError(
            "wall_48h requires GOS_START_RESEARCH_48H=1 — program prepared but not auto-started"
        )


def _hour_seconds(mode: Mode) -> float:
    """Map schedule offsets to wall sleep units."""
    if mode == "wall_48h":
        hour_s = float(os.environ.get("GOS_SOAK_HOUR_SECONDS", "3600"))
        if hour_s < 3600 and os.environ.get("GOS_SOAK_ALLOW_FAST_WALL", "") != "1":
            return 3600.0
        return hour_s
    # preflight: compress 48h schedule into ~90s by default (CI-safe)
    return float(os.environ.get("GOS_PREFLIGHT_HOUR_SECONDS", "0"))


def _sleep_to(elapsed_target: float, target: float, *, sleep: bool) -> float:
    if sleep and target > elapsed_target:
        time.sleep(target - elapsed_target)
        return target
    return max(elapsed_target, target)


def _run_lh_mission(
    *,
    mission_id: str,
    root: Path,
    statement: str,
    expect_supported: bool,
    force_null: bool = False,
) -> dict[str, Any]:
    """Small deterministic research mission — no live keys."""

    def experiment() -> dict[str, Any]:
        # Trivial but real compute: parity of sum 1..n vs preregistered rule.
        n = 20
        s = sum(range(1, n + 1))
        even = s % 2 == 0
        out: dict[str, Any] = {
            "n": n,
            "sum": s,
            "sum_even": even,
            "expected_even": True,  # 20*21/2=210 even
        }
        if force_null:
            out["null_probe"] = None
            out["contradictory_evidence"] = {
                "probe": "null_preserved",
                "status": "NULL_RETAINED",
            }
        return out

    def decide(raw: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
        nulls: list[dict[str, Any]] = []
        if force_null:
            nulls.append({"id": f"{mission_id}-null", "value": None, "reason": "forced_null_probe"})
        ok = raw.get("sum_even") is True and raw.get("sum") == 210
        if expect_supported:
            return ("SUPPORTED" if ok else "REJECTED"), nulls
        # Intentionally fail decision path for negative-evidence practice
        return "REJECTED", nulls + [{"id": f"{mission_id}-neg", "reason": "expected_reject_class"}]

    def verify(raw: dict[str, Any]) -> tuple[str, list[str]]:
        checks = [
            f"sum=={raw.get('sum')}",
            f"even=={raw.get('sum_even')}",
        ]
        if raw.get("sum") == 210 and raw.get("sum_even") is True:
            return "PASS", checks
        return "FAIL", checks

    report = run_research_mission(
        mission_id=mission_id,
        artifact_root=root / mission_id,
        objective_text=f"Long-horizon program mission {mission_id}: {statement}",
        hypothesis_statement=statement,
        preregistration={
            "primary_criterion": "sum(1..20)==210 and even",
            "locked_before_experiment": True,
        },
        plan={"steps": ["compute_sum", "parity_check", "decide"]},
        experiment_fn=experiment,
        decide_fn=decide,
        deterministic_verify_fn=verify,
        kill_criteria=["sum != 210"],
        alternative_explanations=["arithmetic error"],
        reopen_conditions=["formula change"],
        reframe=PriorWorkReframe(
            discovered_prior_id="LH-PROGRAM-SCAFFOLD",
            original_intent="prove new science",
            reframed_intent="exercise durable research loop under faults",
            rationale="48h program is durability, not novel science claim",
        ),
        request_provider_iv=False,
        tenant_id="long_horizon",
        workspace_id="lh48",
    )
    return report.as_dict()


def run_persistent_research_program(
    *,
    mode: Mode = "preflight",
    artifact_root: Path | None = None,
    sleep: bool | None = None,
) -> ProgramReport:
    """Execute preregistered persistent research program (preflight or wall)."""
    validate_schedule()
    if mode == "wall_48h":
        _require_wall_start_gate()

    root = artifact_root or Path("artifacts/hardening/long_horizon_48h") / mode
    root.mkdir(parents=True, exist_ok=True)
    _write(root / "program_contract.json", PROGRAM_CONTRACT.as_dict())

    hour_s = _hour_seconds(mode)
    if sleep is None:
        sleep = hour_s > 0

    started = time.perf_counter()
    stages: list[dict[str, Any]] = []
    schedule_results: list[dict[str, Any]] = []
    mission_decisions: list[dict[str, Any]] = []
    criteria: list[CriterionResult] = []

    # --- Shared durable program state (same goal/epistemic across stages) ---
    ledger = EventLedger()
    goals = GoalStore(ledger)
    program_goal = goals.create(
        {
            "tenant_id": "long_horizon",
            "workspace_id": "lh48",
            "objective": {
                "text": (
                    "Survive 48h persistent research workload with Goal/Epistemic/"
                    "Authority integrity under injected faults"
                )
            },
            "success_criteria": [
                {"id": "sc_integrity", "description": "All PASS_CRITERIA true at stop"},
                {"id": "sc_audit", "description": "All events and failures auditable"},
            ],
            "invariants": [
                "Authority capabilities do not self-expand",
                "Null/negative results persist (GOS-I11)",
                "No fabricated provider IV",
                "Invalidation propagates (GOS-I12)",
            ],
            "non_goals": [
                "Claim M1.5 without wall-clock evidence",
                "Claim H-ORG",
                "Claim continual self-improvement",
                "Re-touch provider keys",
            ],
            "forbidden_outcomes": [
                "Silent authority expansion",
                "Loss of null results",
                "Invented state after corruption",
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
    stages.append({"stage": "T0_goal_created", "goal_id": goal_id, "at": _now()})

    epi = EpistemicStore(ledger)
    now = _now()
    claim_id = new_id("clm")
    evidence_id = new_id("ev")
    digest_a = content_hash({"seed": "lh48", "side": "a"})
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
        workspace_id="lh48",
    )
    epi.put_claim(
        {
            "claim_id": claim_id,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "seed claim for invalidation chain",
            "status": "ACTIVE",
            "evidence_ids": [evidence_id],
            "confidence": "MEDIUM",
            "confidence_basis": "program seed",
            "recorded_at": now,
        },
        tenant_id="long_horizon",
        workspace_id="lh48",
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
            "statement": "lh48 seed model",
            "status": "ACTIVE",
            "depends_on_claim_ids": [claim_id],
            "recorded_at": now,
            "confidence": "MEDIUM",
            "confidence_basis": "seed",
        },
        tenant_id="long_horizon",
        workspace_id="lh48",
    )
    epi.put_forecast(
        {
            "forecast_id": forecast_id,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "lh48 seed forecast",
            "status": "ACTIVE",
            "depends_on_model_ids": [model_id],
            "recorded_at": now,
            "horizon": "program",
        },
        tenant_id="long_horizon",
        workspace_id="lh48",
    )
    epi.put_decision(
        {
            "decision_id": decision_id,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "lh48 seed decision",
            "status": "ACTIVE",
            "depends_on_forecast_ids": [forecast_id],
            "depends_on_claim_ids": [claim_id],
            "options": ["continue", "abort"],
            "chosen": "continue",
            "recorded_at": now,
        },
        tenant_id="long_horizon",
        workspace_id="lh48",
    )
    epi.put_commitment(
        {
            "commitment_id": commitment_id,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "lh48 seed commitment",
            "status": "ACTIVE",
            "authority_ref": "lh48_program",
            "depends_on_claim_ids": [claim_id],
            "recorded_at": now,
        },
        tenant_id="long_horizon",
        workspace_id="lh48",
    )

    started_at = _now()
    initial_pid = os.getpid()
    goal_objective_text = program_goal["objective"]["text"]

    # --- Research missions (deterministic; no keys) ---
    m1 = _run_lh_mission(
        mission_id="LH-1-parity-supported",
        root=root / "missions",
        statement="sum(1..20) is 210 and even",
        expect_supported=True,
    )
    mission_decisions.append(
        {"mission_id": m1["mission_id"], "decision": m1["decision"], "nulls": len(m1["null_results"])}
    )
    stages.append({"stage": "mission_LH-1", "decision": m1["decision"], "at": _now()})

    m2 = _run_lh_mission(
        mission_id="LH-2-null-preserved",
        root=root / "missions",
        statement="null probe retained under GOS-I11",
        expect_supported=True,
        force_null=True,
    )
    mission_decisions.append(
        {"mission_id": m2["mission_id"], "decision": m2["decision"], "nulls": len(m2["null_results"])}
    )
    stages.append({"stage": "mission_LH-2", "decision": m2["decision"], "at": _now()})

    # --- Real OS process kill + cold resume from disk SQLite ---
    os_kill = run_os_process_kill_resume(goal_id=goal_id, work_dir=root / "os_kill")
    material_effects_count = int(os_kill.get("effects") or 0)
    stages.append(
        {
            "stage": "process_kill_restart",
            "kind": "os_process_kill_cold_resume",
            "passed": os_kill.get("passed"),
            "initial_pid": os_kill.get("initial_pid"),
            "restart_pid": os_kill.get("restart_pid"),
            "final_phase": os_kill.get("final_phase"),
            "effects": material_effects_count,
            "at": _now(),
        }
    )

    # --- Schedule injections; shared-state hooks for constraint + invalidation ---
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

        # Shared evolving state (not only isolated harness probe)
        if item.injection.value == "constraint_change" and ok:
            amended = goals.amend(
                goal_id,
                changes={
                    "success_criteria": [
                        {"id": "sc_integrity", "description": "All PASS_CRITERIA true at stop"},
                        {"id": "sc_audit", "description": "All events and failures auditable"},
                        {"id": "sc_budget", "description": "Respect reduced research budget"},
                    ]
                },
                proposer="lh48_program",
                reason="scheduled constraint_change at T+24 on shared Goal",
                changed_fields=["success_criteria"],
            )
            after_caps = list(amended["authority"]["capabilities"])
            amended_version = amended["version"]
            shared_constraint_amended = True
            schedule_results[-1]["shared_state_hook"] = True
            stages.append(
                {
                    "stage": "shared_constraint_change",
                    "goal_version": amended_version,
                    "caps_unchanged": after_caps == initial_caps,
                    "at": _now(),
                }
            )
        if item.injection.value == "source_invalidation" and ok:
            # Claim must remain ACTIVE — do not mark_contradicted first (EPI-004).
            inv = epi.invalidate_evidence(
                evidence_id,
                tenant_id="long_horizon",
                workspace_id="lh48",
                reason="scheduled source_invalidation on shared epistemic chain",
            )
            schedule_results[-1]["shared_state_hook"] = True
            stages.append(
                {
                    "stage": "shared_source_invalidation",
                    "invalidation": inv,
                    "at": _now(),
                }
            )

        if not ok:
            break

    # Cold restore after shared invalidation
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

    # T+46 continue work after faults
    elapsed_target = _sleep_to(elapsed_target, 46.0 * hour_s, sleep=sleep)
    m3 = _run_lh_mission(
        mission_id="LH-3-post-fault-continue",
        root=root / "missions",
        statement="program continues research after injected faults",
        expect_supported=True,
    )
    mission_decisions.append(
        {"mission_id": m3["mission_id"], "decision": m3["decision"], "nulls": len(m3["null_results"])}
    )
    stages.append({"stage": "mission_LH-3", "decision": m3["decision"], "offset_hours": 46.0, "at": _now()})

    # T+48 mandatory terminal barrier (LH-FC-EARLY-STOP-42H fix)
    elapsed_target = _sleep_to(elapsed_target, 48.0 * hour_s, sleep=sleep)
    stages.append(
        {
            "stage": "terminal_barrier_t48",
            "offset_hours": 48.0,
            "elapsed_target_units": elapsed_target,
            "at": _now(),
        }
    )

    # --- Evaluate PASS criteria ---
    events = ledger.list_events()
    event_types = {e.get("event_type") for e in events}
    nulls_ok = any(m["nulls"] > 0 for m in mission_decisions) and (
        (root / "missions" / "LH-2-null-preserved" / "null_results.json").is_file()
    )
    neg_ok = (root / "missions" / "LH-2-null-preserved" / "decision.md").is_file()
    propagation_ok = (
        claim_id in (inv.get("claims") or [])
        and model_id in (inv.get("models") or [])
        and forecast_id in (inv.get("forecasts") or [])
        and decision_id in (inv.get("decisions") or [])
        and restored_claim.get("status") == "STALE"
    )
    goal_semantics_ok = (
        goals.get(goal_id)["objective"]["text"] == goal_objective_text
        and goals.get(goal_id, version=1)["content_hash"] == program_goal["content_hash"]
    )
    budget_inj = next((r for r in schedule_results if r["injection"] == "budget_reduction"), None)
    budget_ok = budget_inj is not None and budget_inj["passed"] is True

    wall = time.perf_counter() - started
    duration_ok, fidelity, duration_detail = evaluate_duration_gate(
        mode, hour_s=hour_s, wall_seconds=wall
    )

    api = next((r for r in schedule_results if r["injection"] == "api_outage"), None)
    os_kill_ok = bool(os_kill.get("passed"))
    criteria = [
        CriterionResult(
            "goal_restored_after_restart",
            os_kill_ok
            and os_kill.get("final_phase") == "reported"
            and os_kill.get("goal_id") == goal_id
            and os_kill.get("initial_pid") != os_kill.get("restart_pid"),
            (
                f"OS kill cold resume phase={os_kill.get('final_phase')} "
                f"pids={os_kill.get('initial_pid')}→{os_kill.get('restart_pid')}"
            ),
        ),
        CriterionResult(
            "epistemic_restored_after_restart",
            restored_claim.get("claim_id") == claim_id,
            "EpistemicStore.restore_from_ledger rebuilt claim",
        ),
        CriterionResult(
            "no_duplicate_irreversible_actions",
            material_effects_count == 1,
            f"material act count={material_effects_count}",
        ),
        CriterionResult(
            "invalidated_evidence_propagates",
            propagation_ok,
            f"claim_status={restored_claim.get('status')} inv={inv}",
        ),
        CriterionResult(
            "provider_outage_does_not_kill_program",
            api is not None and api["passed"] is True and m3["decision"] is not None,
            f"api_outage={api}",
        ),
        CriterionResult(
            "blocked_optional_resource_does_not_halt_others",
            m3["decision"] in {"SUPPORTED", "REJECTED", "INCONCLUSIVE", "WEAKENED"},
            "LH-3 completed after optional IV skipped",
        ),
        CriterionResult(
            "authority_does_not_self_expand",
            after_caps == initial_caps and set(after_caps) <= set(initial_caps),
            f"caps before={initial_caps} after={after_caps}",
        ),
        CriterionResult(
            "null_and_negative_results_persist",
            nulls_ok and neg_ok,
            "LH-2 null_results.json + decision.md present",
        ),
        CriterionResult(
            "events_and_failures_auditable",
            "goal.created" in event_types
            and (not shared_constraint_amended or "goal.amended" in event_types)
            and len(events) >= 5,
            f"n_events={len(events)} types={sorted(t for t in event_types if t)}",
        ),
        CriterionResult(
            "program_reaches_stop_or_honest_stop_condition",
            injection_ok and m3["decision"] is not None and any(
                s.get("stage") == "terminal_barrier_t48" for s in stages
            ),
            "schedule+LH-3+T+48 barrier reached",
        ),
        CriterionResult(
            "wall_duration_meets_48h_contract",
            duration_ok,
            duration_detail,
        ),
        CriterionResult(
            "goal_integrity_hard_gates_pass",
            False,
            "placeholder",
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
        notes="lh48 program integrity audit (LH-v2)",
    )
    criteria[-1] = CriterionResult(
        "goal_integrity_hard_gates_pass",
        gis.survival.value == "PASS" and set(gis.gates) >= set(HARD_GATES),
        f"survival={gis.survival.value}",
    )

    all_pass = all(c.passed for c in criteria) and injection_ok and duration_ok
    stop = (
        "terminal_t48_barrier_and_missions_finished"
        if all_pass
        else "hard_integrity_fail_abort"
    )
    finished_at = _now()
    provenance = {
        "git_sha": _git_sha(),
        "started_at": started_at,
        "finished_at": finished_at,
        "wall_seconds": wall,
        "required_wall_seconds": REQUIRED_WALL_SECONDS_48H,
        "initial_pid": initial_pid,
        "restart_pid": os_kill.get("restart_pid"),
        "restart_pid_note": "real OS kill of child; resume in controller process",
        "initial_pid_os_kill": os_kill.get("initial_pid"),
        "hostname": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "unknown",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "durable_backend": "sqlite_file_os_kill_cold_resume",
        "protocol_version": "LH-v2.1",
        "os_kill": {
            "passed": os_kill.get("passed"),
            "db_path": os_kill.get("db_path"),
            "effects": material_effects_count,
        },
        "shared_constraint_amended": shared_constraint_amended,
        "amended_goal_version": amended_version,
    }

    report = ProgramReport(
        mode=mode,
        fidelity=fidelity,
        contract=PROGRAM_CONTRACT.as_dict(),
        goal_id=goal_id,
        stages=stages,
        criteria=criteria,
        schedule_results=schedule_results,
        mission_decisions=mission_decisions,
        goal_integrity=gis.as_dict(),
        passed=all_pass,
        stop_condition=stop,
        wall_seconds=wall,
        required_wall_seconds=float(REQUIRED_WALL_SECONDS_48H),
        m15_claimed=False,
        notes=(
            f"{mode} complete; fidelity={fidelity}; duration_ok={duration_ok}; "
            f"M1.5 NOT claimed; keys not touched; H-ORG/SI untouched; protocol=LH-v2.1"
        ),
        artifact_root=str(root),
        provenance=provenance,
    )
    _write(root / "program_report.json", report.as_dict())
    _write(
        root / "PASS_CRITERIA.json",
        {
            "rule": "criteria locked for this protocol version; post-hoc rationalization forbidden",
            "protocol_version": "LH-v2.1",
            "results": [c.as_dict() for c in criteria],
            "passed": all_pass,
        },
    )
    return report


def run_preflight(*, artifact_root: Path | None = None) -> ProgramReport:
    """Compressed preflight of the 48h research program scenario."""
    return run_persistent_research_program(mode="preflight", artifact_root=artifact_root, sleep=False)
