"""Y19-H1 acceptance + adversarial tests (sealed holdout protocol)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from global_os.evals.research.y19_transient_early_warning import (
    HOLD_SEEDS,
    MCID_BRIER_RATIO,
    PROTOCOL_VERSION,
    TRAIN_SEEDS,
    run_experiment,
)

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "y19" / "Y19-H1-transient-early-warning"


def test_train_hold_disjoint_and_disjoint_from_y17_ranges():
    assert not (set(TRAIN_SEEDS) & set(HOLD_SEEDS))
    y17 = set(range(550, 565)) | set(range(650, 665))
    assert not (set(TRAIN_SEEDS) & y17)
    assert not (set(HOLD_SEEDS) & y17)


def test_honest_run_unknown_a_priori_and_valid_decision():
    raw = run_experiment()
    assert raw["answer_known_a_priori"] is False
    assert raw["protocol_version"] == PROTOCOL_VERSION
    assert raw["leak_checks"]["peek_holdout_labels_in_train"] is False
    assert raw["decision"] in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
    assert raw["mcid_brier_ratio"] == MCID_BRIER_RATIO
    assert raw["hold_positives"] + raw["hold_negatives"] == raw["hold_n"]


def test_decision_rule_matches_mcid_and_ablation():
    raw = run_experiment()
    ratio = raw["brier_ratio"]
    abl = raw["ablated_brier_ratio"]
    pos, neg = raw["hold_positives"], raw["hold_negatives"]
    if pos < 12 or neg < 12:
        assert raw["decision"] == "INCONCLUSIVE"
    elif ratio <= MCID_BRIER_RATIO and abl <= MCID_BRIER_RATIO:
        assert raw["decision"] == "SUPPORTED"
        assert raw["scientific_claim_accepted"] is True
    elif ratio <= MCID_BRIER_RATIO:
        assert raw["decision"] == "INCONCLUSIVE"
        assert raw["winning_hypothesis_id"] == "H_size_spurious"
    else:
        assert raw["decision"] == "REJECTED"
        assert raw["scientific_claim_accepted"] is False
        assert raw["null_results"], "REJECTED must preserve null"


def test_adversarial_leak_flag_recorded():
    raw = run_experiment(peek_holdout_labels_in_train=True)
    assert raw["leak_checks"]["peek_holdout_labels_in_train"] is True


def test_mission_script_pass():
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    proc = subprocess.run(
        [sys.executable, str(ART / "execute_mission.py")],
        cwd=str(ROOT),
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    mission = json.loads((ART / "mission.json").read_text(encoding="utf-8"))
    assert mission["decision"] in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
    ver = json.loads((ART / "verification.json").read_text(encoding="utf-8"))
    assert ver["deterministic_status"] == "PASS"
    metrics = json.loads((ART / "experiments" / "metrics" / "run.json").read_text(encoding="utf-8"))
    assert metrics["answer_known_a_priori"] is False


def test_h2_seeds_disjoint_from_h1():
    from global_os.evals.research.y19_transient_early_warning import (
        HOLD_SEEDS_H2,
        TRAIN_SEEDS_H2,
    )

    assert not (set(TRAIN_SEEDS_H2) & (set(TRAIN_SEEDS) | set(HOLD_SEEDS)))
    assert not (set(HOLD_SEEDS_H2) & (set(TRAIN_SEEDS) | set(HOLD_SEEDS)))


def test_h2_decision_rule():
    from global_os.evals.research.y19_transient_early_warning import run_experiment_h2

    raw = run_experiment_h2()
    assert raw["answer_known_a_priori"] is False
    assert raw["decision"] in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
    ratio = raw["brier_ratio_full_over_activity"]
    if raw["hold_positives"] < 12 or raw["hold_negatives"] < 12:
        assert raw["decision"] == "INCONCLUSIVE"
    elif ratio <= MCID_BRIER_RATIO:
        assert raw["decision"] == "SUPPORTED"
    else:
        assert raw["decision"] == "REJECTED"
        assert raw["null_results"]


def test_h2_mission_script():
    art = ROOT / "artifacts" / "y19" / "Y19-H2-baseline-mechanism"
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    proc = subprocess.run(
        [sys.executable, str(art / "execute_mission.py")],
        cwd=str(ROOT),
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    mission = json.loads((art / "mission.json").read_text(encoding="utf-8"))
    assert mission["decision"] in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}


def test_h3_seeds_disjoint():
    from global_os.evals.research.y19_transient_early_warning import (
        HOLD_SEEDS_H2,
        HOLD_SEEDS_H3_MATCH,
        HOLD_SEEDS_H3_UNSEEN,
        TRAIN_SEEDS_H2,
        TRAIN_SEEDS_H3,
    )

    prior = set(TRAIN_SEEDS) | set(HOLD_SEEDS) | set(TRAIN_SEEDS_H2) | set(HOLD_SEEDS_H2)
    assert not (set(TRAIN_SEEDS_H3) & prior)
    assert not (set(HOLD_SEEDS_H3_MATCH) & prior)
    assert not (set(HOLD_SEEDS_H3_UNSEEN) & prior)
    assert not (set(HOLD_SEEDS_H3_MATCH) & set(HOLD_SEEDS_H3_UNSEEN))


def test_h3_decision_matches_gates():
    from global_os.evals.research.y19_transient_early_warning import run_experiment_h3

    raw = run_experiment_h3()
    assert raw["answer_known_a_priori"] is False
    gates = raw["gates"]
    statuses = [gates[k]["status"] for k in ("A_activity_matched", "B_unseen_size", "C_regime_k")]
    if any(s == "FAIL" for s in statuses):
        assert raw["decision"] == "REJECTED"
        assert raw["null_results"]
    elif any(s == "UNDERPOWERED" for s in statuses):
        assert raw["decision"] == "INCONCLUSIVE"
    else:
        assert raw["decision"] == "SUPPORTED"
        assert all(gates[k]["passed"] for k in gates)


def test_h3_mission_script():
    art = ROOT / "artifacts" / "y19" / "Y19-H3-h2-robustness"
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    proc = subprocess.run(
        [sys.executable, str(art / "execute_mission.py")],
        cwd=str(ROOT),
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr[-2000:]
    mission = json.loads((art / "mission.json").read_text(encoding="utf-8"))
    assert mission["decision"] in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
    ver = json.loads((art / "verification.json").read_text(encoding="utf-8"))
    assert ver["deterministic_status"] == "PASS"


def test_h4_seeds_disjoint():
    from global_os.evals.research.y19_transient_early_warning import (
        HOLD_SEEDS_H2,
        HOLD_SEEDS_H3_MATCH,
        HOLD_SEEDS_H3_UNSEEN,
        HOLD_SEEDS_H4,
        TRAIN_SEEDS_H2,
        TRAIN_SEEDS_H3,
        TRAIN_SEEDS_H4,
    )

    prior = (
        set(TRAIN_SEEDS)
        | set(HOLD_SEEDS)
        | set(TRAIN_SEEDS_H2)
        | set(HOLD_SEEDS_H2)
        | set(TRAIN_SEEDS_H3)
        | set(HOLD_SEEDS_H3_MATCH)
        | set(HOLD_SEEDS_H3_UNSEEN)
    )
    assert not (set(TRAIN_SEEDS_H4) & prior)
    assert not (set(HOLD_SEEDS_H4) & prior)


def test_h4_decision_matches_gates():
    from global_os.evals.research.y19_transient_early_warning import run_experiment_h4

    raw = run_experiment_h4()
    assert raw["answer_known_a_priori"] is False
    gates = raw["gates"]
    assert set(gates) >= {"A_n_matched", "B_residualized_entropy", "C_leave_one_n_out"}
    statuses = [gates[k]["status"] for k in gates]
    if any(s == "FAIL" for s in statuses):
        assert raw["decision"] in {"REJECTED", "INCONCLUSIVE"}
    elif any(s == "UNDERPOWERED" for s in statuses):
        assert raw["decision"] == "INCONCLUSIVE"
    else:
        assert raw["decision"] == "SUPPORTED"


def test_h4_mission_script():
    art = ROOT / "artifacts" / "y19" / "Y19-H4-size-entropy-decomp"
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    proc = subprocess.run(
        [sys.executable, str(art / "execute_mission.py")],
        cwd=str(ROOT),
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr[-2000:]
    mission = json.loads((art / "mission.json").read_text(encoding="utf-8"))
    assert mission["decision"] in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
