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


def _generate_network(
    seed: int, *, n: int | None = None, k: int | None = None
) -> dict[str, Any]:
    rng = _rng(seed)
    n_eff = int(n) if n is not None else int(rng.choice(N_CHOICES))
    k_eff = int(k) if k is not None else int(rng.choice(K_CHOICES))
    k_eff = min(k_eff, n_eff)
    wiring: list[list[int]] = []
    tables: list[list[int]] = []
    for _i in range(n_eff):
        inputs: list[int] = []
        while len(inputs) < k_eff:
            j = rng.randint(0, n_eff - 1)
            if j not in inputs or n_eff < k_eff:
                inputs.append(j)
            if n_eff < k_eff and len(inputs) >= k_eff:
                break
        while len(inputs) < k_eff:
            inputs.append(rng.randint(0, n_eff - 1))
        wiring.append(inputs[:k_eff])
        tables.append(_bool_fn_table(k_eff, rng))
    return {"seed": seed, "n": n_eff, "k": k_eff, "wiring": wiring, "tables": tables}


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
    period = 0
    hit_t = MAX_STEPS
    for t in range(1, MAX_STEPS + 1):
        state = _step(state, net)
        key = tuple(state)
        traj.append(list(state))
        if key in seen:
            attractor_start = seen[key]
            steps_to_attractor = seen[key]
            period = t - attractor_start
            hit_t = t
            break
        seen[key] = t
    else:
        steps_to_attractor = MAX_STEPS
        attractor_start = None
        period = 0
        hit_t = MAX_STEPS
    long_transient = int(steps_to_attractor > LONG_TRANSIENT_TAU)
    return {
        "traj": traj,
        "steps_to_attractor": steps_to_attractor,
        "attractor_start": attractor_start,
        "period": period,
        "hit_t": hit_t,
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
    return float(total) / float(int(n) * int(n))


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


def _collect_cases(
    seeds: tuple[int, ...],
    *,
    n: int | None = None,
    k: int | None = None,
    n_chooser: Any | None = None,
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for seed in seeds:
        n_use = n_chooser(seed) if n_chooser is not None else n
        net = _generate_network(seed, n=n_use, k=k)
        sim = _simulate(net, ic_seed=seed * 17 + 3)
        feats = _features(sim, net)
        cases.append(
            {
                "network_seed": seed,
                "label": sim["long_transient"],
                "steps_to_attractor": sim["steps_to_attractor"],
                "features": feats,
                "n": sim["n"],
                "k": sim["k"],
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


# --- Y19-H2: mechanistic follow-up after H1 REJECTED (new sealed seeds) ---
PROTOCOL_VERSION_H2 = "Y19-H2-v1"
TRAIN_SEEDS_H2 = tuple(range(2000, 2180))  # 180 — disjoint from H1/Y17
HOLD_SEEDS_H2 = tuple(range(6000, 6120))  # 120 sealed
ACTIVITY_KEYS = ("mean_activity", "activity_std")
FULL_BASELINE_KEYS = BASELINE_KEYS  # n,k,activity*,entropy

COMPETING_H2: tuple[CompetingHypothesis, ...] = (
    CompetingHypothesis(
        id="H_size_entropy_add_signal",
        statement=(
            "Adding {n, k, state_entropy} to activity dynamics improves sealed-holdout "
            "Brier by MCID versus activity-only (mean_activity, activity_std)."
        ),
    ),
    CompetingHypothesis(
        id="H_activity_core_sufficient",
        statement=(
            "Holdout signal of the Y19 baseline is carried by early activity dynamics "
            "alone; size/entropy extras fail MCID against activity-only."
        ),
    ),
    CompetingHypothesis(
        id="H_underpowered",
        statement="Holdout class balance too weak to decide between activity-core and full baseline.",
    ),
)


def run_experiment_h2(*, peek_holdout_labels_in_train: bool = False) -> dict[str, Any]:
    """Y19-H2 mechanistic protocol — does not mutate H1 locks."""
    if set(TRAIN_SEEDS_H2) & set(HOLD_SEEDS_H2):
        raise RuntimeError("H2 train/hold collision")
    if set(TRAIN_SEEDS_H2) & (set(TRAIN_SEEDS) | set(HOLD_SEEDS)):
        raise RuntimeError("H2 train overlaps H1 seeds")
    if set(HOLD_SEEDS_H2) & (set(TRAIN_SEEDS) | set(HOLD_SEEDS)):
        raise RuntimeError("H2 hold overlaps H1 seeds")

    train_cases = _collect_cases(TRAIN_SEEDS_H2)
    hold_cases = _collect_cases(HOLD_SEEDS_H2)
    fit_cases = train_cases + hold_cases if peek_holdout_labels_in_train else train_cases

    def eval_keys(keys: tuple[str, ...]) -> dict[str, Any]:
        x_tr, y_tr = _design_matrix(fit_cases, keys)
        beta = _fit_ridge(x_tr, y_tr)
        x_te, y_te = _design_matrix(hold_cases, keys)
        pred = _predict(beta, x_te)
        return {"brier": _brier(y_te, pred), "auc": _auc(y_te, pred), "keys": list(keys)}

    activity = eval_keys(ACTIVITY_KEYS)
    full = eval_keys(FULL_BASELINE_KEYS)
    y_hold = [c["label"] for c in hold_cases]
    n_pos = sum(y_hold)
    n_neg = len(y_hold) - n_pos
    # full should be lower Brier if size/entropy help
    ratio = full["brier"] / activity["brier"] if activity["brier"] > 1e-12 else float("inf")
    sample_ok = n_pos >= MIN_HOLD_POSITIVES and n_neg >= MIN_HOLD_NEGATIVES
    beats_mcid = ratio <= MCID_BRIER_RATIO

    if not sample_ok:
        decision: Decision = "INCONCLUSIVE"
        winning = "H_underpowered"
    elif beats_mcid:
        decision = "SUPPORTED"
        winning = "H_size_entropy_add_signal"
    else:
        decision = "REJECTED"
        winning = "H_activity_core_sufficient"

    nulls: list[dict[str, Any]] = []
    if decision == "REJECTED":
        nulls.append(
            {
                "id": "y19_h2_full_vs_activity_mcid_fail",
                "brier_ratio_full_over_activity": ratio,
                "mcid": MCID_BRIER_RATIO,
                "interpretation": "size/entropy extras failed MCID vs activity-only",
            }
        )

    return {
        "protocol_version": PROTOCOL_VERSION_H2,
        "prior_mission": "Y19-H1",
        "prior_decision": "REJECTED",
        "competing_hypotheses": [asdict(h) for h in COMPETING_H2],
        "winning_hypothesis_id": winning,
        "decision": decision,
        "train_n": len(TRAIN_SEEDS_H2),
        "hold_n": len(HOLD_SEEDS_H2),
        "hold_positives": n_pos,
        "hold_negatives": n_neg,
        "activity_only": activity,
        "full_baseline": full,
        "brier_ratio_full_over_activity": ratio,
        "mcid_brier_ratio": MCID_BRIER_RATIO,
        "seed_policy": {
            "train": f"{TRAIN_SEEDS_H2[0]}-{TRAIN_SEEDS_H2[-1]}",
            "hold": f"{HOLD_SEEDS_H2[0]}-{HOLD_SEEDS_H2[-1]}",
            "disjoint_from_h1_and_y17": True,
        },
        "leak_checks": {
            "train_hold_disjoint": True,
            "peek_holdout_labels_in_train": peek_holdout_labels_in_train,
        },
        "null_results": nulls,
        "scientific_claim_accepted": decision == "SUPPORTED",
        "answer_known_a_priori": False,
    }


def write_preregistration_h2(path: Path) -> None:
    payload = {
        "mission_id": "Y19-H2",
        "protocol_version": PROTOCOL_VERSION_H2,
        "preregistered_before_data": True,
        "follows": "Y19-H1 REJECTED → H_baseline_sufficient",
        "hypothesis": COMPETING_H2[0].statement,
        "competing_hypotheses": [asdict(h) for h in COMPETING_H2],
        "primary_outcome": "holdout Brier_full_baseline / Brier_activity_only",
        "primary_criterion": {
            "statistic": "holdout_brier_ratio_full_over_activity",
            "mcid_ratio": MCID_BRIER_RATIO,
            "decision_rule": {
                "SUPPORTED": "ratio <= 0.90",
                "REJECTED": "ratio > 0.90",
                "INCONCLUSIVE": "holdout balance fail",
            },
        },
        "seed_data_policy": {
            "train": list(TRAIN_SEEDS_H2),
            "hold": list(HOLD_SEEDS_H2),
        },
        "activity_features": list(ACTIVITY_KEYS),
        "full_baseline_features": list(FULL_BASELINE_KEYS),
        "system_same_as_h1": True,
        "answer_known_a_priori": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# --- Y19-H3: robustness of H2 (activity-matched + unseen-size + regime) ---
PROTOCOL_VERSION_H3 = "Y19-H3-v1"
TRAIN_SEEDS_H3 = tuple(range(3000, 3240))  # 240 mixed-N train
HOLD_SEEDS_H3_MATCH = tuple(range(7200, 7320))  # 120 in-family hold (gates A, C)
HOLD_SEEDS_H3_UNSEEN = tuple(range(7000, 7120))  # 120 unseen-size hold (gate B)
TRAIN_N_SEEN = (16, 20)
HOLD_N_UNSEEN = 24
MIN_STRATUM = 15  # min cases per activity tertile / regime slice
MIN_STRATUM_POS = 4
MIN_STRATUM_NEG = 4

COMPETING_H3: tuple[CompetingHypothesis, ...] = (
    CompetingHypothesis(
        id="H_h2_robust",
        statement=(
            "Size/entropy extras retain sealed-holdout MCID gain over activity after "
            "activity-matched stratification, on unseen system size N, and in both K regimes."
        ),
    ),
    CompetingHypothesis(
        id="H_size_proxy_or_fragile",
        statement=(
            "Apparent H2 gain is a size proxy and/or fails activity-matched / unseen-N "
            "transfer (collapses under robustness gates)."
        ),
    ),
    CompetingHypothesis(
        id="H_regime_local",
        statement=(
            "Gain is local to one connectivity regime (K) or underpowered outside the "
            "training distribution."
        ),
    ),
)


def _tertile_cuts(values: list[float]) -> tuple[float, float]:
    xs = sorted(values)
    n = len(xs)
    if n < 3:
        return (xs[0], xs[-1]) if xs else (0.0, 1.0)
    return xs[n // 3], xs[(2 * n) // 3]


def _assign_tertile(v: float, c1: float, c2: float) -> int:
    if v <= c1:
        return 0
    if v <= c2:
        return 1
    return 2


def _eval_full_vs_activity(
    fit_cases: list[dict[str, Any]], eval_cases: list[dict[str, Any]]
) -> dict[str, Any]:
    x_tr_a, y_tr = _design_matrix(fit_cases, ACTIVITY_KEYS)
    beta_a = _fit_ridge(x_tr_a, y_tr)
    x_tr_f, _ = _design_matrix(fit_cases, FULL_BASELINE_KEYS)
    beta_f = _fit_ridge(x_tr_f, y_tr)
    x_te_a, y_te = _design_matrix(eval_cases, ACTIVITY_KEYS)
    x_te_f, _ = _design_matrix(eval_cases, FULL_BASELINE_KEYS)
    pred_a = _predict(beta_a, x_te_a)
    pred_f = _predict(beta_f, x_te_f)
    brier_a = _brier(y_te, pred_a)
    brier_f = _brier(y_te, pred_f)
    ratio = brier_f / brier_a if brier_a > 1e-12 else float("inf")
    return {
        "brier_activity": brier_a,
        "brier_full": brier_f,
        "brier_ratio": ratio,
        "auc_activity": _auc(y_te, pred_a),
        "auc_full": _auc(y_te, pred_f),
        "n": len(eval_cases),
        "n_pos": int(sum(y_te)),
        "n_neg": int(len(y_te) - sum(y_te)),
        "beats_mcid": ratio <= MCID_BRIER_RATIO,
    }


def _stratum_ok(n_pos: int, n_neg: int, n_tot: int) -> bool:
    return n_tot >= MIN_STRATUM and n_pos >= MIN_STRATUM_POS and n_neg >= MIN_STRATUM_NEG


def run_experiment_h3(*, peek_holdout_labels_in_train: bool = False) -> dict[str, Any]:
    """Y19-H3 robustness of H2 — three preregistered gates."""
    prior = set(TRAIN_SEEDS) | set(HOLD_SEEDS) | set(TRAIN_SEEDS_H2) | set(HOLD_SEEDS_H2)
    for label, seeds in (
        ("train_h3", TRAIN_SEEDS_H3),
        ("hold_match", HOLD_SEEDS_H3_MATCH),
        ("hold_unseen", HOLD_SEEDS_H3_UNSEEN),
    ):
        if set(seeds) & prior:
            raise RuntimeError(f"H3 {label} overlaps prior Y19 seeds")
    if set(HOLD_SEEDS_H3_MATCH) & set(HOLD_SEEDS_H3_UNSEEN):
        raise RuntimeError("H3 hold sets collide")

    train_mixed = _collect_cases(TRAIN_SEEDS_H3)
    hold_match = _collect_cases(HOLD_SEEDS_H3_MATCH)

    def n_seen_chooser(seed: int) -> int:
        return TRAIN_N_SEEN[seed % len(TRAIN_N_SEEN)]

    train_seen_n = _collect_cases(TRAIN_SEEDS_H3, n_chooser=n_seen_chooser)
    hold_unseen_n = _collect_cases(HOLD_SEEDS_H3_UNSEEN, n=HOLD_N_UNSEEN)

    fit_mixed = train_mixed + hold_match if peek_holdout_labels_in_train else train_mixed
    fit_seen = train_seen_n + hold_unseen_n if peek_holdout_labels_in_train else train_seen_n

    # Gate A: activity-matched tertiles
    acts_train = [float(c["features"]["mean_activity"]) for c in train_mixed]
    c1, c2 = _tertile_cuts(acts_train)
    tertile_rows: list[dict[str, Any]] = []
    for t in range(3):
        subset = [
            c
            for c in hold_match
            if _assign_tertile(float(c["features"]["mean_activity"]), c1, c2) == t
        ]
        if not subset:
            tertile_rows.append(
                {"tertile": t, "status": "EMPTY", "beats_mcid": False, "powered": False}
            )
            continue
        metrics = _eval_full_vs_activity(fit_mixed, subset)
        powered = _stratum_ok(metrics["n_pos"], metrics["n_neg"], metrics["n"])
        tertile_rows.append(
            {
                "tertile": t,
                "status": "OK" if powered else "UNDERPOWERED",
                "powered": powered,
                **metrics,
            }
        )
    powered_tert = [r for r in tertile_rows if r.get("powered")]
    if len(powered_tert) < 2:
        gate_a: dict[str, Any] = {
            "name": "activity_matched",
            "status": "UNDERPOWERED",
            "passed": False,
            "tertiles": tertile_rows,
        }
    else:
        n_pass = sum(1 for r in powered_tert if r["beats_mcid"])
        gate_a = {
            "name": "activity_matched",
            "status": "PASS" if n_pass >= 2 else "FAIL",
            "passed": n_pass >= 2,
            "powered_tertiles": len(powered_tert),
            "mcid_pass_tertiles": n_pass,
            "tertiles": tertile_rows,
            "cuts": [c1, c2],
        }

    # Gate B: unseen size
    gate_b_metrics = _eval_full_vs_activity(fit_seen, hold_unseen_n)
    bal_b = (
        gate_b_metrics["n_pos"] >= MIN_HOLD_POSITIVES
        and gate_b_metrics["n_neg"] >= MIN_HOLD_NEGATIVES
    )
    if not bal_b:
        gate_b: dict[str, Any] = {
            "name": "unseen_size",
            "status": "UNDERPOWERED",
            "passed": False,
            **gate_b_metrics,
        }
    else:
        gate_b = {
            "name": "unseen_size",
            "status": "PASS" if gate_b_metrics["beats_mcid"] else "FAIL",
            "passed": bool(gate_b_metrics["beats_mcid"]),
            "train_n_values": list(TRAIN_N_SEEN),
            "hold_n": HOLD_N_UNSEEN,
            **gate_b_metrics,
        }

    # Gate C: regime K
    regime_rows: list[dict[str, Any]] = []
    for kval in (2, 3):
        subset = [c for c in hold_match if int(c["k"]) == kval]
        if not subset:
            regime_rows.append({"k": kval, "status": "EMPTY", "passed": False, "powered": False})
            continue
        metrics = _eval_full_vs_activity(fit_mixed, subset)
        powered = _stratum_ok(metrics["n_pos"], metrics["n_neg"], metrics["n"])
        regime_rows.append(
            {
                "k": kval,
                "status": ("OK" if powered else "UNDERPOWERED"),
                "powered": powered,
                "passed": bool(powered and metrics["beats_mcid"]),
                **metrics,
            }
        )
    powered_reg = [r for r in regime_rows if r.get("powered")]
    failed_reg = [r for r in powered_reg if not r["beats_mcid"]]
    if len(powered_reg) < 2:
        gate_c: dict[str, Any] = {
            "name": "regime_k",
            "status": "UNDERPOWERED",
            "passed": False,
            "regimes": regime_rows,
        }
    elif failed_reg:
        gate_c = {
            "name": "regime_k",
            "status": "FAIL",
            "passed": False,
            "regimes": regime_rows,
        }
    else:
        gate_c = {
            "name": "regime_k",
            "status": "PASS",
            "passed": True,
            "regimes": regime_rows,
        }

    gates = {"A_activity_matched": gate_a, "B_unseen_size": gate_b, "C_regime_k": gate_c}
    statuses = [g["status"] for g in gates.values()]
    if any(s == "FAIL" for s in statuses):
        if gate_c["status"] == "FAIL" and gate_a["status"] != "FAIL" and gate_b["status"] != "FAIL":
            decision: Decision = "REJECTED"
            winning = "H_regime_local"
        else:
            decision = "REJECTED"
            winning = "H_size_proxy_or_fragile"
    elif any(s == "UNDERPOWERED" for s in statuses):
        decision = "INCONCLUSIVE"
        winning = "H_regime_local"
    elif all(g["passed"] for g in gates.values()):
        decision = "SUPPORTED"
        winning = "H_h2_robust"
    else:
        decision = "INCONCLUSIVE"
        winning = "H_regime_local"

    nulls: list[dict[str, Any]] = []
    if decision == "REJECTED":
        nulls.append(
            {
                "id": "y19_h3_robustness_fail",
                "gates": {k: v["status"] for k, v in gates.items()},
                "interpretation": "H2 size/entropy gain did not survive robustness battery",
            }
        )

    return {
        "protocol_version": PROTOCOL_VERSION_H3,
        "prior_mission": "Y19-H2",
        "prior_decision": "SUPPORTED",
        "competing_hypotheses": [asdict(h) for h in COMPETING_H3],
        "winning_hypothesis_id": winning,
        "decision": decision,
        "gates": gates,
        "mcid_brier_ratio": MCID_BRIER_RATIO,
        "seed_policy": {
            "train": f"{TRAIN_SEEDS_H3[0]}-{TRAIN_SEEDS_H3[-1]}",
            "hold_match": f"{HOLD_SEEDS_H3_MATCH[0]}-{HOLD_SEEDS_H3_MATCH[-1]}",
            "hold_unseen_n": f"{HOLD_SEEDS_H3_UNSEEN[0]}-{HOLD_SEEDS_H3_UNSEEN[-1]}",
            "disjoint_from_h1_h2_y17": True,
        },
        "leak_checks": {
            "train_hold_disjoint": True,
            "peek_holdout_labels_in_train": peek_holdout_labels_in_train,
        },
        "null_results": nulls,
        "scientific_claim_accepted": decision == "SUPPORTED",
        "answer_known_a_priori": False,
    }


def write_preregistration_h3(path: Path) -> None:
    payload = {
        "mission_id": "Y19-H3",
        "protocol_version": PROTOCOL_VERSION_H3,
        "preregistered_before_data": True,
        "follows": "Y19-H2 SUPPORTED → test robustness of size/entropy signal",
        "hypothesis": COMPETING_H3[0].statement,
        "competing_hypotheses": [asdict(h) for h in COMPETING_H3],
        "gates": {
            "A_activity_matched": (
                "On in-family hold, ≥2 activity tertiles (train cuts) must show "
                f"Brier_full/Brier_activity ≤ {MCID_BRIER_RATIO}"
            ),
            "B_unseen_size": (
                f"Train N∈{list(TRAIN_N_SEEN)}; hold N={HOLD_N_UNSEEN}; MCID vs activity"
            ),
            "C_regime_k": "Both powered K=2 and K=3 hold slices must meet MCID",
        },
        "primary_criterion": {
            "statistic": "all_three_gates_pass",
            "mcid_ratio": MCID_BRIER_RATIO,
            "decision_rule": {
                "SUPPORTED": "A and B and C PASS",
                "REJECTED": "any gate FAIL",
                "INCONCLUSIVE": "any gate UNDERPOWERED and none FAIL",
            },
        },
        "seed_data_policy": {
            "train": list(TRAIN_SEEDS_H3),
            "hold_match": list(HOLD_SEEDS_H3_MATCH),
            "hold_unseen": list(HOLD_SEEDS_H3_UNSEEN),
        },
        "answer_known_a_priori": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# --- Y19-H4: size vs entropy decomposition ---
PROTOCOL_VERSION_H4 = "Y19-H4-v1"
TRAIN_SEEDS_H4 = tuple(range(4000, 4300))  # 300
HOLD_SEEDS_H4 = tuple(range(8000, 8150))  # 150 sealed
N_PANEL_H4 = (16, 20, 24)
ACTIVITY_KEYS_H4 = ACTIVITY_KEYS  # mean_activity, activity_std
ENTROPY_KEY = "state_entropy"
ACTIVITY_ENTROPY_KEYS = ACTIVITY_KEYS + (ENTROPY_KEY,)
ACTIVITY_N_KEYS = ACTIVITY_KEYS + ("n",)
ACTIVITY_N_ENTROPY_KEYS = ACTIVITY_KEYS + ("n", ENTROPY_KEY)

COMPETING_H4: tuple[CompetingHypothesis, ...] = (
    CompetingHypothesis(
        id="H_entropy_survives_n_control",
        statement=(
            "At fixed N / after residualizing entropy on N+activity / under leave-one-N-out, "
            "entropy retains sealed-holdout predictive value beyond activity (MCID)."
        ),
    ),
    CompetingHypothesis(
        id="H_effect_is_mostly_n",
        statement=(
            "After N control, entropy loses MCID gain; the H2/H3 size/entropy signal is "
            "explained mainly by system size N."
        ),
    ),
    CompetingHypothesis(
        id="H_conditional_on_n",
        statement=(
            "Entropy effect is mixed across N (survives some sizes/LOO folds, fails others) "
            "or underpowered — conditional, not global."
        ),
    ),
)


def _fit_predict_feature(
    fit_cases: list[dict[str, Any]],
    eval_cases: list[dict[str, Any]],
    *,
    target_key: str,
    predictor_keys: tuple[str, ...],
) -> list[float]:
    """Linear predict target_key from predictor_keys; return predictions on eval."""
    x_tr, y_tr = _design_matrix(fit_cases, predictor_keys)
    # y is label in _design_matrix — override with feature target
    y_tr = [float(c["features"][target_key]) for c in fit_cases]
    beta = _fit_ridge(x_tr, y_tr)
    x_te, _ = _design_matrix(eval_cases, predictor_keys)
    return _predict(beta, x_te)


def _with_residual_entropy(
    fit_cases: list[dict[str, Any]], eval_cases: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Attach residual_entropy = entropy - E[entropy | N, activity] fit on train."""
    preds_fit = _fit_predict_feature(
        fit_cases,
        fit_cases,
        target_key=ENTROPY_KEY,
        predictor_keys=ACTIVITY_N_KEYS,
    )
    preds_eval = _fit_predict_feature(
        fit_cases,
        eval_cases,
        target_key=ENTROPY_KEY,
        predictor_keys=ACTIVITY_N_KEYS,
    )

    def attach(cases: list[dict[str, Any]], preds: list[float]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for c, p in zip(cases, preds, strict=True):
            feats = dict(c["features"])
            feats["residual_entropy"] = float(feats[ENTROPY_KEY]) - float(p)
            out.append({**c, "features": feats})
        return out

    return attach(fit_cases, preds_fit), attach(eval_cases, preds_eval)


def _eval_keys_vs(
    fit_cases: list[dict[str, Any]],
    eval_cases: list[dict[str, Any]],
    *,
    base_keys: tuple[str, ...],
    full_keys: tuple[str, ...],
) -> dict[str, Any]:
    x_tr_b, y_tr = _design_matrix(fit_cases, base_keys)
    beta_b = _fit_ridge(x_tr_b, y_tr)
    x_tr_f, _ = _design_matrix(fit_cases, full_keys)
    beta_f = _fit_ridge(x_tr_f, y_tr)
    x_te_b, y_te = _design_matrix(eval_cases, base_keys)
    x_te_f, _ = _design_matrix(eval_cases, full_keys)
    pred_b = _predict(beta_b, x_te_b)
    pred_f = _predict(beta_f, x_te_f)
    brier_b = _brier(y_te, pred_b)
    brier_f = _brier(y_te, pred_f)
    ratio = brier_f / brier_b if brier_b > 1e-12 else float("inf")
    return {
        "brier_base": brier_b,
        "brier_full": brier_f,
        "brier_ratio": ratio,
        "auc_base": _auc(y_te, pred_b),
        "auc_full": _auc(y_te, pred_f),
        "n_cases": len(eval_cases),
        "n_pos": int(sum(y_te)),
        "n_neg": int(len(y_te) - sum(y_te)),
        "beats_mcid": ratio <= MCID_BRIER_RATIO,
        "base_keys": list(base_keys),
        "full_keys": list(full_keys),
    }


def run_experiment_h4(*, peek_holdout_labels_in_train: bool = False) -> dict[str, Any]:
    """Y19-H4 — decompose size vs entropy with three locked gates."""
    prior = (
        set(TRAIN_SEEDS)
        | set(HOLD_SEEDS)
        | set(TRAIN_SEEDS_H2)
        | set(HOLD_SEEDS_H2)
        | set(TRAIN_SEEDS_H3)
        | set(HOLD_SEEDS_H3_MATCH)
        | set(HOLD_SEEDS_H3_UNSEEN)
    )
    if set(TRAIN_SEEDS_H4) & prior or set(HOLD_SEEDS_H4) & prior:
        raise RuntimeError("H4 seeds overlap prior Y19 missions")
    if set(TRAIN_SEEDS_H4) & set(HOLD_SEEDS_H4):
        raise RuntimeError("H4 train/hold collide")

    # Balanced N panel via chooser
    def n_chooser(seed: int) -> int:
        return N_PANEL_H4[seed % len(N_PANEL_H4)]

    train = _collect_cases(TRAIN_SEEDS_H4, n_chooser=n_chooser)
    hold = _collect_cases(HOLD_SEEDS_H4, n_chooser=n_chooser)
    fit = train + hold if peek_holdout_labels_in_train else train

    # --- Gate A: N-matched (within each N, activity+entropy vs activity) ---
    n_rows: list[dict[str, Any]] = []
    for nval in N_PANEL_H4:
        fit_n = [c for c in fit if int(c["n"]) == nval]
        hold_n = [c for c in hold if int(c["n"]) == nval]
        if not fit_n or not hold_n:
            n_rows.append({"n": nval, "status": "EMPTY", "powered": False, "passed": False})
            continue
        metrics = _eval_keys_vs(
            fit_n, hold_n, base_keys=ACTIVITY_KEYS_H4, full_keys=ACTIVITY_ENTROPY_KEYS
        )
        powered = _stratum_ok(metrics["n_pos"], metrics["n_neg"], metrics["n_cases"])
        n_rows.append(
            {
                "n": nval,
                "status": "OK" if powered else "UNDERPOWERED",
                "powered": powered,
                "passed": bool(powered and metrics["beats_mcid"]),
                **metrics,
            }
        )
    powered_n = [r for r in n_rows if r.get("powered")]
    if len(powered_n) < 2:
        gate_a: dict[str, Any] = {
            "name": "n_matched",
            "status": "UNDERPOWERED",
            "passed": False,
            "by_n": n_rows,
        }
    else:
        n_pass = sum(1 for r in powered_n if r["beats_mcid"])
        gate_a = {
            "name": "n_matched",
            "status": "PASS" if n_pass >= 2 else "FAIL",
            "passed": n_pass >= 2,
            "powered_n": len(powered_n),
            "mcid_pass_n": n_pass,
            "by_n": n_rows,
        }

    # --- Gate B: residualized entropy ---
    fit_r, hold_r = _with_residual_entropy(fit, hold)
    residual_keys = ACTIVITY_KEYS_H4 + ("residual_entropy",)
    gate_b_metrics = _eval_keys_vs(
        fit_r, hold_r, base_keys=ACTIVITY_KEYS_H4, full_keys=residual_keys
    )
    # Also report activity+N vs activity+N+entropy (nested control)
    nested = _eval_keys_vs(
        fit, hold, base_keys=ACTIVITY_N_KEYS, full_keys=ACTIVITY_N_ENTROPY_KEYS
    )
    bal_b = (
        gate_b_metrics["n_pos"] >= MIN_HOLD_POSITIVES
        and gate_b_metrics["n_neg"] >= MIN_HOLD_NEGATIVES
    )
    if not bal_b:
        gate_b = {
            "name": "residualized_entropy",
            "status": "UNDERPOWERED",
            "passed": False,
            **gate_b_metrics,
            "nested_activity_n_vs_plus_entropy": nested,
        }
    else:
        # Pass only if residual entropy beats activity AND nested entropy adds beyond N
        passed_b = bool(gate_b_metrics["beats_mcid"] and nested["beats_mcid"])
        gate_b = {
            "name": "residualized_entropy",
            "status": "PASS" if passed_b else "FAIL",
            "passed": passed_b,
            **gate_b_metrics,
            "nested_activity_n_vs_plus_entropy": nested,
        }

    # --- Gate C: leave-one-N-out ---
    loo_rows: list[dict[str, Any]] = []
    for held_n in N_PANEL_H4:
        fit_loo = [c for c in fit if int(c["n"]) != held_n]
        hold_loo = [c for c in hold if int(c["n"]) == held_n]
        if not fit_loo or not hold_loo:
            loo_rows.append({"held_n": held_n, "status": "EMPTY", "powered": False, "passed": False})
            continue
        metrics = _eval_keys_vs(
            fit_loo,
            hold_loo,
            base_keys=ACTIVITY_KEYS_H4,
            full_keys=ACTIVITY_ENTROPY_KEYS,
        )
        powered = _stratum_ok(metrics["n_pos"], metrics["n_neg"], metrics["n_cases"])
        loo_rows.append(
            {
                "held_n": held_n,
                "status": "OK" if powered else "UNDERPOWERED",
                "powered": powered,
                "passed": bool(powered and metrics["beats_mcid"]),
                **metrics,
            }
        )
    powered_loo = [r for r in loo_rows if r.get("powered")]
    if len(powered_loo) < 2:
        gate_c: dict[str, Any] = {
            "name": "leave_one_n_out",
            "status": "UNDERPOWERED",
            "passed": False,
            "folds": loo_rows,
        }
    else:
        n_pass = sum(1 for r in powered_loo if r["beats_mcid"])
        # PASS if ≥2 folds keep entropy MCID (transferable entropy, not N lookup)
        gate_c = {
            "name": "leave_one_n_out",
            "status": "PASS" if n_pass >= 2 else "FAIL",
            "passed": n_pass >= 2,
            "powered_folds": len(powered_loo),
            "mcid_pass_folds": n_pass,
            "folds": loo_rows,
        }

    gates = {
        "A_n_matched": gate_a,
        "B_residualized_entropy": gate_b,
        "C_leave_one_n_out": gate_c,
    }
    statuses = [g["status"] for g in gates.values()]

    if any(s == "FAIL" for s in statuses):
        # Mixed: some pass some fail among powered gates
        pass_flags = [g.get("passed") for g in gates.values() if g["status"] in {"PASS", "FAIL"}]
        if pass_flags and any(pass_flags) and not all(pass_flags):
            decision: Decision = "INCONCLUSIVE"
            winning = "H_conditional_on_n"
        elif gate_a["status"] == "FAIL" or gate_b["status"] == "FAIL":
            decision = "REJECTED"
            winning = "H_effect_is_mostly_n"
        else:
            decision = "REJECTED"
            winning = "H_conditional_on_n"
    elif any(s == "UNDERPOWERED" for s in statuses):
        decision = "INCONCLUSIVE"
        winning = "H_conditional_on_n"
    elif all(g["passed"] for g in gates.values()):
        decision = "SUPPORTED"
        winning = "H_entropy_survives_n_control"
    else:
        decision = "INCONCLUSIVE"
        winning = "H_conditional_on_n"

    nulls: list[dict[str, Any]] = []
    if decision == "REJECTED":
        nulls.append(
            {
                "id": "y19_h4_entropy_dies_under_n_control",
                "gates": {k: v["status"] for k, v in gates.items()},
                "interpretation": "entropy did not retain MCID after N control / residualization / LOO",
            }
        )

    return {
        "protocol_version": PROTOCOL_VERSION_H4,
        "prior_mission": "Y19-H3",
        "prior_decision": "SUPPORTED",
        "competing_hypotheses": [asdict(h) for h in COMPETING_H4],
        "winning_hypothesis_id": winning,
        "decision": decision,
        "gates": gates,
        "mcid_brier_ratio": MCID_BRIER_RATIO,
        "claim_scope": (
            "At most: entropy retains OOS signal beyond activity under N controls — "
            "not a general transient theory"
        ),
        "seed_policy": {
            "train": f"{TRAIN_SEEDS_H4[0]}-{TRAIN_SEEDS_H4[-1]}",
            "hold": f"{HOLD_SEEDS_H4[0]}-{HOLD_SEEDS_H4[-1]}",
            "n_panel": list(N_PANEL_H4),
            "disjoint_from_h1_h2_h3": True,
        },
        "leak_checks": {
            "train_hold_disjoint": True,
            "peek_holdout_labels_in_train": peek_holdout_labels_in_train,
        },
        "null_results": nulls,
        "scientific_claim_accepted": decision == "SUPPORTED",
        "answer_known_a_priori": False,
    }


def write_preregistration_h4(path: Path) -> None:
    payload = {
        "mission_id": "Y19-H4",
        "protocol_version": PROTOCOL_VERSION_H4,
        "preregistered_before_data": True,
        "follows": "Y19-H3 SUPPORTED → decompose size vs entropy",
        "hypothesis": COMPETING_H4[0].statement,
        "competing_hypotheses": [asdict(h) for h in COMPETING_H4],
        "gates": {
            "A_n_matched": "Within each N, activity+entropy vs activity; ≥2 powered N pass MCID",
            "B_residualized_entropy": (
                "residual_entropy = entropy - E[entropy|N,activity]; "
                "activity+residual vs activity MCID AND nested activity+N+entropy vs activity+N MCID"
            ),
            "C_leave_one_n_out": "Train other N, hold one N; ≥2 folds keep entropy MCID",
        },
        "primary_criterion": {
            "statistic": "all_three_decomposition_gates_pass",
            "mcid_ratio": MCID_BRIER_RATIO,
            "decision_rule": {
                "SUPPORTED": "A and B and C PASS",
                "REJECTED": "A or B FAIL (entropy dies under N control)",
                "INCONCLUSIVE": "mixed PASS/FAIL or UNDERPOWERED",
            },
        },
        "seed_data_policy": {
            "train": list(TRAIN_SEEDS_H4),
            "hold": list(HOLD_SEEDS_H4),
            "n_panel": list(N_PANEL_H4),
        },
        "forbidden": [
            "new spectral/sensitivity features",
            "post-hoc MCID change",
            "claiming entropy predicts transients without N-control survival",
        ],
        "answer_known_a_priori": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# --- Y19-H5: why does N predict long transients? ---
PROTOCOL_VERSION_H5 = "Y19-H5-v1"
TRAIN_SEEDS_H5 = tuple(range(9000, 9300))  # 300
HOLD_SEEDS_H5 = tuple(range(11000, 11150))  # 150
N_PANEL_H5 = (16, 20, 24)
N_PROBE_ICS = 8  # extra ICs per net (not the labeled IC)
ALT_TAU = 20  # protocol ablation label threshold
STRUCTURAL_KEYS = (
    "mean_probe_transient",
    "mean_probe_period",
    "probe_long_fraction",
    "probe_transient_std",
)
N_KEYS = ("n",)
LOGN_KEYS = ("log2_n",)
ACTIVITY_PLUS_N = ACTIVITY_KEYS + ("n",)

COMPETING_H5: tuple[CompetingHypothesis, ...] = (
    CompetingHypothesis(
        id="H5a_state_space_n",
        statement=(
            "Long-transient labels rise with N via state-space growth; raw N (or log2 N) "
            "dominates sealed-holdout prediction and structural extras fail N-matched tests."
        ),
    ),
    CompetingHypothesis(
        id="H5b_basin_cycle_structure",
        statement=(
            "Attractor/basin/cycle probe statistics (not raw N) carry the signal and beat "
            "N on sealed holdout, including within-N matched checks."
        ),
    ),
    CompetingHypothesis(
        id="H5d_protocol_artifact",
        statement=(
            "The N→label association is an artifact of τ / single-IC sampling; alternate "
            "protocol ablates the sealed-holdout N advantage."
        ),
    ),
)


def _probe_network_stats(net: dict[str, Any], *, label_ic_seed: int) -> dict[str, float]:
    """Multi-IC probes of the network — must not use the labeled IC outcome as a feature."""
    transients: list[float] = []
    periods: list[float] = []
    longs = 0
    for i in range(N_PROBE_ICS):
        probe_ic = label_ic_seed + 1009 * (i + 1) + 17
        sim = _simulate(net, ic_seed=probe_ic)
        transients.append(float(sim["steps_to_attractor"]))
        periods.append(float(sim["period"]))
        longs += int(sim["steps_to_attractor"] > LONG_TRANSIENT_TAU)
    mean_t = sum(transients) / len(transients)
    var_t = sum((x - mean_t) ** 2 for x in transients) / len(transients)
    return {
        "mean_probe_transient": mean_t,
        "mean_probe_period": sum(periods) / len(periods),
        "probe_long_fraction": longs / len(transients),
        "probe_transient_std": math.sqrt(var_t),
    }


def _collect_cases_h5(
    seeds: tuple[int, ...],
    *,
    tau: int = LONG_TRANSIENT_TAU,
) -> list[dict[str, Any]]:
    def n_chooser(seed: int) -> int:
        return N_PANEL_H5[seed % len(N_PANEL_H5)]

    cases: list[dict[str, Any]] = []
    for seed in seeds:
        n_use = n_chooser(seed)
        net = _generate_network(seed, n=n_use)
        label_ic = seed * 17 + 3
        sim = _simulate(net, ic_seed=label_ic)
        # Relabel under protocol tau without touching structural probes
        label = int(sim["steps_to_attractor"] > tau)
        feats = _features(sim, net)
        feats["log2_n"] = math.log2(float(sim["n"]))
        feats.update(_probe_network_stats(net, label_ic_seed=label_ic))
        cases.append(
            {
                "network_seed": seed,
                "label": label,
                "steps_to_attractor": sim["steps_to_attractor"],
                "features": feats,
                "n": sim["n"],
                "k": sim["k"],
            }
        )
    return cases


def run_experiment_h5(*, peek_holdout_labels_in_train: bool = False) -> dict[str, Any]:
    """Y19-H5 — why N? structural probes vs raw N vs protocol artifact."""
    prior = (
        set(TRAIN_SEEDS)
        | set(HOLD_SEEDS)
        | set(TRAIN_SEEDS_H2)
        | set(HOLD_SEEDS_H2)
        | set(TRAIN_SEEDS_H3)
        | set(HOLD_SEEDS_H3_MATCH)
        | set(HOLD_SEEDS_H3_UNSEEN)
        | set(TRAIN_SEEDS_H4)
        | set(HOLD_SEEDS_H4)
    )
    if set(TRAIN_SEEDS_H5) & prior or set(HOLD_SEEDS_H5) & prior:
        raise RuntimeError("H5 seeds overlap prior Y19 missions")

    train = _collect_cases_h5(TRAIN_SEEDS_H5)
    hold = _collect_cases_h5(HOLD_SEEDS_H5)
    fit = train + hold if peek_holdout_labels_in_train else train

    # Gate 1: structural probes vs raw N
    g1 = _eval_keys_vs(fit, hold, base_keys=N_KEYS, full_keys=STRUCTURAL_KEYS)
    g1_log = _eval_keys_vs(fit, hold, base_keys=LOGN_KEYS, full_keys=STRUCTURAL_KEYS)
    bal1 = g1["n_pos"] >= MIN_HOLD_POSITIVES and g1["n_neg"] >= MIN_HOLD_NEGATIVES
    if not bal1:
        gate1: dict[str, Any] = {
            "name": "structural_vs_n",
            "status": "UNDERPOWERED",
            "passed": False,
            **g1,
            "vs_log2_n": g1_log,
        }
    else:
        # PASS (= favors H5b) if structural beats both n and log2_n by MCID
        passed1 = bool(g1["beats_mcid"] and g1_log["beats_mcid"])
        gate1 = {
            "name": "structural_vs_n",
            "status": "PASS" if passed1 else "FAIL",
            "passed": passed1,
            **g1,
            "vs_log2_n": g1_log,
        }

    # Gate 2: N-matched — within each N, structural vs activity
    n_rows: list[dict[str, Any]] = []
    for nval in N_PANEL_H5:
        fit_n = [c for c in fit if int(c["n"]) == nval]
        hold_n = [c for c in hold if int(c["n"]) == nval]
        if not fit_n or not hold_n:
            n_rows.append({"n": nval, "status": "EMPTY", "powered": False, "passed": False})
            continue
        metrics = _eval_keys_vs(
            fit_n, hold_n, base_keys=ACTIVITY_KEYS, full_keys=ACTIVITY_KEYS + STRUCTURAL_KEYS
        )
        powered = _stratum_ok(metrics["n_pos"], metrics["n_neg"], metrics["n_cases"])
        n_rows.append(
            {
                "n": nval,
                "status": "OK" if powered else "UNDERPOWERED",
                "powered": powered,
                "passed": bool(powered and metrics["beats_mcid"]),
                **metrics,
            }
        )
    powered_n = [r for r in n_rows if r.get("powered")]
    if len(powered_n) < 2:
        gate2: dict[str, Any] = {
            "name": "n_matched_structural",
            "status": "UNDERPOWERED",
            "passed": False,
            "by_n": n_rows,
        }
    else:
        n_pass = sum(1 for r in powered_n if r["beats_mcid"])
        gate2 = {
            "name": "n_matched_structural",
            "status": "PASS" if n_pass >= 2 else "FAIL",
            "passed": n_pass >= 2,
            "powered_n": len(powered_n),
            "mcid_pass_n": n_pass,
            "by_n": n_rows,
        }

    # Gate 3: protocol ablation — under ALT_TAU, does n still beat activity by MCID?
    train_alt = _collect_cases_h5(TRAIN_SEEDS_H5, tau=ALT_TAU)
    hold_alt = _collect_cases_h5(HOLD_SEEDS_H5, tau=ALT_TAU)
    fit_alt = train_alt + hold_alt if peek_holdout_labels_in_train else train_alt
    g3 = _eval_keys_vs(fit_alt, hold_alt, base_keys=ACTIVITY_KEYS, full_keys=ACTIVITY_PLUS_N)
    bal3 = g3["n_pos"] >= MIN_HOLD_POSITIVES and g3["n_neg"] >= MIN_HOLD_NEGATIVES
    # Association "survives" if N still improves over activity under alt protocol
    if not bal3:
        gate3: dict[str, Any] = {
            "name": "protocol_ablation_alt_tau",
            "status": "UNDERPOWERED",
            "passed": False,
            "alt_tau": ALT_TAU,
            **g3,
        }
        n_association_survives = False
    else:
        n_association_survives = bool(g3["beats_mcid"])
        # PASS gate3 means "ablation failed to kill N" i.e. NOT H5d.
        # For decision logic we store survival explicitly.
        gate3 = {
            "name": "protocol_ablation_alt_tau",
            "status": "PASS" if n_association_survives else "FAIL",
            "passed": n_association_survives,
            "alt_tau": ALT_TAU,
            "n_association_survives": n_association_survives,
            **g3,
        }

    # Also: under default tau, confirm N beats activity (sanity / H5a substrate)
    g_n_vs_act = _eval_keys_vs(fit, hold, base_keys=ACTIVITY_KEYS, full_keys=ACTIVITY_PLUS_N)
    n_beats_activity_default = bool(g_n_vs_act.get("beats_mcid"))

    gates = {
        "A_structural_vs_n": gate1,
        "B_n_matched_structural": gate2,
        "C_protocol_ablation": gate3,
    }

    # Decision (triage order: structure first; H5d only if default-N exists then dies)
    if gate1["status"] == "UNDERPOWERED" or gate2["status"] == "UNDERPOWERED":
        decision: Decision = "INCONCLUSIVE"
        winning = "H5b_basin_cycle_structure"
    elif gate1["passed"] and gate2["passed"]:
        decision = "SUPPORTED"
        winning = "H5b_basin_cycle_structure"
    elif (
        n_beats_activity_default
        and gate3["status"] == "FAIL"
        and not n_association_survives
    ):
        # Raw N helped under default τ but not under alt τ → protocol artifact
        decision = "SUPPORTED"
        winning = "H5d_protocol_artifact"
    elif (
        (not gate1["passed"])
        and (not gate2["passed"])
        and n_beats_activity_default
        and n_association_survives
    ):
        decision = "SUPPORTED"
        winning = "H5a_state_space_n"
    elif gate1["passed"] ^ gate2["passed"]:
        decision = "INCONCLUSIVE"
        winning = "H5b_basin_cycle_structure"
    else:
        decision = "INCONCLUSIVE"
        winning = "H5a_state_space_n"

    nulls: list[dict[str, Any]] = []
    if winning == "H5a_state_space_n" and decision == "SUPPORTED":
        nulls.append(
            {
                "id": "y19_h5_structural_fail_vs_n",
                "interpretation": "probe structural features failed to beat N / N-matched activity",
            }
        )
    if winning == "H5d_protocol_artifact" and decision == "SUPPORTED":
        nulls.append(
            {
                "id": "y19_h5_protocol_ablation",
                "alt_tau": ALT_TAU,
                "interpretation": "N→label MCID vs activity disappears under alternate τ",
            }
        )
    if decision == "INCONCLUSIVE" and not n_beats_activity_default:
        nulls.append(
            {
                "id": "y19_h5_raw_n_weak_vs_activity",
                "brier_ratio": g_n_vs_act.get("brier_ratio"),
                "interpretation": (
                    "raw n alone does not beat activity by MCID on this split; "
                    "H2/H4 'size' signal is not identical to univariate n"
                ),
            }
        )

    return {
        "protocol_version": PROTOCOL_VERSION_H5,
        "prior_mission": "Y19-H4",
        "prior_decision": "REJECTED",
        "competing_hypotheses": [asdict(h) for h in COMPETING_H5],
        "winning_hypothesis_id": winning,
        "decision": decision,
        "gates": gates,
        "sanity_n_vs_activity_default_tau": g_n_vs_act,
        "mcid_brier_ratio": MCID_BRIER_RATIO,
        "n_probe_ics": N_PROBE_ICS,
        "claim_scope": (
            "Mechanism sketch for why N predicts long-transient labels in this family — "
            "not a universal transient theory"
        ),
        "seed_policy": {
            "train": f"{TRAIN_SEEDS_H5[0]}-{TRAIN_SEEDS_H5[-1]}",
            "hold": f"{HOLD_SEEDS_H5[0]}-{HOLD_SEEDS_H5[-1]}",
            "n_panel": list(N_PANEL_H5),
            "disjoint_from_h1_h4": True,
        },
        "leak_checks": {
            "train_hold_disjoint": True,
            "peek_holdout_labels_in_train": peek_holdout_labels_in_train,
            "structural_uses_labeled_ic_outcome": False,
        },
        "null_results": nulls,
        "scientific_claim_accepted": decision == "SUPPORTED",
        "answer_known_a_priori": False,
    }


def write_preregistration_h5(path: Path) -> None:
    payload = {
        "mission_id": "Y19-H5",
        "protocol_version": PROTOCOL_VERSION_H5,
        "preregistered_before_data": True,
        "follows": "Y19-H4 REJECTED → mostly N → why N?",
        "hypothesis": COMPETING_H5[0].statement,
        "competing_hypotheses": [asdict(h) for h in COMPETING_H5],
        "gates": {
            "A_structural_vs_n": "Probe basin/cycle stats beat n and log2_n by MCID",
            "B_n_matched_structural": "Within ≥2 N values, structural beats activity by MCID",
            "C_protocol_ablation": f"Under τ={ALT_TAU}, n still beats activity by MCID (survival)",
        },
        "primary_criterion": {
            "statistic": "h5_mechanism_triage",
            "mcid_ratio": MCID_BRIER_RATIO,
            "decision_rule": {
                "SUPPORTED_H5b": "A and B PASS and C survival",
                "SUPPORTED_H5a": "A and B FAIL and C survival",
                "SUPPORTED_H5d": "C FAIL (N association dies under alt τ)",
                "INCONCLUSIVE": "mixed or underpowered",
            },
        },
        "seed_data_policy": {
            "train": list(TRAIN_SEEDS_H5),
            "hold": list(HOLD_SEEDS_H5),
            "n_panel": list(N_PANEL_H5),
        },
        "leak_forbidden": [
            "using labeled IC steps_to_attractor as a predictive feature",
            "post-hoc τ/MCID change after holdout",
        ],
        "answer_known_a_priori": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# --- Y19-H6: ablate structural probes (after H5b) ---
PROTOCOL_VERSION_H6 = "Y19-H6-v1"
TRAIN_SEEDS_H6 = tuple(range(12000, 12300))
HOLD_SEEDS_H6 = tuple(range(13000, 13150))
MEAN_TRANSIENT_KEYS = ("mean_probe_transient",)
PERIOD_KEYS = ("mean_probe_period", "probe_long_fraction", "probe_transient_std")

COMPETING_H6: tuple[CompetingHypothesis, ...] = (
    CompetingHypothesis(
        id="H6a_mean_transient_propensity",
        statement=(
            "Structural win is carried by mean_probe_transient (network long-transient "
            "propensity); period/fraction extras fail once mean transient is controlled."
        ),
    ),
    CompetingHypothesis(
        id="H6b_period_structure_beyond_propensity",
        statement=(
            "Attractor period / long-fraction structure retains MCID beyond mean probe "
            "transient propensity on sealed holdout."
        ),
    ),
    CompetingHypothesis(
        id="H6c_underpowered_or_mixed",
        statement="Ablation gates are mixed or underpowered; carrier within structural set unresolved.",
    ),
)


def run_experiment_h6(*, peek_holdout_labels_in_train: bool = False) -> dict[str, Any]:
    prior = (
        set(TRAIN_SEEDS)
        | set(HOLD_SEEDS)
        | set(TRAIN_SEEDS_H2)
        | set(HOLD_SEEDS_H2)
        | set(TRAIN_SEEDS_H3)
        | set(HOLD_SEEDS_H3_MATCH)
        | set(HOLD_SEEDS_H3_UNSEEN)
        | set(TRAIN_SEEDS_H4)
        | set(HOLD_SEEDS_H4)
        | set(TRAIN_SEEDS_H5)
        | set(HOLD_SEEDS_H5)
    )
    if set(TRAIN_SEEDS_H6) & prior or set(HOLD_SEEDS_H6) & prior:
        raise RuntimeError("H6 seeds overlap prior Y19")

    train = _collect_cases_h5(TRAIN_SEEDS_H6)
    hold = _collect_cases_h5(HOLD_SEEDS_H6)
    fit = train + hold if peek_holdout_labels_in_train else train

    # Gate A: mean_probe_transient vs N
    g_a = _eval_keys_vs(fit, hold, base_keys=N_KEYS, full_keys=MEAN_TRANSIENT_KEYS)
    # Gate B: period-set vs N
    g_b = _eval_keys_vs(fit, hold, base_keys=N_KEYS, full_keys=PERIOD_KEYS)
    # Gate C: period-set vs mean_probe_transient (does period beat propensity?)
    g_c = _eval_keys_vs(fit, hold, base_keys=MEAN_TRANSIENT_KEYS, full_keys=PERIOD_KEYS)
    # Gate D: full structural vs mean alone
    g_d = _eval_keys_vs(
        fit, hold, base_keys=MEAN_TRANSIENT_KEYS, full_keys=STRUCTURAL_KEYS
    )

    def gate(name: str, metrics: dict[str, Any]) -> dict[str, Any]:
        bal = metrics["n_pos"] >= MIN_HOLD_POSITIVES and metrics["n_neg"] >= MIN_HOLD_NEGATIVES
        if not bal:
            return {"name": name, "status": "UNDERPOWERED", "passed": False, **metrics}
        return {
            "name": name,
            "status": "PASS" if metrics["beats_mcid"] else "FAIL",
            "passed": bool(metrics["beats_mcid"]),
            **metrics,
        }

    gates = {
        "A_mean_transient_vs_n": gate("mean_transient_vs_n", g_a),
        "B_period_set_vs_n": gate("period_set_vs_n", g_b),
        "C_period_vs_mean_transient": gate("period_vs_mean_transient", g_c),
        "D_full_structural_vs_mean": gate("full_structural_vs_mean", g_d),
    }

    if any(g["status"] == "UNDERPOWERED" for g in gates.values()):
        decision: Decision = "INCONCLUSIVE"
        winning = "H6c_underpowered_or_mixed"
    elif gates["A_mean_transient_vs_n"]["passed"] and (
        not gates["C_period_vs_mean_transient"]["passed"]
        and not gates["D_full_structural_vs_mean"]["passed"]
    ):
        decision = "SUPPORTED"
        winning = "H6a_mean_transient_propensity"
    elif gates["C_period_vs_mean_transient"]["passed"] or (
        gates["B_period_set_vs_n"]["passed"] and gates["D_full_structural_vs_mean"]["passed"]
    ):
        decision = "SUPPORTED"
        winning = "H6b_period_structure_beyond_propensity"
    elif gates["A_mean_transient_vs_n"]["passed"]:
        decision = "SUPPORTED"
        winning = "H6a_mean_transient_propensity"
    else:
        decision = "INCONCLUSIVE"
        winning = "H6c_underpowered_or_mixed"

    nulls: list[dict[str, Any]] = []
    if winning == "H6a_mean_transient_propensity":
        nulls.append(
            {
                "id": "y19_h6_period_fails_beyond_mean_transient",
                "interpretation": "period/fraction extras do not beat mean probe transient by MCID",
            }
        )

    return {
        "protocol_version": PROTOCOL_VERSION_H6,
        "prior_mission": "Y19-H5",
        "prior_decision": "SUPPORTED",
        "competing_hypotheses": [asdict(h) for h in COMPETING_H6],
        "winning_hypothesis_id": winning,
        "decision": decision,
        "gates": gates,
        "mcid_brier_ratio": MCID_BRIER_RATIO,
        "claim_scope": (
            "Which structural probe carries H5b — propensity vs period structure"
        ),
        "seed_policy": {
            "train": f"{TRAIN_SEEDS_H6[0]}-{TRAIN_SEEDS_H6[-1]}",
            "hold": f"{HOLD_SEEDS_H6[0]}-{HOLD_SEEDS_H6[-1]}",
            "disjoint_from_prior": True,
        },
        "leak_checks": {
            "train_hold_disjoint": True,
            "peek_holdout_labels_in_train": peek_holdout_labels_in_train,
            "structural_uses_labeled_ic_outcome": False,
        },
        "null_results": nulls,
        "scientific_claim_accepted": decision == "SUPPORTED",
        "answer_known_a_priori": False,
    }


def write_preregistration_h6(path: Path) -> None:
    payload = {
        "mission_id": "Y19-H6",
        "protocol_version": PROTOCOL_VERSION_H6,
        "preregistered_before_data": True,
        "follows": "Y19-H5 SUPPORTED H5b → ablate structural probes",
        "hypothesis": COMPETING_H6[0].statement,
        "competing_hypotheses": [asdict(h) for h in COMPETING_H6],
        "primary_criterion": {
            "statistic": "h6_structural_ablation",
            "mcid_ratio": MCID_BRIER_RATIO,
        },
        "seed_data_policy": {
            "train": list(TRAIN_SEEDS_H6),
            "hold": list(HOLD_SEEDS_H6),
        },
        "answer_known_a_priori": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# --- Y19-H7: leave-one-N-out transfer of period structure ---
PROTOCOL_VERSION_H7 = "Y19-H7-v1"
TRAIN_SEEDS_H7 = tuple(range(14000, 14300))
HOLD_SEEDS_H7 = tuple(range(15000, 15150))

COMPETING_H7: tuple[CompetingHypothesis, ...] = (
    CompetingHypothesis(
        id="H7a_period_transfers_across_n",
        statement=(
            "Period/long-fraction structural features retain MCID vs N under leave-one-N-out "
            "on ≥2 held-out sizes."
        ),
    ),
    CompetingHypothesis(
        id="H7b_period_n_local",
        statement="Period structure fails leave-one-N-out transfer; effect is N-local.",
    ),
    CompetingHypothesis(
        id="H7c_underpowered",
        statement="LOO folds underpowered.",
    ),
)


def run_experiment_h7(*, peek_holdout_labels_in_train: bool = False) -> dict[str, Any]:
    prior = (
        set(TRAIN_SEEDS)
        | set(HOLD_SEEDS)
        | set(TRAIN_SEEDS_H2)
        | set(HOLD_SEEDS_H2)
        | set(TRAIN_SEEDS_H3)
        | set(HOLD_SEEDS_H3_MATCH)
        | set(HOLD_SEEDS_H3_UNSEEN)
        | set(TRAIN_SEEDS_H4)
        | set(HOLD_SEEDS_H4)
        | set(TRAIN_SEEDS_H5)
        | set(HOLD_SEEDS_H5)
        | set(TRAIN_SEEDS_H6)
        | set(HOLD_SEEDS_H6)
    )
    if set(TRAIN_SEEDS_H7) & prior or set(HOLD_SEEDS_H7) & prior:
        raise RuntimeError("H7 seeds overlap prior Y19")

    train = _collect_cases_h5(TRAIN_SEEDS_H7)
    hold = _collect_cases_h5(HOLD_SEEDS_H7)
    fit = train + hold if peek_holdout_labels_in_train else train

    folds: list[dict[str, Any]] = []
    for held_n in N_PANEL_H5:
        fit_loo = [c for c in fit if int(c["n"]) != held_n]
        hold_loo = [c for c in hold if int(c["n"]) == held_n]
        if not fit_loo or not hold_loo:
            folds.append({"held_n": held_n, "status": "EMPTY", "powered": False, "passed": False})
            continue
        metrics = _eval_keys_vs(fit_loo, hold_loo, base_keys=N_KEYS, full_keys=PERIOD_KEYS)
        powered = _stratum_ok(metrics["n_pos"], metrics["n_neg"], metrics["n_cases"])
        folds.append(
            {
                "held_n": held_n,
                "status": "OK" if powered else "UNDERPOWERED",
                "powered": powered,
                "passed": bool(powered and metrics["beats_mcid"]),
                **metrics,
            }
        )
    powered_folds = [f for f in folds if f.get("powered")]
    if len(powered_folds) < 2:
        decision: Decision = "INCONCLUSIVE"
        winning = "H7c_underpowered"
        status = "UNDERPOWERED"
        passed = False
    else:
        n_pass = sum(1 for f in powered_folds if f["beats_mcid"])
        passed = n_pass >= 2
        status = "PASS" if passed else "FAIL"
        if passed:
            decision = "SUPPORTED"
            winning = "H7a_period_transfers_across_n"
        else:
            decision = "REJECTED"
            winning = "H7b_period_n_local"

    nulls: list[dict[str, Any]] = []
    if decision == "REJECTED":
        nulls.append(
            {
                "id": "y19_h7_loo_fail",
                "folds": {f["held_n"]: f.get("brier_ratio") for f in folds},
                "interpretation": "period structure failed leave-one-N-out vs N",
            }
        )

    return {
        "protocol_version": PROTOCOL_VERSION_H7,
        "prior_mission": "Y19-H6",
        "prior_decision": "SUPPORTED",
        "competing_hypotheses": [asdict(h) for h in COMPETING_H7],
        "winning_hypothesis_id": winning,
        "decision": decision,
        "gates": {"leave_one_n_out_period_vs_n": {"status": status, "passed": passed, "folds": folds}},
        "mcid_brier_ratio": MCID_BRIER_RATIO,
        "seed_policy": {
            "train": f"{TRAIN_SEEDS_H7[0]}-{TRAIN_SEEDS_H7[-1]}",
            "hold": f"{HOLD_SEEDS_H7[0]}-{HOLD_SEEDS_H7[-1]}",
        },
        "leak_checks": {
            "train_hold_disjoint": True,
            "peek_holdout_labels_in_train": peek_holdout_labels_in_train,
            "structural_uses_labeled_ic_outcome": False,
        },
        "null_results": nulls,
        "scientific_claim_accepted": decision == "SUPPORTED",
        "answer_known_a_priori": False,
    }
