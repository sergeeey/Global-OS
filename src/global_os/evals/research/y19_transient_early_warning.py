"""Y19 — early-warning of long transients in random Boolean networks.

Eval harness only (ADR-0009). Not a T0/T1 surface.

Scientific question (answer unknown a priori):
  Do local spectral / sensitivity features of an early trajectory window
  improve out-of-sample prediction of a later long-transient event beyond
  simple baselines (activity, entropy, system size)?

Holdout seeds are sealed before any holdout feature/label compute in the
decision path (train fit never sees holdout).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

Decision = Literal["SUPPORTED", "REJECTED", "INCONCLUSIVE"]

# --- Locked protocol (do not change after first holdout peek) ---
PROTOCOL_VERSION = "Y19-H1-v1"
N_CHOICES = (16, 20, 24)
K_CHOICES = (2, 3)
MAX_STEPS = 120
EARLY_WINDOW = 6
# Long transient = steps-to-attractor strictly above this threshold
LONG_TRANSIENT_TAU = 10
TRAIN_SEEDS = tuple(range(1000, 1180))  # 180 systems
HOLD_SEEDS = tuple(range(5000, 5120))  # 120 systems — sealed
# Disjoint from Y17 seed ranges (550-564, 650-664, etc.)
MCID_BRIER_RATIO = 0.90  # candidate Brier <= 0.90 * baseline Brier on holdout
MIN_HOLD_POSITIVES = 12
MIN_HOLD_NEGATIVES = 12


@dataclass(frozen=True)
class CompetingHypothesis:
    id: str
    statement: str


COMPETING: tuple[CompetingHypothesis, ...] = (
    CompetingHypothesis(
        id="H_spectral",
        statement=(
            "Local spectral and sensitivity features of the early window contain "
            "holdout-predictive information about long-transient onset beyond "
            "baseline activity/entropy/size features (Y19-H1)."
        ),
    ),
    CompetingHypothesis(
        id="H_baseline_sufficient",
        statement=(
            "All predictable signal is already in simple features; adding spectral/"
            "sensitivity features does not improve sealed-holdout Brier by MCID."
        ),
    ),
    CompetingHypothesis(
        id="H_size_spurious",
        statement=(
            "Any apparent candidate gain is spurious size/K confounding; after "
            "ablating N/K from the candidate, holdout MCID fails."
        ),
    ),
)


def _rng(seed: int) -> Any:
    """Deterministic xorshift32 → floats in [0,1)."""

    class R:
        __slots__ = ("s",)

        def __init__(self, s: int) -> None:
            self.s = s & 0xFFFFFFFF

        def u32(self) -> int:
            x = self.s
            x ^= (x << 13) & 0xFFFFFFFF
            x ^= x >> 17
            x ^= (x << 5) & 0xFFFFFFFF
            self.s = x & 0xFFFFFFFF
            return self.s

        def random(self) -> float:
            return self.u32() / 0xFFFFFFFF

        def randint(self, a: int, b: int) -> int:
            return a + (self.u32() % (b - a + 1))

        def choice(self, seq: tuple[int, ...]) -> int:
            return seq[self.u32() % len(seq)]

        def sample_bits(self, n: int) -> list[int]:
            return [1 if self.random() < 0.5 else 0 for _ in range(n)]

    return R(seed)


def _bool_fn_table(k: int, rng: Any) -> list[int]:
    """Truth table of length 2^k with output bits."""
    return [1 if rng.random() < 0.5 else 0 for _ in range(1 << k)]


def _generate_network(seed: int) -> dict[str, Any]:
    rng = _rng(seed)
    n = rng.choice(N_CHOICES)
    k = rng.choice(K_CHOICES)
    wiring: list[list[int]] = []
    tables: list[list[int]] = []
    for i in range(n):
        # Prefer distinct inputs when possible
        inputs: list[int] = []
        while len(inputs) < k:
            j = rng.randint(0, n - 1)
            if j not in inputs or n < k:
                inputs.append(j)
            if n < k and len(inputs) >= k:
                break
        while len(inputs) < k:
            inputs.append(rng.randint(0, n - 1))
        wiring.append(inputs[:k])
        tables.append(_bool_fn_table(k, rng))
    return {"seed": seed, "n": n, "k": k, "wiring": wiring, "tables": tables}


def _step(state: list[int], net: dict[str, Any]) -> list[int]:
    nxt = []
    for i in range(net["n"]):
        idx = 0
        for bit, src in enumerate(net["wiring"][i]):
            if state[src]:
                idx |= 1 << bit
        nxt.append(net["tables"][i][idx])
    return nxt


def _simulate(net: dict[str, Any], ic_seed: int) -> dict[str, Any]:
    rng = _rng(ic_seed ^ (net["seed"] * 2654435761 & 0xFFFFFFFF))
    state = rng.sample_bits(net["n"])
    traj = [list(state)]
    seen: dict[tuple[int, ...], int] = {tuple(state): 0}
    attractor_start = None
    for t in range(1, MAX_STEPS + 1):
        state = _step(state, net)
        key = tuple(state)
        traj.append(list(state))
        if key in seen:
            attractor_start = seen[key]
            steps_to_attractor = seen[key]  # transient length
            break
        seen[key] = t
    else:
        steps_to_attractor = MAX_STEPS
        attractor_start = None
    long_transient = int(steps_to_attractor > LONG_TRANSIENT_TAU)
    return {
        "traj": traj,
        "steps_to_attractor": steps_to_attractor,
        "attractor_start": attractor_start,
        "long_transient": long_transient,
        "n": net["n"],
        "k": net["k"],
        "network_seed": net["seed"],
        "ic_seed": ic_seed,
    }


def _entropy_bits(bits: list[int]) -> float:
    if not bits:
        return 0.0
    p = sum(bits) / len(bits)
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return float(-(p * math.log2(p) + (1 - p) * math.log2(1 - p)))


def _activity_series(traj: list[list[int]], window: int) -> list[float]:
    return [sum(s) / len(s) for s in traj[:window]]


def _dft_high_energy(series: list[float]) -> float:
    """Fraction of DFT power in upper half of frequencies (stdlib DFT)."""
    m = len(series)
    if m < 2:
        return 0.0
    mean = sum(series) / m
    x = [v - mean for v in series]
    powers: list[float] = []
    for k in range(m):
        re = sum(x[n] * math.cos(2 * math.pi * k * n / m) for n in range(m))
        im = sum(-x[n] * math.sin(2 * math.pi * k * n / m) for n in range(m))
        powers.append(re * re + im * im)
    total = sum(powers) or 1.0
    hi = sum(powers[m // 2 :])
    return float(hi / total)


def _mean_sensitivity(net: dict[str, Any], state: list[int]) -> float:
    """Mean next-state Hamming change under single-bit flips (local sensitivity)."""
    base = _step(state, net)
    n = net["n"]
    total = 0
    for i in range(n):
        flipped = list(state)
        flipped[i] = 1 - flipped[i]
        nxt = _step(flipped, net)
        total += sum(a != b for a, b in zip(base, nxt, strict=True))
    return total / (n * n)


def _features(sim: dict[str, Any], net: dict[str, Any]) -> dict[str, float]:
    traj = sim["traj"]
    w = min(EARLY_WINDOW, len(traj))
    window_states = traj[:w]
    flat = [b for s in window_states for b in s]
    acts = _activity_series(traj, w)
    last = window_states[-1]
    baseline = {
        "n": float(sim["n"]),
        "k": float(sim["k"]),
        "mean_activity": float(sum(acts) / len(acts)),
        "activity_std": float(
            math.sqrt(sum((a - sum(acts) / len(acts)) ** 2 for a in acts) / len(acts))
        ),
        "state_entropy": _entropy_bits(flat),
    }
    candidate_extra = {
        "sensitivity": _mean_sensitivity(net, last),
        "spectral_high_energy": _dft_high_energy(acts),
        "activity_range": float(max(acts) - min(acts)),
    }
    return {**baseline, **candidate_extra}


BASELINE_KEYS = ("n", "k", "mean_activity", "activity_std", "state_entropy")
CANDIDATE_KEYS = BASELINE_KEYS + ("sensitivity", "spectral_high_energy", "activity_range")
ABLATED_KEYS = (
    "mean_activity",
    "activity_std",
    "state_entropy",
    "sensitivity",
    "spectral_high_energy",
    "activity_range",
)  # N/K removed


def _collect_cases(seeds: tuple[int, ...]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for seed in seeds:
        net = _generate_network(seed)
        # One IC per network seed (ic derived); keeps N manageable
        sim = _simulate(net, ic_seed=seed * 17 + 3)
        feats = _features(sim, net)
        cases.append(
            {
                "network_seed": seed,
                "label": sim["long_transient"],
                "steps_to_attractor": sim["steps_to_attractor"],
                "features": feats,
            }
        )
    return cases


def _design_matrix(cases: list[dict[str, Any]], keys: tuple[str, ...]) -> tuple[list[list[float]], list[float]]:
    xs = [[float(c["features"][k]) for k in keys] for c in cases]
    ys = [float(c["label"]) for c in cases]
    return xs, ys


def _fit_ridge(xs: list[list[float]], ys: list[float], l2: float = 1e-2) -> list[float]:
    """Ridge linear probability model with intercept; stdlib Gaussian elimination."""
    n = len(xs)
    d = len(xs[0])
    # Augment with intercept
    a = [[1.0] + row[:] for row in xs]
    dim = d + 1
    # Normal equations (X^T X + λI) β = X^T y ; don't penalize intercept
    xtx = [[0.0] * dim for _ in range(dim)]
    xty = [0.0] * dim
    for i in range(n):
        for r in range(dim):
            xty[r] += a[i][r] * ys[i]
            for c in range(dim):
                xtx[r][c] += a[i][r] * a[i][c]
    for j in range(1, dim):
        xtx[j][j] += l2
    return _solve(xtx, xty)


def _solve(mat: list[list[float]], vec: list[float]) -> list[float]:
    m = [row[:] + [vec[i]] for i, row in enumerate(mat)]
    n = len(vec)
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            continue
        m[col], m[pivot] = m[pivot], m[col]
        div = m[col][col]
        for j in range(col, n + 1):
            m[col][j] /= div
        for r in range(n):
            if r == col:
                continue
            factor = m[r][col]
            for j in range(col, n + 1):
                m[r][j] -= factor * m[col][j]
    return [m[i][n] for i in range(n)]


def _predict(beta: list[float], xs: list[list[float]]) -> list[float]:
    out: list[float] = []
    for row in xs:
        z = beta[0] + sum(b * x for b, x in zip(beta[1:], row, strict=True))
        # Clamp to [0,1] for Brier
        out.append(min(1.0, max(0.0, z)))
    return out


def _brier(ys: list[float], ps: list[float]) -> float:
    return sum((p - y) ** 2 for p, y in zip(ps, ys, strict=True)) / len(ys)


def _auc(ys: list[float], ps: list[float]) -> float:
    """Mann–Whitney AUC; 0.5 if undefined."""
    pos = [p for p, y in zip(ps, ys, strict=True) if y == 1.0]
    neg = [p for p, y in zip(ps, ys, strict=True) if y == 0.0]
    if not pos or not neg:
        return 0.5
    wins = 0.0
    for p in pos:
        for q in neg:
            if p > q:
                wins += 1.0
            elif p == q:
                wins += 0.5
    return wins / (len(pos) * len(neg))


def run_experiment(*, peek_holdout_labels_in_train: bool = False) -> dict[str, Any]:
    """Execute locked Y19-H1 protocol.

    peek_holdout_labels_in_train is ONLY for adversarial tests (must stay False in prod).
    """
    if set(TRAIN_SEEDS) & set(HOLD_SEEDS):
        raise RuntimeError("train/hold seed collision")

    train_cases = _collect_cases(TRAIN_SEEDS)
    hold_cases = _collect_cases(HOLD_SEEDS)
    # Honest path: fit on train only. Adversarial tests may merge hold into fit.
    fit_cases = train_cases + hold_cases if peek_holdout_labels_in_train else train_cases

    def eval_keys(keys: tuple[str, ...]) -> dict[str, Any]:
        x_tr, y_tr = _design_matrix(fit_cases, keys)
        beta = _fit_ridge(x_tr, y_tr)
        x_te, y_te = _design_matrix(hold_cases, keys)
        pred = _predict(beta, x_te)
        return {
            "brier": _brier(y_te, pred),
            "auc": _auc(y_te, pred),
            "beta": beta,
            "keys": list(keys),
        }

    baseline = eval_keys(BASELINE_KEYS)
    candidate = eval_keys(CANDIDATE_KEYS)
    ablated = eval_keys(ABLATED_KEYS)

    y_hold = [c["label"] for c in hold_cases]
    n_pos = sum(y_hold)
    n_neg = len(y_hold) - n_pos
    ratio = candidate["brier"] / baseline["brier"] if baseline["brier"] > 1e-12 else float("inf")
    ablated_ratio = ablated["brier"] / baseline["brier"] if baseline["brier"] > 1e-12 else float("inf")

    sample_ok = n_pos >= MIN_HOLD_POSITIVES and n_neg >= MIN_HOLD_NEGATIVES
    beats_mcid = ratio <= MCID_BRIER_RATIO
    ablation_ok = ablated_ratio <= MCID_BRIER_RATIO

    if not sample_ok:
        decision: Decision = "INCONCLUSIVE"
        winning = "sample_too_small"
    elif beats_mcid and ablation_ok:
        decision = "SUPPORTED"
        winning = "H_spectral"
    elif beats_mcid and not ablation_ok:
        decision = "INCONCLUSIVE"
        winning = "H_size_spurious"
    else:
        decision = "REJECTED"
        winning = "H_baseline_sufficient"

    nulls: list[dict[str, Any]] = []
    if decision == "REJECTED":
        nulls.append(
            {
                "id": "y19_holdout_mcid_fail",
                "brier_ratio": ratio,
                "mcid": MCID_BRIER_RATIO,
                "interpretation": "candidate failed sealed-holdout MCID vs baseline",
            }
        )
    if decision == "INCONCLUSIVE" and not sample_ok:
        nulls.append(
            {
                "id": "y19_holdout_balance",
                "n_pos": n_pos,
                "n_neg": n_neg,
                "interpretation": "holdout class balance below preregistered minima",
            }
        )

    protocol_hash = hashlib.sha256(
        json.dumps(
            {
                "protocol": PROTOCOL_VERSION,
                "train": list(TRAIN_SEEDS),
                "hold": list(HOLD_SEEDS),
                "tau": LONG_TRANSIENT_TAU,
                "mcid": MCID_BRIER_RATIO,
                "window": EARLY_WINDOW,
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()[:16]

    return {
        "protocol_version": PROTOCOL_VERSION,
        "protocol_hash": protocol_hash,
        "competing_hypotheses": [asdict(h) for h in COMPETING],
        "winning_hypothesis_id": winning,
        "decision": decision,
        "train_n": len(TRAIN_SEEDS),
        "hold_n": len(HOLD_SEEDS),
        "hold_positives": n_pos,
        "hold_negatives": n_neg,
        "baseline": {"brier": baseline["brier"], "auc": baseline["auc"]},
        "candidate": {"brier": candidate["brier"], "auc": candidate["auc"]},
        "ablated_no_size": {"brier": ablated["brier"], "auc": ablated["auc"]},
        "brier_ratio": ratio,
        "ablated_brier_ratio": ablated_ratio,
        "mcid_brier_ratio": MCID_BRIER_RATIO,
        "long_transient_tau": LONG_TRANSIENT_TAU,
        "early_window": EARLY_WINDOW,
        "seed_policy": {
            "train": f"{TRAIN_SEEDS[0]}-{TRAIN_SEEDS[-1]}",
            "hold": f"{HOLD_SEEDS[0]}-{HOLD_SEEDS[-1]}",
            "disjoint_from_y17": True,
        },
        "leak_checks": {
            "train_hold_disjoint": True,
            "peek_holdout_labels_in_train": peek_holdout_labels_in_train,
        },
        "null_results": nulls,
        "scientific_claim_accepted": decision == "SUPPORTED",
        "answer_known_a_priori": False,
    }


def write_preregistration(path: Path) -> None:
    payload = {
        "mission_id": "Y19-H1",
        "protocol_version": PROTOCOL_VERSION,
        "preregistered_before_data": True,
        "hypothesis": COMPETING[0].statement,
        "competing_hypotheses": [asdict(h) for h in COMPETING],
        "primary_outcome": "holdout Brier_candidate / Brier_baseline",
        "test": "sealed seed holdout; ridge linear probability; Boolean NK networks",
        "null": "candidate fails MCID on holdout (ratio > 0.90)",
        "threshold": {"mcid_brier_ratio": MCID_BRIER_RATIO},
        "primary_criterion": {
            "statistic": "holdout_brier_ratio",
            "mcid_ratio": MCID_BRIER_RATIO,
            "decision_rule": {
                "SUPPORTED": "ratio <= 0.90 AND ablated_ratio <= 0.90 AND holdout balance OK",
                "REJECTED": "ratio > 0.90",
                "INCONCLUSIVE": "balance fail OR MCID pass but ablation fail",
            },
        },
        "kill_criterion": (
            "SUPPORTED iff holdout Brier_candidate ≤ 0.90·Brier_baseline AND "
            "size-ablated candidate also meets MCID; "
            "REJECTED iff MCID fails; "
            "INCONCLUSIVE iff sample imbalance or MCID pass but ablation fails. "
            "No refit on holdout; no post-hoc MCID/tau/window change."
        ),
        "seed_data_policy": {
            "train": list(TRAIN_SEEDS),
            "hold": list(HOLD_SEEDS),
            "note": "hold sealed; disjoint from Y17 ranges",
        },
        "system": {
            "family": "random_boolean_NK",
            "N": list(N_CHOICES),
            "K": list(K_CHOICES),
            "max_steps": MAX_STEPS,
            "early_window": EARLY_WINDOW,
            "long_transient_tau": LONG_TRANSIENT_TAU,
        },
        "baseline_features": list(BASELINE_KEYS),
        "candidate_extra_features": ["sensitivity", "spectral_high_energy", "activity_range"],
        "forbidden_a_priori_knowledge": [
            "holdout labels and holdout features before train lock",
            "post-hoc tau / MCID / window edits after seeing ratio",
            "merging train+hold for final fit",
            "switching primary metric after holdout",
        ],
        "what_global_os_must_not_know_early": [
            "Whether Y19-H1 is true",
            "Holdout outcomes",
            "Which competing hypothesis wins",
        ],
        "stopping_rule": "Single locked split; one fit; one holdout evaluation.",
        "falsification": {
            "REJECTED": "holdout brier_ratio > 0.90",
            "INCONCLUSIVE_balance": f"hold pos<{MIN_HOLD_POSITIVES} or neg<{MIN_HOLD_NEGATIVES}",
            "INCONCLUSIVE_spurious_size": "MCID pass but ablated_no_size fails MCID",
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
