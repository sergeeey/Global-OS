"""EW1: coupled logistic lattice — generate, seal, score (stdlib+numpy)."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "external" / "EW1_transient_predictor"
EXAM = ROOT / "artifacts" / "external" / "M_EXT2_EW1_EXAM"

W = 8
TAU = 40
T_MAX = 160
R_LO, R_HI = 3.7, 3.9
EPS_LO, EPS_HI = 0.05, 0.2
N_VALUES = (16, 24)
TRAIN = range(1000, 1300)  # 1000..1299
HOLDOUT = range(9000, 9150)  # 9000..9149
MCID_RATIO = 0.9
RIDGE_L2 = 1.0


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _params(seed: int) -> tuple[int, float, float]:
    g = _rng(seed)
    n = int(N_VALUES[int(g.integers(0, len(N_VALUES)))])
    r = float(g.uniform(R_LO, R_HI))
    eps = float(g.uniform(EPS_LO, EPS_HI))
    return n, r, eps


def simulate(seed: int) -> tuple[np.ndarray, dict]:
    n, r, eps = _params(seed)
    g = _rng(seed + 17)
    x = g.uniform(0.05, 0.95, size=n)
    traj = np.zeros((T_MAX, n), dtype=float)
    for t in range(T_MAX):
        traj[t] = x
        # coupled logistic: (1-eps)*f(x_i) + (eps/2)*(f(x_{i-1})+f(x_{i+1}))
        fx = r * x * (1.0 - x)
        x = (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))
        x = np.clip(x, 0.0, 1.0)
    meta = {"N": n, "r": r, "epsilon": eps, "seed": seed}
    return traj, meta


def permutation_entropy(series: np.ndarray, order: int = 3) -> float:
    if len(series) < order + 1:
        return 0.0
    counts: dict[tuple[int, ...], int] = {}
    for i in range(len(series) - order + 1):
        w = series[i : i + order]
        # rank pattern
        pattern = tuple(np.argsort(w, kind="stable").tolist())
        counts[pattern] = counts.get(pattern, 0) + 1
    total = sum(counts.values())
    ent = 0.0
    for c in counts.values():
        p = c / total
        ent -= p * math.log(p + 1e-15)
    return ent / math.log(math.factorial(order))


def spectral_high_energy(series: np.ndarray) -> float:
    if len(series) < 4:
        return 0.0
    s = series - series.mean()
    spec = np.abs(np.fft.rfft(s)) ** 2
    if spec.sum() <= 0:
        return 0.0
    mid = max(1, len(spec) // 2)
    return float(spec[mid:].sum() / spec.sum())


def label_long_chaotic(traj: np.ndarray) -> int:
    """1 if lattice fails to settle (spatial variance) within W+TAU steps."""
    # spatial variance per time
    svar = traj.var(axis=1)
    settle_thresh = 1e-4
    for t in range(W, T_MAX):
        if svar[t] < settle_thresh and svar[max(W, t - 3) : t + 1].mean() < settle_thresh:
            return 1 if (t - W) > TAU else 0
    return 1  # never settled → long/chaotic


def features(traj: np.ndarray, meta: dict) -> dict[str, float]:
    early = traj[:W]
    mean_field = early.mean(axis=1)
    dx = np.diff(early, axis=0)
    base = {
        "N": float(meta["N"]),
        "mean_x": float(early.mean()),
        "std_x": float(early.std()),
        "max_abs_dx": float(np.abs(dx).max()) if dx.size else 0.0,
    }
    # neighbor divergence proxy
    neigh = np.abs(early - np.roll(early, 1, axis=1)).mean()
    cand = {
        "permutation_entropy_early": float(permutation_entropy(mean_field)),
        "spectral_high_energy": float(spectral_high_energy(mean_field)),
        "local_divergence_proxy": float(neigh),
    }
    return {**base, **cand}


def build_rows(seeds: range) -> list[dict]:
    rows = []
    for seed in seeds:
        traj, meta = simulate(seed)
        y = label_long_chaotic(traj)
        feats = features(traj, meta)
        rows.append(
            {
                "seed": seed,
                "label": int(y),
                "meta": meta,
                "features": feats,
            }
        )
    return rows


@dataclass
class RidgeLP:
    weights: np.ndarray
    bias: float
    feature_names: list[str]
    means: np.ndarray
    scales: np.ndarray

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        zs = (X - self.means) / self.scales
        logits = zs @ self.weights + self.bias
        # stable sigmoid
        return 1.0 / (1.0 + np.exp(-np.clip(logits, -40, 40)))


def fit_ridge(rows: list[dict], names: list[str], l2: float = RIDGE_L2) -> RidgeLP:
    X = np.array([[r["features"][n] for n in names] for r in rows], dtype=float)
    y = np.array([r["label"] for r in rows], dtype=float)
    means = X.mean(axis=0)
    scales = X.std(axis=0)
    scales[scales < 1e-8] = 1.0
    Xs = (X - means) / scales
    # closed-form ridge: (X'X + l2 I)^{-1} X'y  with bias via augmented column
    ones = np.ones((Xs.shape[0], 1))
    Xa = np.hstack([Xs, ones])
    reg = l2 * np.eye(Xa.shape[1])
    reg[-1, -1] = 0.0  # don't shrink bias
    beta = np.linalg.solve(Xa.T @ Xa + reg, Xa.T @ y)
    return RidgeLP(
        weights=beta[:-1],
        bias=float(beta[-1]),
        feature_names=names,
        means=means,
        scales=scales,
    )


def brier(model: RidgeLP, rows: list[dict], names: list[str]) -> float:
    X = np.array([[r["features"][n] for n in names] for r in rows], dtype=float)
    y = np.array([r["label"] for r in rows], dtype=float)
    p = model.predict_proba(X)
    return float(np.mean((p - y) ** 2))


def _write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj, (dict, list)):
        path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        path.write_text(str(obj), encoding="utf-8")


def seal_and_score() -> dict:
    print("generating train…")
    train = build_rows(TRAIN)
    print("generating holdout…")
    hold = build_rows(HOLDOUT)

    def bal(rows: list[dict]) -> dict:
        pos = sum(1 for r in rows if r["label"] == 1)
        neg = len(rows) - pos
        return {"n": len(rows), "pos": pos, "neg": neg}

    train_bal, hold_bal = bal(train), bal(hold)
    print("balance", train_bal, hold_bal)

    # Public train (labels OK for training)
    _write(
        ART / "public" / "corpus_manifest.TRAIN.json",
        {
            "pack": "TRAIN",
            "protocol_id": "EW1-CTP-v1",
            "status": "POPULATED",
            "stats": train_bal,
            "rows": train,
        },
    )

    # Seal holdout BEFORE scoring
    sealed = {
        "pack": "HOLDOUT",
        "status": "FROZEN_UNSEEN",
        "protocol_id": "EW1-CTP-v1",
        "stats": hold_bal,
        "rows": hold,
        "frozen_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha256_of_sealed_bundle": "PENDING",
        "unsealed_for_execution": False,
    }
    payload = json.dumps(sealed, indent=2, sort_keys=True) + "\n"
    sha = hashlib.sha256(payload.encode()).hexdigest()
    sealed["sha256_of_sealed_bundle"] = sha
    payload = json.dumps(sealed, indent=2, sort_keys=True) + "\n"
    sha = hashlib.sha256(payload.encode()).hexdigest()
    sealed["sha256_of_sealed_bundle"] = sha
    _write(ART / "sealed" / "sealed_pack.json", sealed)
    _write(
        ART / "sealed" / "HOLDOUT_MANIFEST.json",
        {
            "pack": "HOLDOUT",
            "status": "FROZEN_UNSEEN",
            "protocol_id": "EW1-CTP-v1",
            "n": len(hold),
            "stats": hold_bal,
            "sha256_of_sealed_bundle": sha,
            "unsealed_for_execution": False,
        },
    )
    # Blind public holdout seeds only
    _write(
        ART / "public" / "corpus_manifest.HOLDOUT_BLIND.json",
        {
            "pack": "HOLDOUT_BLIND",
            "status": "BLIND_SEEDS_ONLY",
            "seeds": [r["seed"] for r in hold],
            "n": len(hold),
        },
    )

    # Fit on train only
    baseline_names = ["N", "mean_x", "std_x", "max_abs_dx"]
    candidate_names = baseline_names + [
        "permutation_entropy_early",
        "spectral_high_energy",
        "local_divergence_proxy",
    ]
    ablation_names = [n for n in candidate_names if n != "N"]

    m_base = fit_ridge(train, baseline_names)
    m_cand = fit_ridge(train, candidate_names)
    m_abl = fit_ridge(train, ablation_names)

    # Unseal for scoring (labels now used)
    sealed["status"] = "UNSEALED_FOR_EXECUTION"
    sealed["unsealed_for_execution"] = True
    sealed["unsealed_at_utc"] = datetime.now(UTC).isoformat()
    _write(ART / "sealed" / "sealed_pack.json", sealed)
    man = json.loads((ART / "sealed" / "HOLDOUT_MANIFEST.json").read_text(encoding="utf-8"))
    man["status"] = "UNSEALED_FOR_EXECUTION"
    man["unsealed_for_execution"] = True
    _write(ART / "sealed" / "HOLDOUT_MANIFEST.json", man)

    if hold_bal["pos"] < 12 or hold_bal["neg"] < 12:
        decision = {
            "verdict": "INCONCLUSIVE",
            "reasons": ["holdout_class_balance_underpowered"],
            "holdout_balance": hold_bal,
        }
    else:
        b_base = brier(m_base, hold, baseline_names)
        b_cand = brier(m_cand, hold, candidate_names)
        b_abl = brier(m_abl, hold, ablation_names)
        # ablation baseline without N
        m_base_abl = fit_ridge(train, [n for n in baseline_names if n != "N"])
        b_base_abl = brier(m_base_abl, hold, [n for n in baseline_names if n != "N"])
        primary_ok = b_cand <= MCID_RATIO * b_base
        # ablation MCID: candidate-without-N vs baseline-without-N
        abl_ok = b_abl <= MCID_RATIO * b_base_abl
        if primary_ok and abl_ok:
            verdict = "SUPPORTED"
            reasons = ["primary_and_ablation_mcid_met"]
        else:
            verdict = "REJECTED"
            reasons = []
            if not primary_ok:
                reasons.append(
                    f"primary_brier_ratio_{b_cand / b_base:.4f}_gt_{MCID_RATIO}"
                )
            if not abl_ok:
                reasons.append(
                    f"ablation_brier_ratio_{b_abl / max(b_base_abl, 1e-12):.4f}_gt_{MCID_RATIO}"
                )
        # hypothesis interpretation
        if verdict == "REJECTED" and (b_cand >= b_base * 0.99):
            hyp = "H_baseline_sufficient"
        elif verdict == "REJECTED" and primary_ok and not abl_ok:
            hyp = "H_size_spurious"
        elif verdict == "SUPPORTED":
            hyp = "H_early_complexity"
        else:
            hyp = "mixed_or_primary_fail"
        decision = {
            "verdict": verdict,
            "reasons": reasons,
            "winning_hypothesis_readout": hyp,
            "holdout_balance": hold_bal,
            "brier_baseline": b_base,
            "brier_candidate": b_cand,
            "brier_baseline_no_N": b_base_abl,
            "brier_candidate_no_N": b_abl,
            "primary_ratio": b_cand / b_base,
            "ablation_ratio": b_abl / max(b_base_abl, 1e-12),
            "mcid_ratio": MCID_RATIO,
            "gates": {"primary_ok": primary_ok, "ablation_ok": abl_ok},
        }

    score = {
        "protocol_id": "EW1-CTP-v1",
        "exam_id": "M-EXT2-EW1",
        "train_balance": train_bal,
        "sealed_sha256": sha,
        "decision": decision,
        "not_y19_reopen": True,
        "y24_y25_not_evidence": True,
        "gos_architecture_changed": False,
        "fidelity": "SIMULATED_LATTICE_V1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
    }
    _write(ART / "SCORE_RAW.json", score)
    _write(EXAM / "SCORE_RAW.json", score)

    md = f"""# EW1_DECISION — M-EXT2 Chaotic Transient Predictor

**Status:** `{decision["verdict"]}`  
**Protocol:** `EW1-CTP-v1`  
**Exam:** `M-EXT2-EW1`  
**Fidelity:** `SIMULATED_LATTICE_V1`

## Reasons

```text
{chr(10).join(decision.get("reasons") or [])}
```

## Metrics

```json
{json.dumps(decision, indent=2, sort_keys=True)}
```

## Explicit non-claims

- Not Y19 reopen / not Y19 evidence
- Not Trust Kernel / architecture promote
- Not live physical-system claim (simulated lattice)
- M-EXT1 urllib3 result not used as evidence here
"""
    (ART / "EW1_DECISION.md").write_text(md, encoding="utf-8")
    (EXAM / "EW1_DECISION.md").write_text(md, encoding="utf-8")

    # update prereg flags
    preg = json.loads((ART / "EW1-PREREG.json").read_text(encoding="utf-8"))
    preg["arms_started"] = True
    preg["holdout_status"] = "UNSEALED_FOR_EXECUTION"
    _write(ART / "EW1-PREREG.json", preg)
    _write(
        ART / "CURRENT_STATE.json",
        {
            "mission_id": "EW1",
            "exam_id": "M-EXT2-EW1",
            "protocol_id": "EW1-CTP-v1",
            "phase": "SCORED",
            "verdict": decision["verdict"],
            "arms_started": True,
            "holdout_status": "UNSEALED_FOR_EXECUTION",
            "updated_at_utc": datetime.now(UTC).isoformat(),
        },
    )
    return score


def main() -> int:
    score = seal_and_score()
    print(json.dumps({"ok": True, "verdict": score["decision"]["verdict"], "decision": score["decision"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
