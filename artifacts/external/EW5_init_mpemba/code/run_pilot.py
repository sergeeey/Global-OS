"""M-EXT5 exploratory pilot — separate seeds; not confirmatory."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config import Config
from experiment import make_synthetic_data, result_to_dict, run_pair, train_reference, write_json

# Disjoint from confirmatory base (>=1000)
PILOT_PAIRS = [
    {"seed_pair": 10, "seed_batch": 510},
    {"seed_pair": 11, "seed_batch": 511},
    {"seed_pair": 12, "seed_batch": 512},
    {"seed_pair": 13, "seed_batch": 513},
    {"seed_pair": 14, "seed_batch": 514},
]


def run_pilot(cfg: Config | None = None, out_path: Path | None = None, device: str = "cpu") -> dict:
    cfg = cfg or Config()
    out_path = out_path or (ROOT.parent / "results" / "pilot_results.json")
    train_ds, _ = make_synthetic_data(cfg)
    ref = train_reference(cfg, train_ds, device)
    results = []
    for p in PILOT_PAIRS:
        r = run_pair(cfg, train_ds, ref, p["seed_pair"], p["seed_batch"], device=device)
        results.append(result_to_dict(r))
        print(
            f"pilot pair={p['seed_pair']} valid={r.valid_ordering} "
            f"dH={r.d_hot0:.3f} dC={r.d_cold0:.3f} tauH={r.tau_hot} tauC={r.tau_cold} win={r.hot_wins}"
        )
    valid = [r for r in results if r["valid_ordering"]]
    wins_late = [r for r in valid if r.get("hot_wins_late") is True]
    wins_early = [r for r in valid if r.get("hot_wins_early") is True]
    summary = {
        "phase": "PILOT",
        "n_pairs": len(results),
        "n_valid": len(valid),
        "n_wins_late": len(wins_late),
        "n_wins_early": len(wins_early),
        "note": "Engineering reconnaissance only — not a confirmatory decision",
        "config": cfg.to_dict(),
        "results": results,
    }
    write_json(out_path, summary)
    print(
        f"Pilot saved {out_path}: valid={len(valid)} "
        f"wins_late={len(wins_late)} wins_early={len(wins_early)}"
    )
    return summary


if __name__ == "__main__":
    run_pilot()
