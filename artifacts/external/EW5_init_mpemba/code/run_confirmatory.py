"""M-EXT5 confirmatory runner — loads sealed holdout and executes pairs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config import Config
from experiment import (
    make_synthetic_data,
    result_to_dict,
    run_pair,
    sha256_file,
    train_reference,
    write_json,
)
from stats_rules import decide_effect, decide_fisher, one_sided_binom_p

CONFIRMATORY_SEED_PAIR_BASE = 1000


def build_seal_pairs(n: int = 20, entropy: int = 0xE501_BEEF) -> list[dict]:
    """Deterministic sealed pair list (public algorithm; values sealed in JSON)."""
    import numpy as np

    rng = np.random.default_rng(entropy)
    pairs = []
    for i in range(n):
        pairs.append(
            {
                "seed_pair": CONFIRMATORY_SEED_PAIR_BASE + i,
                "seed_batch": int(rng.integers(10_000, 50_000)),
            }
        )
    return pairs


def run_confirmatory(
    cfg: Config,
    seal_path: Path,
    out_path: Path,
    device: str = "cpu",
) -> dict:
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    pairs = seal["pairs"]
    train_ds, _ = make_synthetic_data(cfg)
    ref = train_reference(cfg, train_ds, device)
    results = []
    for p in pairs:
        r = run_pair(cfg, train_ds, ref, int(p["seed_pair"]), int(p["seed_batch"]), device=device)
        results.append(result_to_dict(r))
        print(
            f"conf pair={p['seed_pair']} valid={r.valid_ordering} "
            f"tauH={r.tau_hot} tauC={r.tau_cold} win={r.hot_wins}"
        )
    valid = [r for r in results if r["valid_ordering"]]
    wins_late = [r for r in valid if r["hot_wins_late"] is True]
    wins_early = [r for r in valid if r["hot_wins_early"] is True]
    gn_hot_gt = [r for r in valid if r["early_gradnorm_hot"] > r["early_gradnorm_cold"]]
    n_valid = len(valid)
    n_wins_late = len(wins_late)
    n_wins_early = len(wins_early)
    # Primary H_EFFECT = LATE target (final-regime aligned)
    effect = decide_effect(n_wins_late, n_valid)
    effect_early = decide_effect(n_wins_early, n_valid)  # secondary prereg endpoint
    fisher = decide_fisher(effect, len(gn_hot_gt), n_valid)
    summary = {
        "status": "COMPLETED",
        "phase": "CONFIRMATORY",
        "seal_path": str(seal_path),
        "seal_sha256": sha256_file(seal_path),
        "n_pairs": len(results),
        "n_valid": n_valid,
        "n_wins_late": n_wins_late,
        "n_wins_early": n_wins_early,
        "n_gradnorm_hot_gt_cold": len(gn_hot_gt),
        "binom_p_effect_late": one_sided_binom_p(n_wins_late, n_valid) if n_valid else None,
        "binom_p_effect_early": one_sided_binom_p(n_wins_early, n_valid) if n_valid else None,
        "H_EFFECT": effect,
        "H_EFFECT_EARLY_SECONDARY": effect_early,
        "H_FISHER": fisher,
        "primary_endpoint": "loss_target_late",
        "config": cfg.to_dict(),
        "results": results,
    }
    write_json(out_path, summary)
    print(
        f"Confirmatory saved {out_path}: H_EFFECT(late)={effect} "
        f"EARLY_SECONDARY={effect_early} H_FISHER={fisher}"
    )
    return summary


def main() -> int:
    cfg = Config()
    exam = ROOT.parent.parent / "M_EXT5_INIT_MPEMBA_EXAM"
    seal_path = exam / "SEALED_HOLDOUT.json"
    out = ROOT.parent / "results" / "confirmatory_results.json"
    if not seal_path.is_file():
        print(f"ERROR: missing seal {seal_path}", file=sys.stderr)
        return 2
    run_confirmatory(cfg, seal_path, out, device="cpu")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
