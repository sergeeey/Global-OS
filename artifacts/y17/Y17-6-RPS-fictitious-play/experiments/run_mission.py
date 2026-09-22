"""Y17-6 — game theory: does fictitious play beat a pure-strategy baseline on RPS?

Class: game-theoretic / adversarial dynamics (distinct from Y17-1..5).
Catalog bridge: open-problem #13 Nash / zero-sum games (computational probe only).

Protocol locked before run:
  PAYOFF: rock-paper-scissors zero-sum matrix (rows player 1)
  T = 400 rounds, N_GAMES = 40 seeds
  FP: fictitious play (empirical frequency best response)
  PURE: degenerate always-Rock mixed strategy (highly exploitable baseline)
  Metric: mean absolute exploitability of average mixed strategy
  Nash mixed = (1/3,1/3,1/3); value = 0
  MCID: mean_exploit(FP) ≤ 0.25 · mean_exploit(PURE)
"""

from __future__ import annotations

from typing import Any

import numpy as np

RPS = np.array(
    [
        [0.0, -1.0, 1.0],
        [1.0, 0.0, -1.0],
        [-1.0, 1.0, 0.0],
    ],
    dtype=float,
)
NASH = np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
T_ROUNDS = 400
N_GAMES = 40
SEED_START = 700
MCID_RATIO = 0.25
PURE_ACTION = 0


def exploitability(mix: np.ndarray, payoff: np.ndarray = RPS) -> float:
    mix = np.asarray(mix, dtype=float)
    mix = mix / mix.sum()
    row_br = float(np.max(payoff @ mix))
    col_br = float(np.min(mix @ payoff))
    return abs(row_br) + abs(col_br)


def fictitious_play(payoff: np.ndarray, t: int, rng: np.random.Generator) -> np.ndarray:
    n = payoff.shape[0]
    counts_row = np.ones(n)
    counts_col = np.ones(n)
    for _ in range(t):
        bel_col = counts_col / counts_col.sum()
        bel_row = counts_row / counts_row.sum()
        row_vals = payoff @ bel_col
        col_vals = bel_row @ payoff
        row_best = np.flatnonzero(row_vals >= row_vals.max() - 1e-12)
        col_best = np.flatnonzero(col_vals <= col_vals.min() + 1e-12)
        a_row = int(rng.choice(row_best))
        a_col = int(rng.choice(col_best))
        counts_row[a_row] += 1
        counts_col[a_col] += 1
    return counts_row / counts_row.sum()


def pure_baseline(action: int, t: int, n_actions: int = 3) -> np.ndarray:
    counts = np.ones(n_actions)
    counts[action] += t
    return counts / counts.sum()


def run_experiment() -> dict[str, Any]:
    fp_exps: list[float] = []
    pure_exps: list[float] = []
    per_seed: dict[str, Any] = {}
    mix_pure = pure_baseline(PURE_ACTION, T_ROUNDS)
    e_pure_fixed = exploitability(mix_pure)
    for i in range(N_GAMES):
        seed = SEED_START + i
        rng_fp = np.random.default_rng(seed)
        mix_fp = fictitious_play(RPS, T_ROUNDS, rng_fp)
        e_fp = exploitability(mix_fp)
        fp_exps.append(e_fp)
        pure_exps.append(e_pure_fixed)
        per_seed[str(seed)] = {
            "exploit_fp": e_fp,
            "exploit_pure": e_pure_fixed,
            "mix_fp": mix_fp.tolist(),
        }

    mean_fp = float(np.mean(fp_exps))
    mean_pure = float(np.mean(pure_exps))
    ratio = mean_fp / mean_pure if mean_pure > 0 else float("inf")
    beats = ratio <= MCID_RATIO

    if beats:
        decision = "SUPPORTED"
        nulls: list[dict[str, Any]] = []
    else:
        decision = "REJECTED"
        nulls = [
            {
                "id": "fp_fails_mcid_vs_pure",
                "mean_exploit_fp": mean_fp,
                "mean_exploit_pure": mean_pure,
                "ratio": ratio,
                "mcid_ratio": MCID_RATIO,
            }
        ]

    contradictory: list[dict[str, Any]] = []
    e_nash = exploitability(NASH)
    if beats and mean_fp > 0.5:
        contradictory.append(
            {
                "note": "FP beats pure MCID but absolute exploit still large",
                "mean_exploit_fp": mean_fp,
                "rule": "walled descriptive",
            }
        )

    return {
        "config": {
            "class": "game_theoretic_zero_sum",
            "game": "rock_paper_scissors",
            "t_rounds": T_ROUNDS,
            "n_games": N_GAMES,
            "seed_start": SEED_START,
            "fp": "fictitious_play_empirical_BR",
            "baseline": "pure_always_rock",
            "metric": "mean_exploitability",
            "mcid_ratio": MCID_RATIO,
            "y17_writes": False,
            "catalog_bridge": "open-problem #13 Nash zero-sum (computational probe only)",
        },
        "primary": {
            "mean_exploit_fp": mean_fp,
            "mean_exploit_pure": mean_pure,
            "ratio_fp_over_pure": ratio,
            "beats_baseline_mcid": beats,
            "nash_exploit": e_nash,
            "per_seed": per_seed,
        },
        "decision": decision,
        "nulls": nulls,
        "contradictory_evidence": contradictory,
        "scope": {
            "qualification": (
                "SUPPORTED means FP mean exploitability ≤ 0.25× always-Rock on this RPS "
                "ensemble — not a general Nash sample-complexity theorem."
            )
        },
    }


def decide_fn(raw: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    return raw["decision"], raw.get("nulls", [])


def deterministic_verify(raw: dict[str, Any]) -> tuple[str, list[str]]:
    checks: list[str] = []
    ok = True
    if raw["config"]["y17_writes"] is not False:
        ok = False
        checks.append("y17_writes must be false")
    else:
        checks.append("no Y-17 writes")
    ratio = raw["primary"]["ratio_fp_over_pure"]
    expected = "SUPPORTED" if ratio <= MCID_RATIO else "REJECTED"
    if raw["decision"] != expected:
        ok = False
        checks.append(f"decision {raw['decision']} != expected {expected}")
    else:
        checks.append("decision matches prereg MCID rule")
    if not (0.0 <= raw["primary"]["mean_exploit_fp"] < 5.0):
        ok = False
        checks.append("fp exploit out of range")
    else:
        checks.append("fp exploit finite")
    if raw["primary"]["mean_exploit_pure"] <= raw["primary"]["mean_exploit_fp"]:
        ok = False
        checks.append("pure baseline should be more exploitable than FP")
    else:
        checks.append("pure baseline more exploitable than FP")
    return ("PASS" if ok else "FAIL", checks)


if __name__ == "__main__":
    import json

    out = run_experiment()
    print(
        json.dumps(
            {
                "decision": out["decision"],
                "primary": {
                    k: out["primary"][k]
                    for k in ("mean_exploit_fp", "mean_exploit_pure", "ratio_fp_over_pure")
                },
            },
            indent=2,
        )
    )
