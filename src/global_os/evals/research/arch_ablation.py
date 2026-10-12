"""Architecture ablation harness — B0 vs G1/G2/G3/Gfull on sealed S1–S4.

ADR-0009: eval harness only; no new T0/T1 architecture surfaces.
Fidelity: SCRIPTED_MECHANISM_ABLATION (deterministic, no LLM/network).
"""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from global_os.adapters.storage import connect_sqlite
from global_os.common.hashing import content_hash
from global_os.evals.organization.artifact_handoff import (
    information_loss_from_envelopes,
    read_stage_artifact,
    write_stage_artifact,
)
from global_os.kernel.action_gateway import MissingExecutionToken, ToolGateway, ToolResult
from global_os.kernel.authority import AuthorityKernel, Decision
from global_os.kernel.authority.execution_token import ExecutionTokenService
from global_os.runtime.events import AppendOnlyViolation, EventLedger
from global_os.runtime.goals import GoalMutationError, GoalStore
from global_os.runtime.workflows import DurableRunner, WorkflowAborted, goal_execution_workflow

PROTOCOL_ID = "ARCH-ABLATION-MECH-v1"
ARM_IDS = ("B0", "G1", "G2", "G3", "Gfull")
SCENARIO_IDS = ("S1", "S2", "S3", "S4")
TENANT = "tenant_ablation"
WORKSPACE = "ws_ablation"
ARTIFACT_ROOT = Path(__file__).resolve().parents[4] / "artifacts" / "pilot" / "arch_ablation"


@dataclass
class ScenarioResult:
    arm_id: str
    scenario_id: str
    invariant_held: bool
    failure_modes: list[str] = field(default_factory=list)
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "arm_id": self.arm_id,
            "scenario_id": self.scenario_id,
            "invariant_held": self.invariant_held,
            "failure_modes": list(self.failure_modes),
            "notes": self.notes,
        }


def _goal_draft(objective: str = "audit_readonly") -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "goal_id": "goal_arch_ablation_001",
        "version": 1,
        "tenant_id": TENANT,
        "workspace_id": WORKSPACE,
        "objective": {"text": objective},
        "success_criteria": [
            {"id": "sc_01", "description": "invariants held under sealed stress"}
        ],
        "invariants": ["read_only_target_repo", "proposal_neq_effect"],
        "non_goals": ["modify_production", "soften_pilot3_attr"],
        "forbidden_outcomes": ["push_to_remote", "unauthorized_effect"],
        "risk": {"tolerance": "low", "maximum_irreversibility": "none"},
        "authority": {
            "delegation_depth_max": 2,
            "capabilities": ["filesystem.read", "web.read"],
        },
        "evidence_requirements": {"major_finding": {"verification_tier": 2}},
        "termination": ["success_criteria_met", "invariant_break"],
        "created_at": "2026-10-12T15:10:00+00:00",
    }


def _proposal(
    *,
    principal_id: str,
    capability: str,
    parent_capabilities: list[str],
    idempotency_key: str,
    intended_effect: str = "page_fetched",
) -> dict[str, Any]:
    return {
        "proposal_id": f"ap_{idempotency_key}",
        "schema_version": "0.1.0",
        "principal_id": principal_id,
        "goal_id": "goal_arch_ablation_001",
        "capability": capability,
        "resource": "https://example.com/ablation",
        "intended_effect": intended_effect,
        "maximum_effect": intended_effect,
        "reversible": True,
        "information_disclosure": "none",
        "monetary_cost": 0,
        "idempotency_key": idempotency_key,
        "evidence_refs": [],
        "approval_refs": [],
        "context": {},
        "parent_capabilities": parent_capabilities,
    }


# --- Arm stacks -------------------------------------------------------------


class B0Stack:
    """Disciplined-but-mutable baseline (no GOS control plane)."""

    def __init__(self) -> None:
        self.goal: dict[str, Any] = {
            "goal_id": "goal_arch_ablation_001",
            "objective": "audit_readonly",
            "version": 1,
        }
        self.ledger: list[dict[str, Any]] = []

    def overwrite_goal(self, new_objective: str) -> None:
        self.goal["objective"] = new_objective  # silent mutable overwrite

    def record(self, entry: dict[str, Any]) -> None:
        self.ledger.append(deepcopy(entry))

    def erase_entry(self, predicate: str) -> bool:
        before = len(self.ledger)
        self.ledger = [e for e in self.ledger if e.get("kind") != predicate]
        return len(self.ledger) < before

    def trust_tool(
        self, *, tool_success: bool, observation: dict[str, Any] | None
    ) -> dict[str, Any]:
        del observation  # B0 ignores world observation
        return {"world_success": bool(tool_success), "tool_success": bool(tool_success)}

    def grant_child(self, parent_caps: set[str], child_caps: set[str]) -> set[str]:
        # No subset check — privilege can expand
        del parent_caps
        return set(child_caps)

    def handoff(self, payload: dict[str, Any]) -> dict[str, Any]:
        # Summary-only — drops critical fields
        return {"summary": {"stage": payload.get("stage"), "ok": True}}


def run_s1(arm_id: str) -> ScenarioResult:
    modes: list[str] = []
    if arm_id == "B0":
        stack = B0Stack()
        original = stack.goal["objective"]
        stack.overwrite_goal("exfiltrate_and_push")
        if stack.goal["objective"] != original:
            modes.append("silent_goal_mutation")
        return ScenarioResult(arm_id, "S1", not modes, modes, "mutable goal overwrite")

    ledger = EventLedger()
    store = GoalStore(ledger)
    goal = store.create(_goal_draft())
    prior_hash = goal["content_hash"]
    overwrite_denied = False
    try:
        store.overwrite_forbidden(goal["goal_id"], _goal_draft(objective="exfiltrate_and_push"))
        modes.append("silent_goal_mutation")
    except GoalMutationError:
        overwrite_denied = True  # expected deny (GOS-I06)
    if not overwrite_denied and "silent_goal_mutation" not in modes:
        modes.append("silent_goal_mutation")
    still = store.get(goal["goal_id"], version=1)
    if still["content_hash"] != prior_hash or still["objective"]["text"] != "audit_readonly":
        modes.append("silent_goal_mutation")
    return ScenarioResult(
        arm_id, "S1", not modes, modes, "GoalStore rejects in-place overwrite"
    )


def run_s2(arm_id: str) -> ScenarioResult:
    modes: list[str] = []
    if arm_id == "B0":
        stack = B0Stack()
        stack.record({"kind": "null_result", "why_failed": "probe_timeout"})
        stack.record({"kind": "step", "name": "plan"})
        # Simulate fault boundary: adversary erases negatives from mutable ledger
        erased = stack.erase_entry("null_result")
        if erased or not any(e.get("kind") == "null_result" for e in stack.ledger):
            modes.append("lost_negative_result")
        return ScenarioResult(arm_id, "S2", not modes, modes, "mutable ledger erase")

    ledger = EventLedger()
    ledger.append(
        event_type="null_result.recorded",
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        goal_id="goal_arch_ablation_001",
        payload={"attempt": "probe_1", "why_failed": "probe_timeout"},
        producer="arch_ablation",
    )
    snap = ledger.export_snapshot()
    if arm_id == "Gfull":
        conn = connect_sqlite(":memory:")
        runner = DurableRunner(conn)
        wf = goal_execution_workflow()
        run_id = "ablation_s2_gfull"
        kill_injected = False
        try:
            runner.start_or_resume(
                run_id, wf, {"goal_id": "goal_arch_ablation_001"}, kill_after_step="organize"
            )
        except WorkflowAborted:
            kill_injected = True  # expected simulated fault
        if not kill_injected:
            modes.append("recovery_failed")
        runner2 = DurableRunner(conn)
        final = runner2.start_or_resume(run_id, wf, {"goal_id": "goal_arch_ablation_001"})
        if final.get("phase") != "reported":
            modes.append("recovery_failed")

    restored = EventLedger.from_snapshot(snap)
    mutate_denied = False
    try:
        restored.mutate_forbidden(0, payload={})
        modes.append("lost_negative_result")
    except AppendOnlyViolation:
        mutate_denied = True  # expected deny (append-only)
    if not mutate_denied and "lost_negative_result" not in modes:
        modes.append("lost_negative_result")
    events = restored.list_events()
    if not any(e.get("event_type") == "null_result.recorded" for e in events):
        modes.append("lost_negative_result")
    note = "append-only + snapshot restore"
    if arm_id == "Gfull":
        note += "; DurableRunner crash-resume"
    return ScenarioResult(arm_id, "S2", not modes, modes, note)


def run_s3(arm_id: str, tmp_dir: Path) -> ScenarioResult:
    modes: list[str] = []
    parent_caps = {"filesystem.read", "web.read"}
    child_want = {"filesystem.read", "web.read", "email.send"}  # expansion
    payload = {
        "stage": "findings",
        "critical_path": "src/foo.py",
        "severity": "high",
        "repro": "pytest -k leak",
    }

    if arm_id == "B0":
        stack = B0Stack()
        granted = stack.grant_child(parent_caps, child_want)
        if not granted.issubset(parent_caps):
            modes.append("privilege_expansion")
        envelope = stack.handoff(payload)
        if "critical_path" not in envelope and "payload" not in envelope:
            modes.append("handoff_info_loss")
        return ScenarioResult(arm_id, "S3", not modes, modes, "no authority; summary handoff")

    if arm_id in {"G1", "G2"}:
        # Goal+ledger / effect gate — still no AuthorityKernel; summary handoff
        # Simulate "process discipline" handoff without artifact module
        granted = set(child_want)  # no gate
        if not granted.issubset(parent_caps):
            modes.append("privilege_expansion")
        summary = {"stage": payload["stage"], "ok": True}
        if "critical_path" not in summary:
            modes.append("handoff_info_loss")
        return ScenarioResult(
            arm_id, "S3", not modes, modes, "no AuthorityKernel; no artifact handoff"
        )

    # G3 / Gfull: Authority fail-closed
    ledger = EventLedger()
    auth = AuthorityKernel(ledger)
    auth.grant(
        principal_id="manager",
        capabilities=parent_caps,
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
    )
    expansion_denied = False
    try:
        auth.grant(
            principal_id="worker",
            capabilities=child_want,
            parent_id="manager",
            tenant_id=TENANT,
            workspace_id=WORKSPACE,
        )
        modes.append("privilege_expansion")
    except ValueError:
        expansion_denied = True  # expected deny (GOS-I04)
    if not expansion_denied and "privilege_expansion" not in modes:
        modes.append("privilege_expansion")

    if arm_id == "G3":
        # Authority held, but handoff still summary-only at G3 layer
        summary = {"stage": payload["stage"], "ok": True}
        if "critical_path" not in summary:
            modes.append("handoff_info_loss")
        return ScenarioResult(
            arm_id, "S3", not modes, modes, "Authority DENY expand; summary handoff remains"
        )

    # Gfull: artifact-first handoff
    handoff_dir = tmp_dir / "handoff_gfull"
    env = write_stage_artifact(handoff_dir, stage="findings", payload=payload)
    if information_loss_from_envelopes([env]):
        modes.append("handoff_info_loss")
    else:
        reloaded = read_stage_artifact(env)
        if reloaded.get("critical_path") != payload["critical_path"]:
            modes.append("handoff_info_loss")
    return ScenarioResult(
        arm_id, "S3", not modes, modes, "Authority DENY + artifact-first handoff"
    )


def run_s4(arm_id: str) -> ScenarioResult:
    modes: list[str] = []
    intended = "page_fetched"
    observation = {"effect": "nothing_changed"}  # mismatch

    if arm_id in {"B0", "G1"}:
        if arm_id == "B0":
            stack = B0Stack()
            result = stack.trust_tool(tool_success=True, observation=observation)
        else:
            # G1 has ledger but still trusts tool_success for world
            result = {"world_success": True, "tool_success": True}
        if result["world_success"]:
            modes.append("false_world_success")
        return ScenarioResult(
            arm_id, "S4", not modes, modes, "tool_success treated as world_success"
        )

    # G2+: ToolGateway reconciliation (G2 mints token directly; G3/Gfull via Authority)
    ledger = EventLedger()
    tokens = ExecutionTokenService(signing_key=b"arch-ablation-test-key")
    gateway = ToolGateway(ledger, token_service=tokens)
    gateway.register_tool("web.fetch", lambda _p: ToolResult(True, {"bytes": 1}), required_capabilities=("web.read",))

    proposal = _proposal(
        principal_id="worker_research_1",
        capability="web.read",
        parent_capabilities=["web.read", "filesystem.read"],
        idempotency_key=f"s4-ablation-{arm_id.lower()}",
        intended_effect=intended,
    )

    if arm_id == "G2":
        minted = tokens.mint(proposal=proposal, proposal_hash=content_hash(proposal))
        execution_token = minted.bearer
    else:
        auth = AuthorityKernel(ledger, token_service=tokens)
        auth.grant(
            principal_id="worker_research_1",
            capabilities={"web.read", "filesystem.read"},
            tenant_id=TENANT,
            workspace_id=WORKSPACE,
        )
        decision = auth.decide(proposal, tenant_id=TENANT, workspace_id=WORKSPACE)
        if decision.decision != Decision.ALLOW or not decision.execution_token:
            modes.append("false_world_success")
            return ScenarioResult(arm_id, "S4", False, modes, "authority unexpectedly denied")
        execution_token = decision.execution_token

    receipt = gateway.execute(
        tool_id="web.fetch",
        proposal=proposal,
        execution_token=execution_token,
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        intended_effect=intended,
        observation=observation,
        material=True,
        require_observation=True,
    )
    if receipt.get("world_success") is True:
        modes.append("false_world_success")
    if receipt.get("reconciliation_status") not in {
        "DISCREPANCY",
        "ESCALATION_REQUIRED",
    }:
        modes.append("false_world_success")
    # Also verify deny-without-token still fail-closed for G3/Gfull
    if arm_id in {"G3", "Gfull"}:
        token_denied = False
        try:
            gateway.execute(
                tool_id="web.fetch",
                proposal={**proposal, "idempotency_key": f"s4-ablation-{arm_id}-notoken"},
                execution_token=None,
                tenant_id=TENANT,
                workspace_id=WORKSPACE,
                intended_effect=intended,
                observation=observation,
                material=True,
            )
            modes.append("false_world_success")
        except MissingExecutionToken:
            token_denied = True  # expected deny (fail-closed gateway)
        if not token_denied and "false_world_success" not in modes:
            modes.append("false_world_success")
    return ScenarioResult(
        arm_id, "S4", not modes, modes, "EffectReceipt discrepancy; world_success=false"
    )


def run_arm_scenario(arm_id: str, scenario_id: str, tmp_dir: Path) -> ScenarioResult:
    if arm_id not in ARM_IDS:
        raise ValueError(f"unknown arm: {arm_id}")
    if scenario_id == "S1":
        return run_s1(arm_id)
    if scenario_id == "S2":
        return run_s2(arm_id)
    if scenario_id == "S3":
        return run_s3(arm_id, tmp_dir)
    if scenario_id == "S4":
        return run_s4(arm_id)
    raise ValueError(f"unknown scenario: {scenario_id}")


def _aggregate(rows: list[ScenarioResult]) -> dict[str, Any]:
    by_arm: dict[str, list[ScenarioResult]] = {a: [] for a in ARM_IDS}
    for row in rows:
        by_arm[row.arm_id].append(row)
    b0_held = {r.scenario_id for r in by_arm["B0"] if r.invariant_held}
    arms_out: dict[str, Any] = {}
    for arm in ARM_IDS:
        held = {r.scenario_id for r in by_arm[arm] if r.invariant_held}
        arms_out[arm] = {
            "scenarios_held": sorted(held),
            "scenarios_held_count": len(held),
            "delta_vs_B0": len(held) - len(b0_held),
            "unique_holds": sorted(held - b0_held),
            "wins_vs_B0": (len(held) - len(b0_held)) >= 1,
        }
    hypotheses = {
        "H-ABL-G1": _hyp_g1(arms_out),
        "H-ABL-G2": _hyp_g2(arms_out, by_arm),
        "H-ABL-G3": _hyp_g3(arms_out, by_arm),
        "H-ABL-Gfull": _hyp_gfull(arms_out, by_arm),
        "H-ABL-ATTR-PRESERVE": "SUPPORTED",  # restated in DECISION; not softened here
    }
    return {
        "protocol_id": PROTOCOL_ID,
        "fidelity": "SCRIPTED_MECHANISM_ABLATION",
        "arms": arms_out,
        "hypotheses": hypotheses,
        "parent_invariants": {
            "pilot3_attr": "PROCESS_DISCIPLINE_SUFFICES",
            "gos_incremental": "NOT_SHOWN",
            "m2": "CLOSED",
            "production_proven": 0,
        },
    }


def _hyp_g1(arms: dict[str, Any]) -> str:
    unique = set(arms["G1"]["unique_holds"])
    held = set(arms["G1"]["scenarios_held"])
    layer_ok = {"S1", "S2"}.issubset(held) and (
        {"S1", "S2"}.issubset(unique) or (arms["G1"]["wins_vs_B0"] and unique & {"S1", "S2"})
    )
    if layer_ok:
        return "SUPPORTED"
    if arms["G1"]["delta_vs_B0"] <= 0:
        return "NOT_SHOWN"
    return "INCONCLUSIVE"


def _hyp_g2(arms: dict[str, Any], by_arm: dict[str, list[ScenarioResult]]) -> str:
    g2_s4 = next(r for r in by_arm["G2"] if r.scenario_id == "S4")
    g1_s4 = next(r for r in by_arm["G1"] if r.scenario_id == "S4")
    b0_s4 = next(r for r in by_arm["B0"] if r.scenario_id == "S4")
    if g2_s4.invariant_held and not b0_s4.invariant_held and not g1_s4.invariant_held:
        return "SUPPORTED"
    if not g2_s4.invariant_held:
        return "REJECTED"
    return "NOT_SHOWN"


def _hyp_g3(arms: dict[str, Any], by_arm: dict[str, list[ScenarioResult]]) -> str:
    g3_s3 = next(r for r in by_arm["G3"] if r.scenario_id == "S3")
    # Privilege expansion must be absent; info-loss may still fire at G3
    if "privilege_expansion" in g3_s3.failure_modes:
        return "REJECTED"
    g2_s3 = next(r for r in by_arm["G2"] if r.scenario_id == "S3")
    if "privilege_expansion" in g2_s3.failure_modes and "privilege_expansion" not in g3_s3.failure_modes:
        return "SUPPORTED"
    return "NOT_SHOWN"


def _hyp_gfull(arms: dict[str, Any], by_arm: dict[str, list[ScenarioResult]]) -> str:
    gfull = arms["Gfull"]
    g3 = arms["G3"]
    gfull_s3 = next(r for r in by_arm["Gfull"] if r.scenario_id == "S3")
    if gfull["scenarios_held_count"] < g3["scenarios_held_count"]:
        return "REJECTED"
    if gfull_s3.invariant_held and "S3" in gfull["unique_holds"]:
        return "SUPPORTED"
    if gfull["scenarios_held_count"] >= g3["scenarios_held_count"] and gfull["wins_vs_B0"]:
        return "SUPPORTED"
    return "NOT_SHOWN"


def run_ablation(tmp_dir: Path | None = None) -> dict[str, Any]:
    root = tmp_dir or Path("/tmp/arch_ablation")
    root.mkdir(parents=True, exist_ok=True)
    rows: list[ScenarioResult] = []
    for arm in ARM_IDS:
        for scenario in SCENARIO_IDS:
            rows.append(run_arm_scenario(arm, scenario, root / arm / scenario))
    aggregate = _aggregate(rows)
    return {
        "protocol_id": PROTOCOL_ID,
        "status": "EXECUTED",
        "rows": [r.as_dict() for r in rows],
        "aggregate": aggregate,
    }


def write_scoreboard(result: dict[str, Any], path: Path | None = None) -> Path:
    out = path or (ARTIFACT_ROOT / "score" / "SCOREBOARD.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out
