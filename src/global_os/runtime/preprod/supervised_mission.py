"""Supervised mission path: Goal → Mission → Gateway observe → Achiever → Delivery.

PREPROD_SUPERVISED: one operator, one active mission, read-only sandbox tools by default.
World effects only via ToolGateway; Achiever remains control-plane (world_effects=False).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from global_os.adapters.storage.sql import connect_sqlite
from global_os.cognition.organization import MissionAssigner, OrganizationCompiler
from global_os.cognition.organs.achiever_loop import AchieverLoopError, run_achiever_organ_loop
from global_os.common.hashing import new_id
from global_os.kernel.action_gateway import ToolGateway, ToolResult, trusted_observation
from global_os.kernel.authority import AuthorityKernel
from global_os.kernel.authority.durable_gate import SqliteDurableGateStore
from global_os.runtime.events import EventLedger
from global_os.runtime.goals import GoalStore
from global_os.runtime.workflows.durable import (
    DurableRunner,
    WorkflowAborted,
    WorkflowDefinition,
    WorkflowStep,
)
from global_os.world.artifacts import ArtifactStore
from global_os.world.tools import run_repo_audit

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


def _criterion_entries(goal: dict[str, Any]) -> list[tuple[str, str]]:
    """Return (criterion_id, description) pairs from the Goal Contract."""
    entries: list[tuple[str, str]] = []
    for c in goal.get("success_criteria") or []:
        if isinstance(c, str):
            entries.append((c, c))
            continue
        cid = str(c.get("id") or c.get("description") or "")
        desc = str(c.get("description") or c.get("id") or "")
        if cid:
            entries.append((cid, desc))
    return entries


# Semantic markers only — never trust bare criterion ids (e.g. sc_01 alone).
# Description markers this verifier can honestly support (substring, lowercased).
_REPO_AUDIT_DESC_MARKERS = (
    "engineering report",
    "audit report",
    "repo audit",
    "verified engineering report",
)
# If present, criterion is out of scope for repo.audit even when id looks familiar.
_REPO_AUDIT_EXCLUDE_MARKERS = (
    "integration test",
    "интеграционн",
    "tests passed",
    "тесты прошли",
    "e2e passed",
    "pytest",
)


def criteria_supported_by_repo_audit(goal: dict[str, Any]) -> list[str]:
    """Criteria this verifier can independently evidence — by description semantics.

    Never bind solely because ``id == sc_01``. Unrelated criteria (e.g. integration
    tests passed) stay unbound → UNKNOWN at Completion Gate.
    """
    supported: list[str] = []
    for cid, desc in _criterion_entries(goal):
        lowered = desc.lower()
        if any(marker in lowered for marker in _REPO_AUDIT_EXCLUDE_MARKERS):
            continue
        if any(marker in lowered for marker in _REPO_AUDIT_DESC_MARKERS):
            supported.append(cid)
    return supported


def verify_repo_audit_report(report: Any) -> dict[str, Any]:
    """Deterministic independent check of a repo-audit artifact (read-only pilot)."""
    if not isinstance(report, dict):
        return {"ok": False, "reason": "report_not_object"}
    if report.get("modified_target") is not False:
        return {"ok": False, "reason": "modified_target_not_false"}
    if report.get("read_only") is not True:
        return {"ok": False, "reason": "read_only_not_true"}
    findings = report.get("findings")
    if not isinstance(findings, list) or len(findings) < 1:
        return {"ok": False, "reason": "empty_or_missing_findings"}
    if not isinstance(report.get("scan"), dict):
        return {"ok": False, "reason": "missing_scan"}
    return {"ok": True, "reason": "deterministic_structure_ok", "finding_count": len(findings)}


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


def _gateway_observe_step(state: dict[str, Any]) -> dict[str, Any]:
    run_dir = Path(state["run_dir"])
    _require_control(run_dir)
    goal = state["goal"]
    hooks = dict(state.get("hooks") or {})
    ledger = EventLedger.from_snapshot(state.get("events") or [])
    budget = dict(state.get("budget") or {})
    def _as_float(value: Any, default: float) -> float:
        if value is None:
            return default
        return float(value)

    tool_cost = _as_float(hooks.get("tool_cost_usd"), 0.01)
    remaining = _as_float(
        budget.get("remaining_usd", budget.get("usd")),
        0.0,
    )

    # Pre-tool budget gate (fail closed — no SUCCESS via skipped evidence).
    if remaining < tool_cost:
        state = {
            **state,
            "effect_receipts": [],
            "artifact_digest": None,
            "budget": budget,
            "tool_calls": state.get("tool_calls") or {"repo.audit": 0},
            "phase": "observed",
            "observe_block": "budget_insufficient",
            "artifact_verify": {"ok": False, "reason": "budget_insufficient"},
        }
        _write_json(_state_path(run_dir), {k: v for k, v in state.items() if k != "events"})
        return state

    target = Path(state["target_path"])
    call_count_path = run_dir / "tool_calls.json"
    prior = _read_json(call_count_path) if call_count_path.exists() else {"repo.audit": 0}

    # 1) Produce audit first (or inject corrupt / empty body for negative tests).
    if hooks.get("inject_corrupt_report"):
        report: dict[str, Any] = {"findings": [], "modified_target": True}
    elif hooks.get("inject_empty_report"):
        report = {"findings": [], "read_only": True, "modified_target": False, "scan": {}}
    else:
        report = run_repo_audit(target)

    # 2) Independent deterministic verification BEFORE success attestation.
    artifact_verify = verify_repo_audit_report(report)
    art = ArtifactStore(run_dir / "artifacts")
    digest = art.put_json(
        {
            "kind": "repo_audit_report",
            "run_id": state["run_id"],
            "goal_id": goal["goal_id"],
            "report": report,
            "artifact_verify": artifact_verify,
            "produced_at": _now(),
        }
    ).digest

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

        def handler(_payload: dict[str, Any]) -> ToolResult:
            prior["repo.audit"] = int(prior.get("repo.audit", 0)) + 1
            _write_json(call_count_path, prior)
            if hooks.get("inject_tool_failure"):
                return ToolResult(False, {"error": "injected_tool_failure", "report": report})
            return ToolResult(True, report)

        gateway.register_tool(
            "repo.audit",
            handler,
            required_capabilities=("filesystem.read",),
        )

        idem = f"preprod-{state['run_id']}-repo-audit"
        proposal = {
            "proposal_id": f"ap_{state['run_id']}_audit",
            "schema_version": "0.1.0",
            "principal_id": principal,
            "goal_id": goal["goal_id"],
            "capability": "filesystem.read",
            "resource": str(target),
            "intended_effect": "repo_audit_report",
            "maximum_effect": "repo_audit_report",
            "reversible": True,
            "information_disclosure": "none",
            "monetary_cost": tool_cost,
            "idempotency_key": idem,
            "evidence_refs": [],
            "approval_refs": [],
            "context": {"profile": PROFILE},
            "parent_capabilities": sorted(caps),
        }
        decision = auth.decide(
            proposal, tenant_id=goal["tenant_id"], workspace_id=goal["workspace_id"]
        )
        if decision.execution_token is None:
            raise SupervisedMissionError(f"authority denied observe: {decision.decision}")

        # 3) Attest success only after independent verify; else force DISCREPANCY
        # or leave observation pending — never pre-sign SUCCESS for unverified work.
        observation = None
        if (
            artifact_verify.get("ok")
            and not hooks.get("inject_tool_failure")
            and not hooks.get("inject_discrepancy_observation")
        ):
            observation = trusted_observation("repo_audit_report")
        elif hooks.get("inject_discrepancy_observation") or not artifact_verify.get("ok"):
            observation = trusted_observation("repo_audit_failed")

        receipt = gateway.execute(
            tool_id="repo.audit",
            proposal=proposal,
            execution_token=decision.execution_token,
            tenant_id=goal["tenant_id"],
            workspace_id=goal["workspace_id"],
            intended_effect="repo_audit_report",
            observation=observation,
        )

        # Bind only criteria this verifier supports — never all Goal criteria by default.
        supported = criteria_supported_by_repo_audit(goal)
        override = hooks.get("binds_criteria_override")
        if override is not None:
            # Test hook may only narrow the supported set, never expand it.
            bind_ids = [cid for cid in list(override) if cid in supported]
        else:
            bind_ids = list(supported)
        enriched = {
            **receipt,
            "binds_criteria": bind_ids,
            "success_criteria_ids": bind_ids,
            "artifact_verify": artifact_verify,
            "verifier": "repo_audit",
            "criteria_supported": supported,
        }
        # Only claim criterion support when verify + reconciliation both pass.
        if not (
            artifact_verify.get("ok")
            and enriched.get("world_success") is True
            and enriched.get("reconciliation_status") == "RECONCILED"
        ):
            # Explicit negative map so Completion Gate cannot treat blank as True.
            enriched["criterion_results"] = {cid: False for cid in bind_ids}

        spent = float(budget.get("spent_usd", 0.0)) + tool_cost
        budget["spent_usd"] = spent
        budget["remaining_usd"] = float(budget.get("usd", 0.0)) - spent

        state = {
            **state,
            "events": ledger.export_snapshot(),
            "effect_receipts": [enriched],
            "artifact_digest": digest,
            "artifact_verify": artifact_verify,
            "budget": budget,
            "tool_calls": prior,
            "phase": "observed",
            "observe_block": None,
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
    try:
        result = run_achiever_organ_loop(
            goal,
            attempt_fn=_build_attempt_fn(receipts=receipts),
            attempt_budget=1,
            ledger=ledger,
        )
    except AchieverLoopError as exc:
        raise SupervisedMissionError(str(exc)) from exc

    state = {
        **state,
        "events": ledger.export_snapshot(),
        "achiever": result.to_dict(),
        "completion": result.completion.to_dict(),
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
        "tool_calls": state.get("tool_calls"),
        "limits": {
            "external_write": "human_confirmation_required",
            "hmac_action_binding_residual": "NOT_CLAIMED_SOLVED",
            "challenge_ga": "NOT_STARTED",
        },
        "evidence": {
            "effect_receipt_ids": [
                r.get("receipt_id") for r in (state.get("effect_receipts") or [])
            ],
            "events_path": str(run_dir / "events.json"),
            "artifact_digest": state.get("artifact_digest"),
        },
        "history_summary": (state.get("achiever") or {}).get("events") or [],
        "delivered_at": _now(),
        "honesty": {
            "production_proven": 0,
            "continual_si": "NOT_MEASURED",
            "end_to_end_os_speedup": "NOT_CLAIMED",
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
    if phase == "observed":
        return "achiever_settle → deliver"
    if phase == "settled":
        return "deliver"
    return "gateway_observe → verification → delivery"
