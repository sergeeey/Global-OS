"""Supervised mission path: Goal → Brief → Gateway tools → Achiever → Delivery.

PREPROD_SUPERVISED: one operator, one active mission, read-only sandbox tools by default.
World effects only via ToolGateway; Achiever remains control-plane (world_effects=False).
Tool choice comes from Goal capabilities ∩ Execution Brief ∩ Operator tool catalog —
not from a hardcoded tool id in the observe step.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from global_os.adapters.models.base import GenerateRequest
from global_os.adapters.models.recording import RecordingModelProvider
from global_os.adapters.models.scripted_action import (
    ScriptedActionProvider,
    default_tool_script,
)
from global_os.adapters.storage.sql import connect_sqlite
from global_os.cognition.organization import MissionAssigner, OrganizationCompiler
from global_os.cognition.organs.achiever_loop import AchieverLoopError, run_achiever_organ_loop
from global_os.cognition.organs.task_compiler import TaskCompilerError, compile_execution_brief
from global_os.common.hashing import content_hash, new_id
from global_os.kernel.action_gateway import ToolGateway, ToolResult
from global_os.kernel.authority import AuthorityKernel
from global_os.kernel.authority.durable_gate import SqliteDurableGateStore
from global_os.runtime.events import EventLedger
from global_os.runtime.goals import GoalStore
from global_os.runtime.preprod.tool_catalog import (
    ToolCatalogError,
    assert_tool_permitted,
    criteria_supported_by_tool,
    criteria_supported_by_tools,
    produce_tool_artifact,
    resolve_allowed_tool_ids,
    verify_tool_artifact,
)
from global_os.runtime.workflows.durable import (
    DurableRunner,
    WorkflowAborted,
    WorkflowDefinition,
    WorkflowStep,
)
from global_os.world.artifacts import ArtifactStore

PROFILE = "PREPROD_SUPERVISED"
CONTROL_RUNNING = "RUNNING"
CONTROL_PAUSED = "PAUSED"
CONTROL_CANCELLED = "CANCELLED"


class SupervisedMissionError(Exception):
    pass


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _missions_root(gos_root: Path) -> Path:
    root = gos_root / "missions"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _run_dir(gos_root: Path, run_id: str) -> Path:
    path = _missions_root(gos_root) / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read_json(path: Path) -> dict[str, Any]:
    raw: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise SupervisedMissionError(f"expected JSON object at {path}")
    return raw


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _control_path(run_dir: Path) -> Path:
    return run_dir / "control.json"


def _state_path(run_dir: Path) -> Path:
    return run_dir / "state.json"


def _delivery_path(run_dir: Path) -> Path:
    return run_dir / "delivery.json"


def _index_path(gos_root: Path) -> Path:
    return _missions_root(gos_root) / "index.json"


def _load_index(gos_root: Path) -> dict[str, Any]:
    path = _index_path(gos_root)
    if not path.exists():
        return {"active_run_id": None, "runs": []}
    return _read_json(path)


def _save_index(gos_root: Path, index: dict[str, Any]) -> None:
    _write_json(_index_path(gos_root), index)


def _require_control(run_dir: Path, *, allow_paused: bool = False) -> dict[str, Any]:
    ctrl = _read_json(_control_path(run_dir))
    status = str(ctrl.get("status"))
    if status == CONTROL_CANCELLED:
        raise SupervisedMissionError("mission cancelled by operator")
    if status == CONTROL_PAUSED and not allow_paused:
        raise SupervisedMissionError("mission paused; use resume")
    return ctrl


def _persist_events(run_dir: Path, ledger: EventLedger) -> None:
    _write_json(run_dir / "events.json", {"events": ledger.list_events()})


def _criterion_ids(goal: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for c in goal.get("success_criteria") or []:
        if isinstance(c, str):
            out.append(c)
        else:
            out.append(str(c.get("id") or c.get("description") or c))
    return out


def criteria_supported_by_repo_audit(goal: dict[str, Any]) -> list[str]:
    """Backward-compatible helper — criteria supportable by ``repo.audit`` only."""
    return criteria_supported_by_tool(goal, "repo.audit")


def _build_attempt_fn(*, receipts: list[dict[str, Any]]) -> Any:
    def attempt_fn(
        _goal: dict[str, Any], _plan: dict[str, Any], _route: dict[str, Any]
    ) -> dict[str, Any]:
        # Achiever is control-only. Never blanket criterion_checks=True —
        # Completion Gate must derive met/unmet/unknown from receipts.
        return {
            "effect_receipts": receipts,
            "world_effects": False,
            "challenge_win_claimed": False,
        }

    return attempt_fn


def _brief_select_step(state: dict[str, Any]) -> dict[str, Any]:
    """Compile Execution Brief and resolve allowed Gateway tool IDs (fail-closed)."""
    run_dir = Path(state["run_dir"])
    _require_control(run_dir)
    goal = state["goal"]
    budget = dict(state.get("budget") or {})
    ledger = EventLedger.from_snapshot(state.get("events") or [])
    org_unit = {
        "id": str(state.get("org_unit_id") or "org_preprod"),
        "authority": {"capabilities": list(goal["authority"]["capabilities"])},
        "budget": {
            "usd": float(budget.get("usd", 0) or 0),
            "tokens": int(budget.get("tokens", 0) or 0),
        },
        "output_contract": "artifact_and_evidence",
    }
    plan = {
        "plan_id": f"plan_{state['run_id']}",
        "task_advances_criteria": {},
    }
    task = {"task_id": f"task_{state['run_id']}_observe", "title": "observe"}
    # Do not pre-bind all criteria — tool verifiers bind after evidence.
    try:
        brief = compile_execution_brief(
            goal=goal,
            plan=plan,
            task=task,
            org_unit=org_unit,
            ledger_tail=ledger.list_events(),
            material_reason="first_attempt",
            criterion_ids=[],
            force=True,
        )
    except TaskCompilerError as exc:
        raise SupervisedMissionError(f"brief_compile_failed:{exc}") from exc
    if brief is None:
        raise SupervisedMissionError("brief_compile_failed:none")

    goal_caps = list(goal["authority"]["capabilities"])
    brief_caps = list(brief.get("allowed_tools") or [])
    allowed_tool_ids = resolve_allowed_tool_ids(
        goal_capabilities=goal_caps,
        brief_allowed_capabilities=brief_caps,
    )
    # Optional test narrowing of tool set (never expands beyond resolved).
    hooks = dict(state.get("hooks") or {})
    override_tools = hooks.get("allowed_tool_ids_override")
    if override_tools is not None:
        allowed_tool_ids = [t for t in list(override_tools) if t in allowed_tool_ids]

    if not allowed_tool_ids:
        state = {
            **state,
            "events": ledger.export_snapshot(),
            "execution_brief": brief,
            "allowed_tool_ids": [],
            "phase": "briefed",
            "observe_block": "no_allowed_tools",
            "effect_receipts": [],
        }
        _persist_events(run_dir, ledger)
        _write_json(_state_path(run_dir), {k: v for k, v in state.items() if k != "events"})
        return state

    state = {
        **state,
        "events": ledger.export_snapshot(),
        "execution_brief": brief,
        "allowed_tool_ids": allowed_tool_ids,
        "phase": "briefed",
        "observe_block": None,
    }
    _persist_events(run_dir, ledger)
    _write_json(_state_path(run_dir), {k: v for k, v in state.items() if k != "events"})
    return state


def _gateway_observe_step(state: dict[str, Any]) -> dict[str, Any]:
    """Execute tools selected via mock action cycles through ToolGateway only."""
    run_dir = Path(state["run_dir"])
    _require_control(run_dir)
    goal = state["goal"]
    hooks = dict(state.get("hooks") or {})
    ledger = EventLedger.from_snapshot(state.get("events") or [])
    budget = dict(state.get("budget") or {})
    allowed_tool_ids = list(state.get("allowed_tool_ids") or [])

    def _as_float(value: Any, default: float) -> float:
        if value is None:
            return default
        return float(value)

    tool_cost = _as_float(hooks.get("tool_cost_usd"), 0.01)

    if state.get("observe_block") == "no_allowed_tools" or not allowed_tool_ids:
        state = {
            **state,
            "effect_receipts": [],
            "artifact_digest": None,
            "budget": budget,
            "tool_calls": state.get("tool_calls") or {},
            "phase": "observed",
            "observe_block": "no_allowed_tools",
            "artifact_verify": {"ok": False, "reason": "no_allowed_tools"},
            "model_cycles": 0,
        }
        _write_json(_state_path(run_dir), {k: v for k, v in state.items() if k != "events"})
        return state

    remaining = _as_float(budget.get("remaining_usd", budget.get("usd")), 0.0)
    if remaining < tool_cost:
        state = {
            **state,
            "effect_receipts": [],
            "artifact_digest": None,
            "budget": budget,
            "tool_calls": state.get("tool_calls") or {},
            "phase": "observed",
            "observe_block": "budget_insufficient",
            "artifact_verify": {"ok": False, "reason": "budget_insufficient"},
            "model_cycles": 0,
        }
        _write_json(_state_path(run_dir), {k: v for k, v in state.items() if k != "events"})
        return state

    target = Path(state["target_path"])
    call_count_path = run_dir / "tool_calls.json"
    last_report_path = run_dir / "last_tool_report.json"
    prior = _read_json(call_count_path) if call_count_path.exists() else {}

    # Prefer catalog tools whose verifiers can bind Goal success criteria.
    preferred = [
        tid for tid in allowed_tool_ids if criteria_supported_by_tool(goal, tid)
    ]
    script = hooks.get("model_script")
    if script is None:
        script = default_tool_script(
            allowed_tool_ids, preferred_tool_ids=preferred or None
        )
    # Adversarial: force an unknown/forbidden tool proposal.
    if hooks.get("inject_forbidden_tool_id"):
        script = [
            {
                "action": "call_tool",
                "tool_id": str(hooks["inject_forbidden_tool_id"]),
                "args": {},
            },
            {"action": "stop"},
        ]

    inner = ScriptedActionProvider(list(script))
    model = RecordingModelProvider(
        inner,
        ledger,
        tenant_id=str(goal["tenant_id"]),
        workspace_id=str(goal["workspace_id"]),
        goal_id=str(goal["goal_id"]),
        producer="preprod.scripted_action",
    )

    receipts: list[dict[str, Any]] = []
    last_digest: str | None = None
    last_verify: dict[str, Any] = {"ok": False, "reason": "no_tool_executed"}
    last_report_hash: str | None = None
    executed_tools: list[str] = []
    observe_block: str | None = None
    max_cycles = int(hooks.get("max_model_cycles") or 4)

    gate_path = run_dir / "durable_gate.sqlite"
    gate = SqliteDurableGateStore(gate_path)
    try:
        auth = AuthorityKernel(ledger)
        gateway = ToolGateway(ledger, gate_store=gate)
        principal = "operator_supervised_1"
        caps = set(goal["authority"]["capabilities"])
        auth.grant(
            principal_id=principal,
            capabilities=caps,
            tenant_id=goal["tenant_id"],
            workspace_id=goal["workspace_id"],
        )

        # Register catalog tools. Produce runs ONLY here — after Authority+Gateway.
        for tid in allowed_tool_ids:
            try:
                spec = assert_tool_permitted(tid, allowed_tool_ids=allowed_tool_ids)
            except ToolCatalogError as exc:
                raise SupervisedMissionError(str(exc)) from exc

            def _make_handler(tool_id: str) -> Any:
                def handler(_payload: dict[str, Any]) -> ToolResult:
                    report = produce_tool_artifact(tool_id, target, hooks)
                    prior[tool_id] = int(prior.get(tool_id, 0)) + 1
                    _write_json(call_count_path, prior)
                    _write_json(
                        last_report_path,
                        {
                            "tool_id": tool_id,
                            "report": report,
                            "report_hash": content_hash(report),
                            "produced_at": _now(),
                        },
                    )
                    if hooks.get("inject_tool_failure"):
                        return ToolResult(
                            False, {"error": "injected_tool_failure", "report": report}
                        )
                    return ToolResult(True, report)

                return handler

            gateway.register_tool(
                tid,
                _make_handler(tid),
                required_capabilities=spec.required_capabilities,
            )

        for _cycle in range(max_cycles):
            remaining = _as_float(budget.get("remaining_usd", budget.get("usd")), 0.0)
            if remaining < tool_cost:
                observe_block = "budget_insufficient"
                break

            decision_doc = model.structured_generate(
                GenerateRequest(
                    prompt=(
                        f"Select next Operator action for goal {goal['goal_id']}. "
                        f"allowed_tool_ids={allowed_tool_ids}. "
                        f"executed={executed_tools}."
                    ),
                    max_tokens=256,
                    metadata={"profile": PROFILE},
                ),
                schema={"title": "OperatorAction", "type": "object"},
            )
            action = str(decision_doc.get("action") or "")
            if action == "stop":
                break
            if action != "call_tool":
                observe_block = f"unknown_model_action:{action}"
                break

            tool_id = str(decision_doc.get("tool_id") or "")
            try:
                spec = assert_tool_permitted(tool_id, allowed_tool_ids=allowed_tool_ids)
            except ToolCatalogError as exc:
                observe_block = str(exc)
                break

            # Pilot tools take no model args — reject anything except {}.
            raw_args = decision_doc.get("args", {})
            if raw_args is None:
                raw_args = {}
            if not isinstance(raw_args, dict) or raw_args != {}:
                observe_block = "invalid_tool_args"
                break

            # Fail-closed before Gateway: no produce on deny paths.
            if hooks.get("deny_capability"):
                observe_block = "authority_capability_denied"
                break

            idem = f"preprod-{state['run_id']}-{tool_id.replace('.', '-')}"
            proposal = {
                "proposal_id": f"ap_{state['run_id']}_{tool_id.replace('.', '_')}",
                "schema_version": "0.1.0",
                "principal_id": principal,
                "goal_id": goal["goal_id"],
                "capability": spec.required_capabilities[0],
                "resource": str(target),
                "intended_effect": spec.intended_effect,
                "maximum_effect": spec.intended_effect,
                "reversible": True,
                "information_disclosure": "none",
                "monetary_cost": tool_cost,
                "idempotency_key": idem,
                "evidence_refs": [],
                "approval_refs": [],
                "context": {"profile": PROFILE, "tool_id": tool_id},
                "parent_capabilities": sorted(caps),
            }
            decision = auth.decide(
                proposal, tenant_id=goal["tenant_id"], workspace_id=goal["workspace_id"]
            )
            if decision.execution_token is None:
                observe_block = f"authority_denied:{decision.decision}"
                break

            # observation=None → Gateway leaves OBSERVATION_PENDING (no pre-attest).
            # Single produce happens inside the registered handler after token checks.
            receipt = gateway.execute(
                tool_id=tool_id,
                proposal=proposal,
                execution_token=decision.execution_token,
                tenant_id=goal["tenant_id"],
                workspace_id=goal["workspace_id"],
                intended_effect=spec.intended_effect,
                observation=None,
            )

            if not last_report_path.exists():
                observe_block = "missing_tool_report_after_gateway"
                break
            saved = _read_json(last_report_path)
            if str(saved.get("tool_id") or "") != tool_id:
                observe_block = "tool_report_mismatch"
                break
            report = saved.get("report")
            if not isinstance(report, dict):
                observe_block = "tool_report_not_object"
                break
            report_hash = str(saved.get("report_hash") or content_hash(report))
            artifact_verify = verify_tool_artifact(tool_id, report)
            art = ArtifactStore(run_dir / "artifacts")
            digest = art.put_json(
                {
                    "kind": spec.artifact_kind,
                    "tool_id": tool_id,
                    "run_id": state["run_id"],
                    "goal_id": goal["goal_id"],
                    "report": report,
                    "report_hash": report_hash,
                    "artifact_verify": artifact_verify,
                    "produced_at": _now(),
                }
            ).digest
            last_digest = digest
            last_verify = artifact_verify
            last_report_hash = report_hash

            supported = criteria_supported_by_tool(goal, tool_id)
            override = hooks.get("binds_criteria_override")
            if override is not None:
                bind_ids = [cid for cid in list(override) if cid in supported]
            else:
                bind_ids = list(supported)

            gateway_status = str(receipt.get("reconciliation_status") or "")
            tool_ok = (receipt.get("tool_response") or {}).get("success") is True
            enriched: dict[str, Any] = {
                **receipt,
                "binds_criteria": bind_ids,
                "success_criteria_ids": bind_ids,
                "artifact_verify": artifact_verify,
                "artifact_digest": digest,
                "report_hash": report_hash,
                "verifier": tool_id,
                "criteria_supported": supported,
                "tool_id": tool_id,
                "gateway_reconciliation_status": gateway_status,
            }
            # Post-execution attestation of the single Gateway produce — never pre-RECONCILED.
            if hooks.get("inject_discrepancy_observation"):
                enriched["reconciliation_status"] = "DISCREPANCY"
                enriched["world_success"] = False
                enriched["discrepancy"] = "injected_discrepancy_observation"
                enriched["verification_method"] = "post_execution_artifact_verify"
            elif tool_ok and artifact_verify.get("ok"):
                enriched["reconciliation_status"] = "RECONCILED"
                enriched["world_success"] = True
                enriched["observed_effect"] = spec.intended_effect
                enriched["discrepancy"] = "none"
                enriched["verification_method"] = "post_execution_artifact_verify"
            else:
                enriched["reconciliation_status"] = "DISCREPANCY"
                enriched["world_success"] = False
                enriched["verification_method"] = "post_execution_artifact_verify"
                if not artifact_verify.get("ok"):
                    enriched["discrepancy"] = (
                        f"artifact_verify:{artifact_verify.get('reason')}"
                    )
                elif not tool_ok:
                    enriched["discrepancy"] = "tool_response_not_success"

            if not (
                artifact_verify.get("ok")
                and enriched.get("world_success") is True
                and enriched.get("reconciliation_status") == "RECONCILED"
            ):
                enriched["criterion_results"] = {cid: False for cid in bind_ids}

            receipts.append(enriched)
            executed_tools.append(tool_id)
            spent = float(budget.get("spent_usd", 0.0)) + tool_cost
            budget["spent_usd"] = spent
            budget["remaining_usd"] = float(budget.get("usd", 0.0)) - spent

            # One successful tool is enough for pilot Goals; model cycle 2 issues stop.
            if artifact_verify.get("ok") and enriched.get("world_success") is True:
                continue

        state = {
            **state,
            "events": ledger.export_snapshot(),
            "effect_receipts": receipts,
            "artifact_digest": last_digest,
            "artifact_verify": last_verify,
            "report_hash": last_report_hash,
            "budget": budget,
            "tool_calls": prior,
            "executed_tools": executed_tools,
            "model_cycles": inner.cycles,
            "model_history": list(inner.history),
            "phase": "observed",
            "observe_block": observe_block,
        }
        _persist_events(run_dir, ledger)
        _write_json(_state_path(run_dir), {k: v for k, v in state.items() if k != "events"})
        return state
    finally:
        gate.close()


def _achiever_settle_step(state: dict[str, Any]) -> dict[str, Any]:
    run_dir = Path(state["run_dir"])
    _require_control(run_dir)
    goal = state["goal"]
    ledger = EventLedger.from_snapshot(state.get("events") or [])
    receipts = list(state.get("effect_receipts") or [])
    budget = dict(state.get("budget") or {})
    org_unit = {
        "id": str(state.get("org_unit_id") or "org_preprod"),
        "authority": {"capabilities": list(goal["authority"]["capabilities"])},
        "budget": {
            "usd": float(budget.get("usd", 0) or 0),
            "tokens": int(budget.get("tokens", 0) or 0),
        },
        "output_contract": "artifact_and_evidence",
    }
    executed = list(state.get("executed_tools") or [])
    supported = criteria_supported_by_tools(goal, executed)
    try:
        result = run_achiever_organ_loop(
            goal,
            attempt_fn=_build_attempt_fn(receipts=receipts),
            attempt_budget=1,
            ledger=ledger,
            org_unit=org_unit,
            routing_context={"brief_criterion_ids": supported},
        )
    except AchieverLoopError as exc:
        raise SupervisedMissionError(str(exc)) from exc

    # Prefer brief from brief_select; Achiever may emit another — keep first for delivery honesty
    last_brief = state.get("execution_brief") or result.to_dict().get("last_brief")
    state = {
        **state,
        "events": ledger.export_snapshot(),
        "achiever": result.to_dict(),
        "completion": result.completion.to_dict(),
        "last_brief": last_brief,
        "phase": "settled",
        "stop": result.stop,
    }
    _persist_events(run_dir, ledger)
    _write_json(_state_path(run_dir), {k: v for k, v in state.items() if k != "events"})
    return state


def _deliver_step(state: dict[str, Any]) -> dict[str, Any]:
    run_dir = Path(state["run_dir"])
    _require_control(run_dir)
    completion = state.get("completion") or {}
    status = str(completion.get("status") or "UNKNOWN")
    terminal = {
        "ACHIEVED": "SUCCEEDED",
        "PARTIAL": "PARTIAL",
        "FAILED": "FAILED",
        "UNKNOWN": "INCONCLUSIVE",
    }.get(status, "INCONCLUSIVE")
    delivery = {
        "schema_version": "0.1.0",
        "profile": PROFILE,
        "run_id": state["run_id"],
        "goal_id": state["goal"]["goal_id"],
        "mission_id": state.get("mission_id"),
        "terminal_status": terminal,
        "completion": completion,
        "achiever_stop": state.get("stop"),
        "budget": state.get("budget"),
        "artifact_digest": state.get("artifact_digest"),
        "report_hash": state.get("report_hash"),
        "tool_calls": state.get("tool_calls"),
        "allowed_tool_ids": state.get("allowed_tool_ids"),
        "executed_tools": state.get("executed_tools"),
        "model_cycles": state.get("model_cycles"),
        "observe_block": state.get("observe_block"),
        "limits": {
            "external_write": "human_confirmation_required",
            "hmac_action_binding_residual": "NOT_CLAIMED_SOLVED",
            "challenge_ga": "NOT_STARTED",
            "live_llm": "NOT_USED_MOCK_SCRIPTED_ONLY",
        },
        "evidence": {
            "effect_receipt_ids": [
                r.get("receipt_id") for r in (state.get("effect_receipts") or [])
            ],
            "effect_receipts": list(state.get("effect_receipts") or []),
            "events_path": str(run_dir / "events.json"),
            "artifact_digest": state.get("artifact_digest"),
            "report_hash": state.get("report_hash"),
        },
        "history_summary": (state.get("achiever") or {}).get("events") or [],
        "last_execution_brief": state.get("last_brief"),
        "delivered_at": _now(),
        "honesty": {
            "production_proven": 0,
            "continual_si": "NOT_MEASURED",
            "end_to_end_os_speedup": "NOT_CLAIMED",
            "execution_brief": "ephemeral_work_order_not_completion",
            "tool_selection": "brief_catalog_gateway_not_hardcoded",
        },
    }
    _write_json(_delivery_path(run_dir), delivery)
    ctrl = _read_json(_control_path(run_dir))
    ctrl["status"] = terminal
    ctrl["updated_at"] = _now()
    _write_json(_control_path(run_dir), ctrl)
    state = {**state, "delivery": delivery, "phase": "delivered"}
    _write_json(_state_path(run_dir), {k: v for k, v in state.items() if k != "events"})
    return state


def _workflow() -> WorkflowDefinition:
    return WorkflowDefinition(
        name="preprod_supervised_mission_v0",
        steps=[
            WorkflowStep("brief_select", _brief_select_step),
            WorkflowStep("gateway_observe", _gateway_observe_step),
            WorkflowStep("achiever_settle", _achiever_settle_step),
            WorkflowStep("deliver", _deliver_step),
        ],
    )


def start_mission(
    goal_draft: dict[str, Any],
    *,
    target_path: str | Path,
    gos_root: Path | None = None,
    budget_usd: float = 15.0,
    budget_tokens: int = 50_000,
    kill_after_step: str | None = None,
    run_id: str | None = None,
    hooks: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create Goal + Mission and run supervised workflow (or resume by run_id).

    ``hooks`` is for adversarial/acceptance tests only (inject failures). Production
    operators should leave it unset.
    """
    gos_root = gos_root or (Path.cwd() / ".gos")
    gos_root.mkdir(parents=True, exist_ok=True)
    index = _load_index(gos_root)
    if run_id is None and index.get("active_run_id"):
        active = str(index["active_run_id"])
        ctrl = _read_json(_control_path(_run_dir(gos_root, active)))
        if ctrl.get("status") == CONTROL_RUNNING:
            raise SupervisedMissionError(
                f"one active mission allowed ({active}); pause/cancel it first"
            )

    if run_id is None:
        run_id = new_id("run")
        run_dir = _run_dir(gos_root, run_id)
        ledger = EventLedger()
        goals = GoalStore(ledger)
        goal = goals.create(goal_draft)
        org = OrganizationCompiler(ledger).compile_manager_workers(
            goal,
            worker_missions=["observe", "verify", "deliver"],
            budget_usd=budget_usd,
            budget_tokens=budget_tokens,
        )
        worker = org["workers"][0]
        mission = MissionAssigner(ledger).assign(
            org_unit=worker,
            objective=str(
                goal["objective"].get("text")
                if isinstance(goal["objective"], dict)
                else goal["objective"]
            ),
            success_criteria=_criterion_ids(goal),
            evidence_required=["effect_receipt", "artifact_digest"],
            constraints=list(goal.get("invariants") or []),
            tenant_id=goal["tenant_id"],
            workspace_id=goal["workspace_id"],
        )
        state: dict[str, Any] = {
            "profile": PROFILE,
            "run_id": run_id,
            "run_dir": str(run_dir),
            "target_path": str(Path(target_path).resolve()),
            "goal": goal,
            "mission_id": mission["id"],
            "org_unit_id": worker["id"],
            "budget": {
                "usd": budget_usd,
                "tokens": budget_tokens,
                "spent_usd": 0.0,
                "remaining_usd": budget_usd,
            },
            "hooks": dict(hooks or {}),
            "events": ledger.export_snapshot(),
            "phase": "started",
            "started_at": _now(),
        }
        _write_json(
            _control_path(run_dir),
            {
                "status": CONTROL_RUNNING,
                "profile": PROFILE,
                "run_id": run_id,
                "goal_id": goal["goal_id"],
                "updated_at": _now(),
            },
        )
        _write_json(_state_path(run_dir), {k: v for k, v in state.items() if k != "events"})
        _persist_events(run_dir, ledger)
        index["active_run_id"] = run_id
        runs = list(index.get("runs") or [])
        runs.append({"run_id": run_id, "goal_id": goal["goal_id"], "started_at": state["started_at"]})
        index["runs"] = runs
        _save_index(gos_root, index)
    else:
        run_dir = _run_dir(gos_root, run_id)
        if not _state_path(run_dir).exists():
            raise SupervisedMissionError(f"unknown run_id: {run_id}")
        ctrl = _require_control(run_dir, allow_paused=True)
        if ctrl.get("status") == CONTROL_PAUSED:
            ctrl["status"] = CONTROL_RUNNING
            ctrl["updated_at"] = _now()
            _write_json(_control_path(run_dir), ctrl)
        state = _read_json(_state_path(run_dir))
        events_doc = _read_json(run_dir / "events.json")
        state["events"] = events_doc.get("events") or []
        state["run_dir"] = str(run_dir)

    # Durable gate is constructed with an on-disk path inside gateway_observe;
    # do not mutate process env (pollutes subsequent tests / soak harnesses).

    wf_conn = connect_sqlite(run_dir / "workflow.sqlite")
    try:
        runner = DurableRunner(wf_conn)
        try:
            final = runner.start_or_resume(
                run_id,
                _workflow(),
                state,
                kill_after_step=kill_after_step,
            )
        except WorkflowAborted:
            ctrl = _read_json(_control_path(run_dir))
            ctrl["status"] = CONTROL_PAUSED
            ctrl["updated_at"] = _now()
            ctrl["note"] = "interrupted; resume to continue"
            _write_json(_control_path(run_dir), ctrl)
            return status_mission(gos_root=gos_root, run_id=run_id)
        except SupervisedMissionError as exc:
            if "paused" in str(exc).lower():
                return status_mission(gos_root=gos_root, run_id=run_id)
            raise
    finally:
        wf_conn.close()

    index = _load_index(gos_root)
    if index.get("active_run_id") == run_id:
        index["active_run_id"] = None
        _save_index(gos_root, index)
    return deliver_mission(gos_root=gos_root, run_id=run_id) if _delivery_path(run_dir).exists() else final


def pause_mission(*, gos_root: Path | None = None, run_id: str | None = None) -> dict[str, Any]:
    gos_root = gos_root or (Path.cwd() / ".gos")
    run_id = run_id or str(_load_index(gos_root).get("active_run_id") or "")
    if not run_id:
        raise SupervisedMissionError("no active run_id")
    run_dir = _run_dir(gos_root, run_id)
    ctrl = _read_json(_control_path(run_dir))
    if ctrl.get("status") == CONTROL_CANCELLED:
        raise SupervisedMissionError("mission already cancelled")
    ctrl["status"] = CONTROL_PAUSED
    ctrl["updated_at"] = _now()
    _write_json(_control_path(run_dir), ctrl)
    return status_mission(gos_root=gos_root, run_id=run_id)


def resume_mission(*, gos_root: Path | None = None, run_id: str | None = None) -> dict[str, Any]:
    gos_root = gos_root or (Path.cwd() / ".gos")
    run_id = run_id or str(_load_index(gos_root).get("active_run_id") or "")
    if not run_id:
        raise SupervisedMissionError("no run_id to resume")
    return start_mission(
        {},  # unused on resume
        target_path=".",
        gos_root=gos_root,
        run_id=run_id,
    )


def cancel_mission(*, gos_root: Path | None = None, run_id: str | None = None) -> dict[str, Any]:
    gos_root = gos_root or (Path.cwd() / ".gos")
    run_id = run_id or str(_load_index(gos_root).get("active_run_id") or "")
    if not run_id:
        raise SupervisedMissionError("no run_id to cancel")
    run_dir = _run_dir(gos_root, run_id)
    ctrl = _read_json(_control_path(run_dir))
    ctrl["status"] = CONTROL_CANCELLED
    ctrl["updated_at"] = _now()
    _write_json(_control_path(run_dir), ctrl)
    index = _load_index(gos_root)
    if index.get("active_run_id") == run_id:
        index["active_run_id"] = None
        _save_index(gos_root, index)
    return status_mission(gos_root=gos_root, run_id=run_id)


def status_mission(*, gos_root: Path | None = None, run_id: str | None = None) -> dict[str, Any]:
    gos_root = gos_root or (Path.cwd() / ".gos")
    index = _load_index(gos_root)
    run_id = run_id or index.get("active_run_id") or (
        (index.get("runs") or [{}])[-1].get("run_id") if index.get("runs") else None
    )
    if not run_id:
        raise SupervisedMissionError("no missions found")
    run_dir = _run_dir(gos_root, str(run_id))
    ctrl = _read_json(_control_path(run_dir))
    state = _read_json(_state_path(run_dir)) if _state_path(run_dir).exists() else {}
    delivery = (
        _read_json(_delivery_path(run_dir)) if _delivery_path(run_dir).exists() else None
    )
    started = state.get("started_at")
    return {
        "profile": PROFILE,
        "run_id": run_id,
        "goal_id": ctrl.get("goal_id") or (state.get("goal") or {}).get("goal_id"),
        "status": ctrl.get("status"),
        "phase": state.get("phase"),
        "started_at": started,
        "budget": state.get("budget"),
        "human_action_required": ctrl.get("status")
        in {CONTROL_PAUSED, "PARTIAL", "BLOCKED", CONTROL_CANCELLED},
        "next": _next_hint(ctrl.get("status"), state.get("phase")),
        "delivery_available": delivery is not None,
        "completion": state.get("completion") or (delivery or {}).get("completion"),
        "control_updated_at": ctrl.get("updated_at"),
    }


def deliver_mission(*, gos_root: Path | None = None, run_id: str | None = None) -> dict[str, Any]:
    gos_root = gos_root or (Path.cwd() / ".gos")
    st = status_mission(gos_root=gos_root, run_id=run_id)
    run_id = str(st["run_id"])
    path = _delivery_path(_run_dir(gos_root, run_id))
    if not path.exists():
        raise SupervisedMissionError("delivery not ready; resume mission until deliver step")
    return _read_json(path)


def _next_hint(status: Any, phase: Any) -> str:
    if status == CONTROL_PAUSED:
        return "resume"
    if status == CONTROL_CANCELLED:
        return "none"
    if status in {"SUCCEEDED", "PARTIAL", "FAILED", "INCONCLUSIVE"}:
        return "deliver / review audit trail"
    if phase == "briefed":
        return "gateway_observe → achiever_settle → deliver"
    if phase == "observed":
        return "achiever_settle → deliver"
    if phase == "settled":
        return "deliver"
    return "brief_select → gateway_observe → verification → delivery"
