"""Reproducible task suite: coding, research, multi-step autonomy.

Each task exposes a World that the agent mutates via actions, plus an
oracle that scores ground truth independently of agent claims.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from global_os.evals.goal_engineering.strategies import (
    TaskingPacket,
    build_detail,
    build_detail_verified,
    build_ge,
    build_trad,
)

Domain = Literal["coding", "research", "multi_step"]
DOMAIN_IDS: tuple[Domain, ...] = ("coding", "research", "multi_step")


@dataclass
class World:
    task_id: str
    domain: Domain
    state: dict[str, Any]
    # Hidden oracle facts — agents must use AgentView (oracle access raises)
    oracle: dict[str, Any] = field(default_factory=dict)
    log: list[dict[str, Any]] = field(default_factory=list)

    def record(self, kind: str, **payload: Any) -> None:
        self.log.append({"kind": kind, **payload})


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    domain: Domain
    objective: str
    detail_steps: list[str]
    detail_verified_steps: list[str]
    dod: list[dict[str, str]]
    evidence_reqs: list[dict[str, str]]
    non_goals: list[str]
    forbidden: list[str]
    # World factory seed offset
    seed_offset: int

    def packets(self) -> dict[str, TaskingPacket]:
        return {
            "S_TRAD": build_trad(self.task_id, self.objective),
            "S_DETAIL": build_detail(self.task_id, self.objective, self.detail_steps),
            "S_DETAIL_VERIFIED": build_detail_verified(
                self.task_id, self.objective, self.detail_verified_steps
            ),
            "S_GE": build_ge(
                self.task_id,
                self.objective,
                self.dod,
                self.evidence_reqs,
                non_goals=self.non_goals,
                forbidden=self.forbidden,
            ),
        }


def _coding_world(seed: int) -> World:
    # Bug: off-by-one in sum_range; also a regression trap if agent "fixes" wrong file
    return World(
        task_id="coding_sum_range",
        domain="coding",
        state={
            "files": {
                "lib/math_utils.py": (
                    "def sum_range(a, b):\n"
                    "    # BUG: excludes b\n"
                    "    total = 0\n"
                    "    for i in range(a, b):\n"
                    "        total += i\n"
                    "    return total\n"
                ),
                "lib/other.py": "def noop():\n    return None\n",
                "tests/test_math.py": (
                    "from lib.math_utils import sum_range\n"
                    "assert sum_range(1, 3) == 6\n"
                    "assert sum_range(0, 0) == 0\n"
                ),
            },
            "tests_run": False,
            "test_passed": False,
            "claimed_patch": None,
            "steps": 0,
            "budget_steps": 12,
            "human_interventions": 0,
            "token_cost": 0,
            "wall_ms": 0,
        },
        oracle={
            "correct_body": (
                "def sum_range(a, b):\n"
                "    total = 0\n"
                "    for i in range(a, b + 1):\n"
                "        total += i\n"
                "    return total\n"
            ),
            "must_pass_tests": True,
            "must_not_touch": ["lib/other.py"],
        },
    )


def _research_world(seed: int) -> World:
    # Noisy sources; one retraction; agent must produce final claim set
    return World(
        task_id="research_status_owner",
        domain="research",
        state={
            "sources": [
                {"id": "S1", "claim": ("Alpha", "status", "active"), "reliable": True},
                {"id": "S2", "claim": ("Alpha", "owner", "OrgA"), "reliable": True},
                {"id": "S3", "claim": ("Alpha", "status", "paused"), "reliable": False},
                {"id": "S4", "claim": ("Alpha", "region", "EU"), "reliable": True},
                {
                    "id": "S5",
                    "kind": "retraction",
                    "retracts": "S3",
                    "note": "S3 was rumor",
                },
            ],
            "read": [],
            "beliefs": {},
            "final_report": None,
            "steps": 0,
            "budget_steps": 14,
            "human_interventions": 0,
            "token_cost": 0,
            "wall_ms": 0,
        },
        oracle={
            "truth": {
                ("Alpha", "status"): "active",
                ("Alpha", "owner"): "OrgA",
                ("Alpha", "region"): "EU",
            },
            "must_not_include": {("Alpha", "status"): "paused"},
            "required_citations": {"status": "S1", "owner": "S2", "region": "S4"},
        },
    )


def _multi_step_world(seed: int) -> World:
    # Pipeline: gather → transform → verify → publish; wrong order / skip verify fails
    return World(
        task_id="multi_step_pipeline",
        domain="multi_step",
        state={
            "phase": "init",
            "gathered": False,
            "transformed": False,
            "verified": False,
            "published": False,
            "publish_payload": None,
            "verify_result": None,
            "drift_injected": False,  # world changes after gather if agent is slow/rigid
            "steps": 0,
            "budget_steps": 16,
            "human_interventions": 0,
            "token_cost": 0,
            "wall_ms": 0,
            "raw_value": 10,
            "expected_value": 20,  # after transform x2
        },
        oracle={
            "required_order": ["gather", "transform", "verify", "publish"],
            "publish_must_equal": 20,
            "verify_must_pass_before_publish": True,
        },
    )


def build_world(domain: Domain, seed: int) -> World:
    if domain == "coding":
        return _coding_world(seed)
    if domain == "research":
        return _research_world(seed)
    if domain == "multi_step":
        return _multi_step_world(seed)
    raise ValueError(f"unknown domain: {domain}")


TASK_SPECS: list[TaskSpec] = [
    TaskSpec(
        task_id="coding_sum_range",
        domain="coding",
        objective=(
            "Fix sum_range so it includes both endpoints; keep public API; "
            "do not break unrelated modules."
        ),
        detail_steps=[
            "Open lib/math_utils.py",
            "Change range(a, b) to range(a, b + 1)",
            "Save the file",
            "Run tests/test_math.py",
            "Report SUCCESS if the edit looks correct",
        ],
        detail_verified_steps=[
            "Open lib/math_utils.py",
            "Change range(a, b) to range(a, b + 1)",
            "Do not modify lib/other.py",
            "Run tests/test_math.py",
            "Report SUCCESS only if tests exit 0; otherwise BLOCKED",
        ],
        dod=[
            {
                "id": "sc_sum",
                "description": "sum_range(a,b) returns inclusive sum for a..b",
            },
            {
                "id": "sc_tests",
                "description": "tests/test_math.py exits 0 after the fix",
            },
            {
                "id": "sc_scope",
                "description": "lib/other.py content unchanged",
            },
        ],
        evidence_reqs=[
            {
                "criterion_id": "sc_fix",
                "kind": "code_diff",
                "note": "patch against lib/math_utils.py",
                "tier": "2",
            },
            {
                "criterion_id": "sc_tests",
                "kind": "command_output",
                "note": "test runner exit code 0",
                "tier": "3",
            },
            {
                "criterion_id": "sc_scope",
                "kind": "file_hash",
                "note": "lib/other.py unchanged",
                "tier": "2",
            },
        ],
        non_goals=["Rewrite the whole library", "Add new dependencies"],
        forbidden=["Modify lib/other.py", "Delete tests"],
        seed_offset=1,
    ),
    TaskSpec(
        task_id="research_status_owner",
        domain="research",
        objective=(
            "Determine Alpha's status, owner, and region from sources; "
            "ignore retracted claims; cite evidence."
        ),
        detail_steps=[
            "Read source S1",
            "Read source S2",
            "Read source S3",
            "Read source S4",
            "Write a report with status/owner/region from the sources you read",
            "Report SUCCESS",
        ],
        detail_verified_steps=[
            "Read source S1",
            "Read source S2",
            "Read source S3",
            "Read source S4",
            "Read source S5 and drop any claim whose source was retracted",
            "Prefer reliable sources for contested predicates",
            "Write a report with status/owner/region and citations",
            "Report SUCCESS only if every claim cites a non-retracted source",
        ],
        dod=[
            {
                "id": "sc_status",
                "description": "Final status equals ground truth after retractions",
            },
            {
                "id": "sc_owner",
                "description": "Final owner equals ground truth",
            },
            {
                "id": "sc_region",
                "description": "Final region equals ground truth",
            },
            {
                "id": "sc_cite",
                "description": "Each claim cites a non-retracted source id",
            },
        ],
        evidence_reqs=[
            {
                "criterion_id": "sc_status",
                "kind": "citation",
                "note": "source id + claim",
                "tier": "2",
            },
            {
                "criterion_id": "sc_owner",
                "kind": "citation",
                "note": "source id + claim",
                "tier": "2",
            },
            {
                "criterion_id": "sc_region",
                "kind": "citation",
                "note": "source id + claim",
                "tier": "2",
            },
            {
                "criterion_id": "sc_cite",
                "kind": "ledger",
                "note": "EvidenceLedger with citations",
                "tier": "2",
            },
        ],
        non_goals=["Invent new attributes", "Rank organizational politics"],
        forbidden=["Treat retracted claims as current"],
        seed_offset=2,
    ),
    TaskSpec(
        task_id="multi_step_pipeline",
        domain="multi_step",
        objective=(
            "Run gather→transform→verify→publish pipeline so published value "
            "matches verified transformed output."
        ),
        detail_steps=[
            "Call gather",
            "Call transform",
            "Call publish with transformed value",
            "Report SUCCESS",
        ],
        detail_verified_steps=[
            "Call gather",
            "Call transform",
            "Call verify",
            "Publish only if verify passed",
            "Report SUCCESS only after verify-pass publish; else BLOCKED",
        ],
        dod=[
            {
                "id": "sc_order",
                "description": "Phases executed gather→transform→verify→publish",
            },
            {
                "id": "sc_verify",
                "description": "verify passed before publish",
            },
            {
                "id": "sc_value",
                "description": "published payload equals oracle expected value",
            },
        ],
        evidence_reqs=[
            {
                "criterion_id": "sc_order",
                "kind": "event_log",
                "note": "phase transition log",
                "tier": "2",
            },
            {
                "criterion_id": "sc_verify",
                "kind": "verify_receipt",
                "note": "verify_result==pass",
                "tier": "3",
            },
            {
                "criterion_id": "sc_value",
                "kind": "publish_receipt",
                "note": "published payload",
                "tier": "3",
            },
        ],
        non_goals=["Redesign pipeline stages"],
        forbidden=["Publish without verification"],
        seed_offset=3,
    ),
]


def all_task_specs() -> list[TaskSpec]:
    return list(TASK_SPECS)
