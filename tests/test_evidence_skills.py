"""Evidence-backed skill library + transfer eval."""

from __future__ import annotations

import pytest

from global_os.cognition.skills.evidence_library import EvidenceSkill, EvidenceSkillLibrary
from global_os.evals.mission_learning.transfer_eval import run_transfer_trial


def test_register_starts_experimental_cannot_self_promote() -> None:
    lib = EvidenceSkillLibrary()
    with pytest.raises(ValueError):
        lib.register(
            EvidenceSkill(
                skill_id="sk1",
                title="t",
                instructions="do x",
                applies_to_task_types=("repair",),
                required_capabilities=("fs_read",),
                provenance={"source": "mll_v0"},
                status="PROMOTED_BY_HUMAN",
            )
        )
    sk = lib.register(
        EvidenceSkill(
            skill_id="sk1",
            title="t",
            instructions="do x",
            applies_to_task_types=("repair",),
            required_capabilities=("fs_read",),
            provenance={"source": "mll_v0"},
        )
    )
    assert sk.status == "EXPERIMENTAL"


def test_seven_of_ten_not_enough_to_promote() -> None:
    lib = EvidenceSkillLibrary()
    lib.register(
        EvidenceSkill(
            skill_id="sk2",
            title="t",
            instructions="do x",
            applies_to_task_types=("repair",),
            required_capabilities=("fs_read",),
            provenance={"source": "mll_v0"},
        )
    )
    lib.record_eval(
        "sk2",
        suite_id="transfer_a",
        success_rate=0.7,
        n_trials=10,
        cost_tokens=1000,
        disjoint_from_train=True,
        positive=True,
    )
    with pytest.raises(ValueError, match="too small"):
        lib.promote_by_human("sk2", approver="human")


def test_transfer_trial_rejects_train_overlap() -> None:
    tasks = ["t1", "t2", "t3", "t4", "t5"]
    res = run_transfer_trial(
        suite_id="suite_x",
        task_ids=tasks,
        baseline_runner=lambda tid, b: True,
        candidate_runner=lambda tid, b: True,
        budget={"tokens": 100},
        train_task_ids={"t1"},
    )
    assert res.disjoint_from_train is False
    assert res.promote_allowed is False


def test_transfer_trial_advantage_on_disjoint() -> None:
    tasks = [f"h{i}" for i in range(5)]
    res = run_transfer_trial(
        suite_id="suite_y",
        task_ids=tasks,
        baseline_runner=lambda tid, b: False,
        candidate_runner=lambda tid, b: True,
        budget={"tokens": 100},
        train_task_ids={"train_only"},
    )
    assert res.candidate_advantage == 1.0
    assert res.promote_allowed is True
    assert res.budget_equal is True
