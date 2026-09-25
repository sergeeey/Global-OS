"""LH-COGNITIVE probes — external-object research ticks (numpy/scipy; no sum-harness).

Locked object: Jain & Wallace 2019 attention≠explanation thesis (continuation of R2 class).
These probes are paper-analogue metrics, not novel science claims by themselves.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import stats  # type: ignore[import]

from global_os.common.hashing import content_hash

EXTERNAL_OBJECT_ID = "EXT-JAIN-WALLACE-2019-ATTN-EXPLAIN"
PRIMARY_CLAIM = (
    "Attention weights are frequently weakly correlated with feature-importance "
    "proxies; strongly altered attention can preserve predictions — attention "
    "should not be treated as explanation by default."
)


def locked_object_payload() -> dict[str, Any]:
    return {
        "object_id": EXTERNAL_OBJECT_ID,
        "arxiv": "1902.10186",
        "title": "Attention is not Explanation",
        "authors": ["Sarthak Jain", "Byron C. Wallace"],
        "venue": "NAACL 2019",
        "primary_claim": PRIMARY_CLAIM,
        "workload_class": "EXTERNAL_RESEARCH_OBJECT",
        "forbidden_primary_criterion": "sum(1..20)==210",
        "protocol": "LH-COGNITIVE-v1",
    }


def write_locked_object(root: Path) -> dict[str, Any]:
    payload = locked_object_payload()
    path = root / "LOCKED_OBJECT.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {**payload, "path": str(path), "content_hash": content_hash(payload)}


def claim_inventory(root: Path) -> dict[str, Any]:
    """C1 — inventory locked claims; hash must be stable for the freeze pack."""
    obj = write_locked_object(root / "object")
    claims = {
        "C1_attention_not_explanation": PRIMARY_CLAIM,
        "C2_pattern_across_settings": (
            "Association pattern reported across datasets/encoders/attention types in paper."
        ),
        "object_id": EXTERNAL_OBJECT_ID,
    }
    out = {
        "stage": "C1_claim_inventory",
        "claims": claims,
        "object_hash": obj["content_hash"],
        "claims_hash": content_hash(claims),
        "n_claims": len(claims) - 1,
    }
    _dump(root / "evidence" / "C1_claim_inventory.json", out)
    return out


def attention_importance_kendall(root: Path, *, seed: int, n: int, T: int = 32) -> dict[str, Any]:
    """C2 — Kendall τ between attention mass and a feature-importance proxy."""
    rng = np.random.default_rng(seed)
    # Simulate token importances (gradient-proxy) and attention distributions.
    importance = rng.normal(size=(n, T))
    # Attention partly aligned + noise (weak correlation regime — paper-analogue).
    attn_logits = 0.25 * importance + rng.normal(scale=1.0, size=(n, T))
    attn = _softmax(attn_logits)
    taus = []
    for i in range(n):
        tau, _ = stats.kendalltau(attn[i], importance[i])
        if not np.isnan(tau):
            taus.append(float(tau))
    median_tau = float(np.median(taus)) if taus else float("nan")
    # Preregistered interpretative threshold (not a paper replication claim):
    # median |τ| often modest under noisy alignment.
    weak = abs(median_tau) < 0.5
    out = {
        "stage": "C2_attention_importance_kendall",
        "object_id": EXTERNAL_OBJECT_ID,
        "seed": seed,
        "n": n,
        "T": T,
        "median_kendall_tau": median_tau,
        "mean_kendall_tau": float(np.mean(taus)) if taus else float("nan"),
        "frac_abs_tau_lt_0_5": float(np.mean(np.abs(taus) < 0.5)) if taus else float("nan"),
        "decision_hint": "WEAK_ASSOCIATION" if weak else "NONWEAK_ASSOCIATION",
        "evidence_hash": "",
    }
    out["evidence_hash"] = content_hash(out)
    _dump(root / "evidence" / f"C2_kendall_seed{seed}_n{n}.json", out)
    return out


def underpowered_null_probe(root: Path, *, seed: int) -> dict[str, Any]:
    """C3 — deliberately tiny N → inconclusive/NULL retained (not discarded)."""
    rng = np.random.default_rng(seed)
    n = 4  # intentionally underpowered
    a = rng.normal(size=n)
    b = rng.normal(size=n)
    tau, p = stats.kendalltau(a, b)
    out = {
        "stage": "C3_underpowered_null",
        "object_id": EXTERNAL_OBJECT_ID,
        "n": n,
        "kendall_tau": None if tau is None or np.isnan(tau) else float(tau),
        "p_value": None if p is None or np.isnan(p) else float(p),
        "decision": "NULL_INCONCLUSIVE",
        "reason": "n=4 preregistered as underpowered; result retained as null/negative evidence",
        "null_retained": True,
    }
    out["evidence_hash"] = content_hash(out)
    _dump(root / "evidence" / "C3_underpowered_null.json", out)
    return out


def counterfactual_attention_stability(root: Path, *, seed: int, n: int = 64, T: int = 20) -> dict[str, Any]:
    """C4 — permute attention; measure how often a linear proxy prediction is preserved."""
    rng = np.random.default_rng(seed)
    # Hidden states + attention → context → logit proxy
    H = rng.normal(size=(n, T, 8))
    logits_attn = rng.normal(size=(n, T))
    attn = _softmax(logits_attn)
    ctx = np.einsum("nt,ntd->nd", attn, H)
    w = rng.normal(size=(8,))
    pred0 = (ctx @ w) > 0

    # Permute attention mass per row
    perm = np.stack([rng.permutation(T) for _ in range(n)])
    attn_p = np.take_along_axis(attn, perm, axis=1)
    ctx_p = np.einsum("nt,ntd->nd", attn_p, H)
    pred1 = (ctx_p @ w) > 0
    same = float(np.mean(pred0 == pred1))
    tv = float(0.5 * np.abs(attn - attn_p).sum(axis=1).mean())
    out = {
        "stage": "C4_counterfactual_attention",
        "object_id": EXTERNAL_OBJECT_ID,
        "seed": seed,
        "n": n,
        "T": T,
        "frac_pred_preserved_under_attn_perm": same,
        "mean_attn_tv_distance": tv,
        "decision_hint": (
            "ALTERED_ATTN_OFTEN_PRESERVES_PRED"
            if same >= 0.7
            else "ALTERED_ATTN_CHANGES_PRED_OFTEN"
        ),
    }
    out["evidence_hash"] = content_hash(out)
    _dump(root / "evidence" / f"C4_counterfactual_seed{seed}.json", out)
    return out


def deepen_post_fault(root: Path, *, seed: int, prior_hashes: list[str]) -> dict[str, Any]:
    """C5 — larger-N deepen after fault; evidence hash MUST differ from priors."""
    deepened = attention_importance_kendall(root, seed=seed, n=256, T=40)
    deepened = dict(deepened)
    deepened["stage"] = "C5_post_fault_deepen"
    deepened["prior_evidence_hashes"] = list(prior_hashes)
    # recompute hash after stage retag so artifact identity matches C5
    deepened.pop("evidence_hash", None)
    deepened["evidence_hash"] = content_hash(deepened)
    deepened["is_new_vs_priors"] = deepened["evidence_hash"] not in set(prior_hashes)
    _dump(root / "evidence" / f"C5_deepen_seed{seed}.json", deepened)
    return deepened


def contradiction_and_invalidation(root: Path, *, seed: int) -> dict[str, Any]:
    """C6 — conflicting strong-association probe vs primary weak-association claim."""
    rng = np.random.default_rng(seed)
    n, T = 128, 24
    importance = rng.normal(size=(n, T))
    # Artificially strong alignment (adversarial / contradictory evidence)
    attn = _softmax(5.0 * importance + rng.normal(scale=0.05, size=(n, T)))
    taus = [float(stats.kendalltau(attn[i], importance[i])[0]) for i in range(n)]
    median_tau = float(np.median(taus))
    contradictory = {
        "stage": "C6_contradictory_strong_association",
        "median_kendall_tau": median_tau,
        "conflicts_with_primary_claim": median_tau > 0.7,
        "handling": "mark_as_contradictory_evidence_candidate_for_invalidation_path",
    }
    contradictory["evidence_hash"] = content_hash(contradictory)
    _dump(root / "evidence" / "C6_contradiction.json", contradictory)
    return contradictory


def terminal_review_pack(root: Path, *, ticks: list[dict[str, Any]]) -> dict[str, Any]:
    """C7 — pack for independent review (executor does not self-certify M1.5)."""
    hashes = [t.get("evidence_hash") for t in ticks if t.get("evidence_hash")]
    nulls = [t for t in ticks if t.get("null_retained") or t.get("decision") == "NULL_INCONCLUSIVE"]
    pack = {
        "stage": "C7_terminal_review_pack",
        "object_id": EXTERNAL_OBJECT_ID,
        "protocol": "LH-COGNITIVE-v1",
        "m15_claimed": False,
        "n_ticks": len(ticks),
        "distinct_evidence_hashes": sorted({h for h in hashes if h}),
        "n_distinct_evidence": len({h for h in hashes if h}),
        "n_null_or_inconclusive": len(nulls),
        "ticks_summary": [
            {"stage": t.get("stage"), "evidence_hash": t.get("evidence_hash"), "decision": t.get("decision") or t.get("decision_hint")}
            for t in ticks
        ],
        "independent_review_required": True,
        "self_certification_forbidden": True,
    }
    pack["evidence_hash"] = content_hash(pack)
    _dump(root / "review" / "TERMINAL_REVIEW_PACK.json", pack)
    _dump(root / "review" / "INDEPENDENT_REVIEW_REQUIRED.md", {
        "text": "Independent contour must score this pack; executor m15_claimed stays false."
    })
    return pack


def _softmax(x: NDArray[np.floating]) -> NDArray[np.floating]:
    z = x - np.max(x, axis=-1, keepdims=True)
    e = np.exp(z)
    return e / np.sum(e, axis=-1, keepdims=True)  # type: ignore[no-any-return]


def _dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
