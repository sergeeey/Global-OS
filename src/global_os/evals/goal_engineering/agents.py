"""Deterministic behavioral agents modulated by tasking strategy.

Post-audit constraints:
- Agents operate on AgentView only — World.oracle access raises.
- Policies follow the tasking packet (steps / DoD), not hidden oracles.
- Still NOT live LLMs; results are mechanism demos, not causal GE proof.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from global_os.evals.goal_engineering.agent_view import AgentView
from global_os.evals.goal_engineering.strategies import TaskingPacket
from global_os.evals.goal_engineering.tasks import World


@dataclass
class EpisodeResult:
    strategy_id: str
    task_id: str
    domain: str
    claimed_success: bool
    claimed_blocked: bool
    final_artifacts: dict[str, Any]
    evidence_ledger: list[dict[str, Any]]
    steps: int
    token_cost: int
    wall_ms: int
    human_interventions: int
    trajectory: list[dict[str, Any]] = field(default_factory=list)


def _tick(view: AgentView, tokens: int = 40, ms: int = 25) -> None:
    view.state["steps"] += 1
    view.state["token_cost"] += tokens
    view.state["wall_ms"] += ms


def _budget_ok(view: AgentView) -> bool:
    return int(view.state["steps"]) < int(view.state["budget_steps"])


def _patch_inclusive_from_source(buggy: str) -> str:
    """Derive fix from visible source text only (bug comment / range)."""
    return buggy.replace("range(a, b)", "range(a, b + 1)").replace(
        "    # BUG: excludes b\n", ""
    )


def _run_unit_tests(files: dict[str, str]) -> bool:
    """Simulate tests/test_math.py using only file contents (no oracle)."""
    body = files.get("lib/math_utils.py", "")
    # Observable structural check matching the fixture tests' intent
    return "range(a, b + 1)" in body or "range(a, b+1)" in body


def run_episode(world: World, packet: TaskingPacket, seed: int) -> EpisodeResult:
    """Dispatch by domain × strategy using an oracle-isolating view."""
    view = AgentView(world)
    if view.domain == "coding":
        return _run_coding(view, packet, seed)
    if view.domain == "research":
        return _run_research(view, packet, seed)
    if view.domain == "multi_step":
        return _run_multi_step(view, packet, seed)
    raise ValueError(view.domain)


def _run_coding(view: AgentView, packet: TaskingPacket, seed: int) -> EpisodeResult:
    traj: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    files = view.state["files"]
    other_before = files["lib/other.py"]
    distract = (seed % 5) == 0

    _tick(view, 60, 30)
    traj.append({"op": "open", "path": "lib/math_utils.py"})
    candidate = _patch_inclusive_from_source(files["lib/math_utils.py"])

    if packet.strategy_id == "S_TRAD":
        if distract:
            files["lib/other.py"] = files["lib/other.py"] + "# touched\n"
            traj.append({"op": "edit", "path": "lib/other.py", "note": "distractor"})
            _tick(view, 50, 20)
        files["lib/math_utils.py"] = candidate
        traj.append({"op": "edit", "path": "lib/math_utils.py"})
        _tick(view, 80, 40)
        run_tests = (seed % 5) in (1, 2)
        if run_tests and _budget_ok(view):
            view.state["tests_run"] = True
            view.state["test_passed"] = _run_unit_tests(files)
            traj.append({"op": "run_tests", "passed": view.state["test_passed"]})
            _tick(view, 70, 50)
        return EpisodeResult(
            strategy_id=packet.strategy_id,
            task_id=view.task_id,
            domain=view.domain,
            claimed_success=True,
            claimed_blocked=False,
            final_artifacts={
                "files": dict(files),
                "tests_run": view.state["tests_run"],
                "test_passed": view.state["test_passed"],
                "other_unchanged": files["lib/other.py"] == other_before,
            },
            evidence_ledger=ledger,
            steps=view.state["steps"],
            token_cost=view.state["token_cost"],
            wall_ms=view.state["wall_ms"],
            human_interventions=view.state["human_interventions"],
            trajectory=traj,
        )

    if packet.strategy_id == "S_DETAIL":
        files["lib/math_utils.py"] = candidate
        traj.append({"op": "edit", "path": "lib/math_utils.py", "via": "step"})
        _tick(view, 80, 40)
        view.state["tests_run"] = True
        view.state["test_passed"] = _run_unit_tests(files)
        traj.append({"op": "run_tests", "passed": view.state["test_passed"], "via": "step"})
        _tick(view, 70, 50)
        ledger.append(
            {
                "criterion_id": "informal",
                "kind": "self_check",
                "value": "edit looks correct",
            }
        )
        return EpisodeResult(
            strategy_id=packet.strategy_id,
            task_id=view.task_id,
            domain=view.domain,
            claimed_success=True,  # step text: success if edit "looks correct"
            claimed_blocked=False,
            final_artifacts={
                "files": dict(files),
                "tests_run": True,
                "test_passed": view.state["test_passed"],
                "other_unchanged": files["lib/other.py"] == other_before,
            },
            evidence_ledger=ledger,
            steps=view.state["steps"],
            token_cost=view.state["token_cost"],
            wall_ms=view.state["wall_ms"],
            human_interventions=0,
            trajectory=traj,
        )

    if packet.strategy_id == "S_DETAIL_VERIFIED":
        files["lib/math_utils.py"] = candidate
        traj.append({"op": "edit", "path": "lib/math_utils.py", "via": "verified_step"})
        _tick(view, 80, 40)
        view.state["tests_run"] = True
        view.state["test_passed"] = _run_unit_tests(files)
        traj.append(
            {"op": "run_tests", "passed": view.state["test_passed"], "via": "verified_step"}
        )
        _tick(view, 70, 50)
        other_ok = files["lib/other.py"] == other_before
        ledger.append(
            {
                "criterion_id": "runbook_tests",
                "kind": "command_output",
                "value": "exit_0" if view.state["test_passed"] else "exit_1",
            }
        )
        ok = bool(view.state["test_passed"]) and other_ok
        return EpisodeResult(
            strategy_id=packet.strategy_id,
            task_id=view.task_id,
            domain=view.domain,
            claimed_success=ok,
            claimed_blocked=not ok,
            final_artifacts={
                "files": dict(files),
                "tests_run": True,
                "test_passed": view.state["test_passed"],
                "other_unchanged": other_ok,
            },
            evidence_ledger=ledger,
            steps=view.state["steps"],
            token_cost=view.state["token_cost"],
            wall_ms=view.state["wall_ms"],
            human_interventions=0,
            trajectory=traj,
        )

    # S_GE
    files["lib/math_utils.py"] = candidate
    traj.append({"op": "edit", "path": "lib/math_utils.py", "via": "dod"})
    _tick(view, 90, 45)
    view.state["tests_run"] = True
    view.state["test_passed"] = _run_unit_tests(files)
    traj.append({"op": "run_tests", "passed": view.state["test_passed"], "via": "dod"})
    _tick(view, 80, 55)
    other_ok = files["lib/other.py"] == other_before
    ledger.extend(
        [
            {
                "criterion_id": "sc_sum",
                "kind": "code_diff",
                "value": "range(a, b + 1)",
                "path": "lib/math_utils.py",
            },
            {
                "criterion_id": "sc_tests",
                "kind": "command_output",
                "value": "exit_0" if view.state["test_passed"] else "exit_1",
                "path": "tests/test_math.py",
            },
            {
                "criterion_id": "sc_scope",
                "kind": "file_hash",
                "value": hashlib.sha256(other_before.encode()).hexdigest()[:16],
                "unchanged": other_ok,
            },
        ]
    )
    required = {c["id"] for c in packet.definition_of_done}
    have = {e["criterion_id"] for e in ledger}
    # Claim from observable checks only — never oracle
    criteria_met = bool(view.state["test_passed"]) and other_ok
    complete = required <= have and criteria_met
    return EpisodeResult(
        strategy_id=packet.strategy_id,
        task_id=view.task_id,
        domain=view.domain,
        claimed_success=bool(complete),
        claimed_blocked=not complete,
        final_artifacts={
            "files": dict(files),
            "tests_run": view.state["tests_run"],
            "test_passed": view.state["test_passed"],
            "other_unchanged": other_ok,
        },
        evidence_ledger=ledger,
        steps=view.state["steps"],
        token_cost=view.state["token_cost"],
        wall_ms=view.state["wall_ms"],
        human_interventions=0,
        trajectory=traj,
    )


def _run_research(view: AgentView, packet: TaskingPacket, seed: int) -> EpisodeResult:
    traj: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    sources = {s["id"]: s for s in view.state["sources"] if "id" in s}
    retracted: set[str] = set()

    def read_source(sid: str) -> None:
        if not _budget_ok(view):
            return
        view.state["read"].append(sid)
        traj.append({"op": "read", "source": sid})
        _tick(view, 45, 20)
        s = sources[sid]
        if s.get("kind") == "retraction":
            retracted.add(str(s["retracts"]))
            traj.append({"op": "note_retraction", "retracts": s["retracts"]})
        else:
            subj, pred, val = s["claim"]
            if sid not in retracted:
                view.state["beliefs"][(subj, pred)] = {
                    "value": val,
                    "source": sid,
                    "reliable": s.get("reliable", False),
                }

    def apply_retractions() -> None:
        for k, v in list(view.state["beliefs"].items()):
            if v["source"] in retracted:
                del view.state["beliefs"][k]

    if packet.strategy_id == "S_TRAD":
        for sid in ["S1", "S2", "S3", "S4"]:
            read_source(sid)
        if (seed % 5) >= 3:
            read_source("S5")
            apply_retractions()
        report = {
            pred: view.state["beliefs"].get(("Alpha", pred), {}).get("value")
            for pred in ("status", "owner", "region")
        }
        cites = {
            pred: view.state["beliefs"].get(("Alpha", pred), {}).get("source")
            for pred in ("status", "owner", "region")
        }
        view.state["final_report"] = {"claims": report, "citations": cites}
        _tick(view, 50, 30)
        return EpisodeResult(
            strategy_id=packet.strategy_id,
            task_id=view.task_id,
            domain=view.domain,
            claimed_success=True,
            claimed_blocked=False,
            final_artifacts=view.state["final_report"],
            evidence_ledger=[],
            steps=view.state["steps"],
            token_cost=view.state["token_cost"],
            wall_ms=view.state["wall_ms"],
            human_interventions=0,
            trajectory=traj,
        )

    if packet.strategy_id == "S_DETAIL":
        for sid in ["S1", "S2", "S3", "S4"]:
            read_source(sid)
        detail_report: dict[str, Any] = {}
        detail_cites: dict[str, Any] = {}
        for sid in ["S1", "S2", "S3", "S4"]:
            s = sources[sid]
            if s.get("kind") == "retraction":
                continue
            _subj, pred, val = s["claim"]
            detail_report[pred] = val
            detail_cites[pred] = sid
        view.state["final_report"] = {"claims": detail_report, "citations": detail_cites}
        _tick(view, 50, 30)
        ledger.append(
            {"criterion_id": "informal", "kind": "steps_complete", "value": "S1-S4"}
        )
        return EpisodeResult(
            strategy_id=packet.strategy_id,
            task_id=view.task_id,
            domain=view.domain,
            claimed_success=True,
            claimed_blocked=False,
            final_artifacts=view.state["final_report"],
            evidence_ledger=ledger,
            steps=view.state["steps"],
            token_cost=view.state["token_cost"],
            wall_ms=view.state["wall_ms"],
            human_interventions=0,
            trajectory=traj,
        )

    if packet.strategy_id == "S_DETAIL_VERIFIED":
        for sid in ["S1", "S2", "S3", "S4", "S5"]:
            read_source(sid)
        apply_retractions()
        for k, v in list(view.state["beliefs"].items()):
            if not v.get("reliable", False) and k[1] == "status":
                del view.state["beliefs"][k]
        for sid in ["S1", "S2", "S4"]:
            s = sources[sid]
            subj, pred, val = s["claim"]
            view.state["beliefs"][(subj, pred)] = {
                "value": val,
                "source": sid,
                "reliable": True,
            }
        report = {
            pred: view.state["beliefs"][("Alpha", pred)]["value"]
            for pred in ("status", "owner", "region")
        }
        cites = {
            pred: view.state["beliefs"][("Alpha", pred)]["source"]
            for pred in ("status", "owner", "region")
        }
        view.state["final_report"] = {"claims": report, "citations": cites}
        cite_ok = all(cites.values()) and cites.get("status") != "S3"
        ledger.append(
            {
                "criterion_id": "runbook_citations",
                "kind": "citation",
                "value": cites,
                "non_retracted": cite_ok,
            }
        )
        _tick(view, 70, 40)
        return EpisodeResult(
            strategy_id=packet.strategy_id,
            task_id=view.task_id,
            domain=view.domain,
            claimed_success=bool(cite_ok),
            claimed_blocked=not cite_ok,
            final_artifacts=view.state["final_report"],
            evidence_ledger=ledger,
            steps=view.state["steps"],
            token_cost=view.state["token_cost"],
            wall_ms=view.state["wall_ms"],
            human_interventions=0,
            trajectory=traj,
        )

    # S_GE — follow DoD/evidence from packet; claim from observable ledger only
    for sid in ["S1", "S2", "S3", "S4", "S5"]:
        read_source(sid)
    apply_retractions()
    for k, v in list(view.state["beliefs"].items()):
        if not v.get("reliable", False) and k[1] == "status":
            del view.state["beliefs"][k]
    for sid in ["S1", "S2", "S4"]:
        s = sources[sid]
        subj, pred, val = s["claim"]
        view.state["beliefs"][(subj, pred)] = {
            "value": val,
            "source": sid,
            "reliable": True,
        }
    report = {
        pred: view.state["beliefs"][("Alpha", pred)]["value"]
        for pred in ("status", "owner", "region")
    }
    cites = {
        pred: view.state["beliefs"][("Alpha", pred)]["source"]
        for pred in ("status", "owner", "region")
    }
    view.state["final_report"] = {"claims": report, "citations": cites}
    for pred in ("status", "owner", "region"):
        ledger.append(
            {
                "criterion_id": f"sc_{pred}",
                "kind": "citation",
                "value": report[pred],
                "source": cites[pred],
            }
        )
    ledger.append(
        {
            "criterion_id": "sc_cite",
            "kind": "ledger",
            "value": "all_claims_cited",
            "citations": cites,
        }
    )
    _tick(view, 70, 40)
    required = {c["id"] for c in packet.definition_of_done}
    have = {e["criterion_id"] for e in ledger}
    cite_ok = all(cites.values()) and cites.get("status") not in retracted
    complete = required <= have and cite_ok
    return EpisodeResult(
        strategy_id=packet.strategy_id,
        task_id=view.task_id,
        domain=view.domain,
        claimed_success=bool(complete),
        claimed_blocked=not complete,
        final_artifacts=view.state["final_report"],
        evidence_ledger=ledger,
        steps=view.state["steps"],
        token_cost=view.state["token_cost"],
        wall_ms=view.state["wall_ms"],
        human_interventions=0,
        trajectory=traj,
    )


def _run_multi_step(view: AgentView, packet: TaskingPacket, seed: int) -> EpisodeResult:
    traj: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    phases: list[str] = []

    def gather() -> None:
        view.state["gathered"] = True
        view.state["phase"] = "gathered"
        phases.append("gather")
        traj.append({"op": "gather", "raw": view.state["raw_value"]})
        _tick(view, 40, 25)

    def transform() -> None:
        view.state["transformed"] = True
        view.state["phase"] = "transformed"
        view.state["expected_value"] = int(view.state["raw_value"]) * 2
        phases.append("transform")
        traj.append({"op": "transform", "value": view.state["expected_value"]})
        _tick(view, 40, 25)

    def verify() -> bool:
        ok = (
            view.state["gathered"]
            and view.state["transformed"]
            and int(view.state["expected_value"]) == int(view.state["raw_value"]) * 2
        )
        view.state["verified"] = ok
        view.state["verify_result"] = "pass" if ok else "fail"
        view.state["phase"] = "verified"
        phases.append("verify")
        traj.append({"op": "verify", "result": view.state["verify_result"]})
        _tick(view, 50, 30)
        return ok

    def publish(value: int) -> None:
        view.state["published"] = True
        view.state["publish_payload"] = value
        view.state["phase"] = "published"
        phases.append("publish")
        traj.append({"op": "publish", "value": value})
        _tick(view, 40, 25)

    if packet.strategy_id == "S_TRAD":
        gather()
        transform()
        if (seed % 2) == 0:
            verify()
        publish(int(view.state["expected_value"]))
        return EpisodeResult(
            strategy_id=packet.strategy_id,
            task_id=view.task_id,
            domain=view.domain,
            claimed_success=True,
            claimed_blocked=False,
            final_artifacts={
                "phases": phases,
                "publish_payload": view.state["publish_payload"],
                "verify_result": view.state["verify_result"],
            },
            evidence_ledger=[],
            steps=view.state["steps"],
            token_cost=view.state["token_cost"],
            wall_ms=view.state["wall_ms"],
            human_interventions=0,
            trajectory=traj,
        )

    if packet.strategy_id == "S_DETAIL":
        gather()
        transform()
        publish(int(view.state["expected_value"]))
        ledger.append(
            {"criterion_id": "informal", "kind": "steps_complete", "value": "1-3"}
        )
        return EpisodeResult(
            strategy_id=packet.strategy_id,
            task_id=view.task_id,
            domain=view.domain,
            claimed_success=True,
            claimed_blocked=False,
            final_artifacts={
                "phases": phases,
                "publish_payload": view.state["publish_payload"],
                "verify_result": view.state["verify_result"],
            },
            evidence_ledger=ledger,
            steps=view.state["steps"],
            token_cost=view.state["token_cost"],
            wall_ms=view.state["wall_ms"],
            human_interventions=0,
            trajectory=traj,
        )

    if packet.strategy_id == "S_DETAIL_VERIFIED":
        gather()
        transform()
        ok = verify()
        if ok:
            publish(int(view.state["expected_value"]))
        ledger.append(
            {
                "criterion_id": "runbook_verify",
                "kind": "verify_receipt",
                "value": view.state["verify_result"],
            }
        )
        complete = (
            phases == ["gather", "transform", "verify", "publish"]
            and view.state["verify_result"] == "pass"
        )
        return EpisodeResult(
            strategy_id=packet.strategy_id,
            task_id=view.task_id,
            domain=view.domain,
            claimed_success=bool(complete),
            claimed_blocked=not complete,
            final_artifacts={
                "phases": phases,
                "publish_payload": view.state["publish_payload"],
                "verify_result": view.state["verify_result"],
            },
            evidence_ledger=ledger,
            steps=view.state["steps"],
            token_cost=view.state["token_cost"],
            wall_ms=view.state["wall_ms"],
            human_interventions=0,
            trajectory=traj,
        )

    # S_GE
    gather()
    transform()
    ok = verify()
    if ok:
        publish(int(view.state["expected_value"]))
    ledger.extend(
        [
            {"criterion_id": "sc_order", "kind": "event_log", "value": list(phases)},
            {
                "criterion_id": "sc_verify",
                "kind": "verify_receipt",
                "value": view.state["verify_result"],
            },
        ]
    )
    if view.state["published"]:
        ledger.append(
            {
                "criterion_id": "sc_value",
                "kind": "publish_receipt",
                "value": view.state["publish_payload"],
            }
        )
    required = {c["id"] for c in packet.definition_of_done}
    have = {e["criterion_id"] for e in ledger}
    complete = (
        required <= have
        and phases == ["gather", "transform", "verify", "publish"]
        and view.state["verify_result"] == "pass"
        and view.state["publish_payload"] == view.state["expected_value"]
    )
    return EpisodeResult(
        strategy_id=packet.strategy_id,
        task_id=view.task_id,
        domain=view.domain,
        claimed_success=bool(complete),
        claimed_blocked=not complete,
        final_artifacts={
            "phases": phases,
            "publish_payload": view.state["publish_payload"],
            "verify_result": view.state["verify_result"],
        },
        evidence_ledger=ledger,
        steps=view.state["steps"],
        token_cost=view.state["token_cost"],
        wall_ms=view.state["wall_ms"],
        human_interventions=0,
        trajectory=traj,
    )
