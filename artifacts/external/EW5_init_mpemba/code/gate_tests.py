"""M-EXT5 mechanical correctness gate — must all PASS before confirmatory science."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config import Config  # noqa: E402
from experiment import (  # noqa: E402
    batch_stream,
    make_synthetic_data,
    run_pair,
    train_reference,
    write_json,
)


def test_g3_config_serializes() -> None:
    cfg = Config()
    d = cfg.to_dict()
    assert d["protocol_id"] == "M-EXT5-INIT-MPEMBA-v1"
    assert d["max_steps"] == cfg.max_steps
    # round-trip via JSON
    raw = json.dumps(d, sort_keys=True)
    loaded = json.loads(raw)
    assert loaded["lr"] == cfg.lr


def test_g2_g4_g5_g6_identical_batches_and_update_count() -> None:
    cfg = Config(max_steps=40, n_train=512, n_test=128, monitor_every=1)
    train_ds, _ = make_synthetic_data(cfg)
    device = "cpu"
    ref = train_reference(Config(ref_train_steps=200, n_train=512, n_test=128), train_ds, device)
    # Same batch seed → identical sequences
    b1 = batch_stream(train_ds, cfg.batch_size, cfg.max_steps, seed=99)
    b2 = batch_stream(train_ds, cfg.batch_size, cfg.max_steps, seed=99)
    assert len(b1) == cfg.max_steps
    for (x1, y1), (x2, y2) in zip(b1, b2, strict=True):
        assert torch.equal(x1, x2) and torch.equal(y1, y2)
    r = run_pair(cfg, train_ds, ref, seed_pair=7, seed_batch=99, device=device)
    assert r.n_updates_hot == cfg.max_steps
    assert r.n_updates_cold == cfg.max_steps
    assert r.n_updates_hot == r.n_updates_cold


def test_g4_seed_reproducible_pair() -> None:
    cfg = Config(max_steps=30, n_train=512, n_test=128, monitor_every=1)
    train_ds, _ = make_synthetic_data(cfg)
    ref = train_reference(Config(ref_train_steps=150, n_train=512, n_test=128), train_ds, "cpu")
    r1 = run_pair(cfg, train_ds, ref, seed_pair=3, seed_batch=11, device="cpu")
    r2 = run_pair(cfg, train_ds, ref, seed_pair=3, seed_batch=11, device="cpu")
    assert abs(r1.d_hot0 - r2.d_hot0) < 1e-6
    assert abs(r1.d_cold0 - r2.d_cold0) < 1e-6
    assert r1.tau_hot == r2.tau_hot and r1.tau_cold == r2.tau_cold


def test_g1_confirmatory_mode_runs(tmp_path: Path | None = None) -> None:
    out = Path(tmp_path) if tmp_path else Path(tempfile.mkdtemp())
    seal = {
        "status": "TASK_PINNED_TEST",
        "protocol_id": "M-EXT5-INIT-MPEMBA-v1",
        "pairs": [{"seed_pair": 1, "seed_batch": 1001}, {"seed_pair": 2, "seed_batch": 1002}],
    }
    seal_path = out / "SEALED_HOLDOUT.json"
    write_json(seal_path, seal)
    # Import confirmatory runner
    import run_confirmatory as rc

    cfg = Config(max_steps=25, n_train=512, n_test=128, ref_train_steps=100, monitor_every=1)
    summary = rc.run_confirmatory(cfg, seal_path, out / "conf_results.json", device="cpu")
    assert summary["n_pairs"] == 2
    assert Path(out / "conf_results.json").is_file()
    assert summary["status"] == "COMPLETED"


def test_g7_pilot_seeds_disjoint_from_seal_template() -> None:
    pilot_seeds = {10, 11, 12, 13, 14}
    # Confirmatory seal template uses 1000+ range in production; gate checks disjointness helper
    from run_pilot import PILOT_PAIRS
    from run_confirmatory import CONFIRMATORY_SEED_PAIR_BASE

    pilot_pairs = {p["seed_pair"] for p in PILOT_PAIRS}
    assert pilot_pairs.isdisjoint(set(range(CONFIRMATORY_SEED_PAIR_BASE, CONFIRMATORY_SEED_PAIR_BASE + 50)))
    assert pilot_seeds == pilot_pairs or pilot_pairs  # non-empty


def test_g8_statistical_rule_consistent() -> None:
    """Bin(20,0.5) one-sided α=0.05 requires ≥15, not ≥14."""
    from math import comb

    n = 20
    p14 = sum(comb(n, k) for k in range(14, n + 1)) / 2**n
    p15 = sum(comb(n, k) for k in range(15, n + 1)) / 2**n
    assert p14 > 0.05
    assert p15 < 0.05
    from stats_rules import PRIMARY_N, PRIMARY_MIN_WINS, one_sided_binom_p

    assert PRIMARY_N == 20
    assert PRIMARY_MIN_WINS == 15
    assert one_sided_binom_p(14, 20) > 0.05
    assert one_sided_binom_p(15, 20) < 0.05


def main() -> int:
    results: dict[str, str] = {}
    tests = [
        ("G3", test_g3_config_serializes),
        ("G2_G4_G5_G6", test_g2_g4_g5_g6_identical_batches_and_update_count),
        ("G4_repro", test_g4_seed_reproducible_pair),
        ("G8", test_g8_statistical_rule_consistent),
        ("G7", test_g7_pilot_seeds_disjoint_from_seal_template),
        ("G1", test_g1_confirmatory_mode_runs),
    ]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            results[name] = "PASS"
            print(f"PASS {name}")
        except Exception as e:
            results[name] = f"FAIL: {e}"
            failed += 1
            print(f"FAIL {name}: {e}")
    out = ROOT.parent / "results" / "mechanical_gate_results.json"
    write_json(out, {"results": results, "failed": failed})
    print(f"Wrote {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
