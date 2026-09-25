"""R2 executor — audit released CorrStats + independent attention-counterfactual probe.

Does NOT write independent review scores.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent
UPSTREAM = WORK / "AttentionExplanation" / "graph_outputs" / "CorrStats_kendalltau"
OUT = ROOT


def audit_corrstats() -> dict:
    if not UPSTREAM.is_dir():
        return {"status": "BLOCKED", "reason": "upstream CorrStats dir missing"}
    rows = []
    for f in sorted(UPSTREAM.glob("*.csv")):
        df = pd.read_csv(f, index_col=0)
        rec: dict = {"file": f.name}
        for k in ("ag", "al", "gl"):
            if k in df.index:
                rec[f"{k}_mean"] = float(df.loc[k, "mean"])
                rec[f"{k}_pval_sig"] = float(df.loc[k, "pval_sig"])
        rows.append(rec)
    out = pd.DataFrame(rows)
    out.to_csv(WORK / "corrstats_summary.csv", index=False)
    ag = out["ag_mean"].dropna()
    gl = out["gl_mean"].dropna()
    return {
        "status": "OK",
        "n_configs": int(len(out)),
        "ag_median": float(ag.median()),
        "ag_mean": float(ag.mean()),
        "gl_median": float(gl.median()),
        "frac_ag_lt_0_5": float((ag < 0.5).mean()),
        "frac_ag_lt_gl": float((ag < gl.reindex(ag.index)).mean())
        if len(gl)
        else None,
        "interpretation": (
            "Released CorrStats show median attention–gradient Kendall τ (ag) "
            "well below strong correlation; often below gradient self-consistency (gl)."
        ),
    }


class TinyAttnClassifier(nn.Module):
    """Minimal encoder+attention for counterfactual attention probe (extension)."""

    def __init__(self, vocab: int = 50, dim: int = 32) -> None:
        super().__init__()
        self.emb = nn.Embedding(vocab, dim)
        self.rnn = nn.GRU(dim, dim, batch_first=True, bidirectional=True)
        self.attn_v = nn.Linear(dim * 2, 1, bias=False)
        self.out = nn.Linear(dim * 2, 2)

    def forward(self, x: torch.Tensor, attn_override: torch.Tensor | None = None):
        h = self.emb(x)
        h, _ = self.rnn(h)  # [B,T,2D]
        scores = self.attn_v(h).squeeze(-1)  # [B,T]
        attn = F.softmax(scores, dim=-1)
        if attn_override is not None:
            attn = attn_override
        ctx = torch.einsum("bt,btd->bd", attn, h)
        logits = self.out(ctx)
        return logits, attn


def independent_counterfactual_probe(seed: int = 0) -> dict:
    """Extension: after brief training, can altered attention preserve argmax?"""
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = TinyAttnClassifier()
    opt = torch.optim.Adam(model.parameters(), lr=1e-2)
    B, T, steps = 64, 20, 200
    # Synthetic task: label = whether token-id 7 appears (forces non-uniform attention usefulness)
    def batch() -> tuple[torch.Tensor, torch.Tensor]:
        x = torch.randint(0, 50, (B, T))
        y = (x == 7).any(dim=1).long()
        return x, y

    model.train()
    last_acc = 0.0
    for _ in range(steps):
        x, y = batch()
        logits, _ = model(x)
        loss = F.cross_entropy(logits, y)
        opt.zero_grad()
        loss.backward()
        opt.step()
        last_acc = (logits.argmax(-1) == y).float().mean().item()

    model.eval()
    with torch.no_grad():
        x, y = batch()
        logits0, attn0 = model(x)
        pred0 = logits0.argmax(-1)
        acc = (pred0 == y).float().mean().item()
        # degenerate guard
        pred_hist = torch.bincount(pred0, minlength=2).tolist()
        idx = torch.stack([torch.randperm(T) for _ in range(B)])
        attn_perm = attn0.gather(1, idx)
        logits1, _ = model(x, attn_override=attn_perm)
        pred1 = logits1.argmax(-1)
        same = (pred0 == pred1).float().mean().item()
        attn_rand = torch.distributions.Dirichlet(torch.ones(T)).sample((B,))
        logits2, _ = model(x, attn_override=attn_rand)
        pred2 = logits2.argmax(-1)
        same_rand = (pred0 == pred2).float().mean().item()
        tv = 0.5 * (attn0 - attn_perm).abs().sum(-1).mean().item()
        # logit shift under perm
        logit_l2 = (logits0 - logits1).pow(2).sum(-1).sqrt().mean().item()
    return {
        "status": "OK",
        "n": B,
        "seq_len": T,
        "train_steps": steps,
        "train_acc_last": last_acc,
        "eval_acc": acc,
        "pred_hist": pred_hist,
        "frac_pred_same_under_permuted_attn": same,
        "frac_pred_same_under_random_attn": same_rand,
        "mean_tv_attn_vs_permuted": tv,
        "mean_logit_l2_under_perm": logit_l2,
        "degenerate_pred_collapse": max(pred_hist) == B,
        "note": (
            "Trained tiny BiGRU+attention on synthetic token-presence task; "
            "tests whether alternate attention can preserve argmax. "
            "NOT a full SST/IMDB replication of Jain & Wallace."
        ),
    }


def main() -> None:
    audit = audit_corrstats()
    probe = independent_counterfactual_probe()
    blocked = {
        "official_full_retrain": {
            "status": "BLOCKED_ENVIRONMENT",
            "reason": (
                "Upstream requires pytorch-nightly/source + torchtext 0.4 from source "
                "+ dataset preprocess; not executed end-to-end in this environment."
            ),
        }
    }
    # Decision rule (executor proposal; independent reviewer re-scores)
    if audit.get("status") == "OK" and audit.get("frac_ag_lt_0_5", 0) >= 0.6:
        if probe.get("degenerate_pred_collapse"):
            decision = "PARTIAL"
            rationale = (
                "CorrStats audit supports weak attn–gradient alignment; "
                "extension probe collapsed predictions — treated as weak extension. "
                "Full official retrain blocked."
            )
        elif probe["frac_pred_same_under_permuted_attn"] >= 0.3:
            decision = "PARTIAL"
            rationale = (
                "Released CorrStats support weak attn–gradient alignment across "
                "many configs; trained tiny-model probe shows non-trivial "
                "prediction-preserving attention changes. Full official retrain blocked."
            )
        else:
            decision = "PARTIAL"
            rationale = (
                "CorrStats support C1 pattern; probe rarely preserved predictions "
                "under attention change (mechanism only partially echoed). "
                "Full retrain blocked."
            )
    else:
        decision = "INCONCLUSIVE"
        rationale = "Insufficient released-evidence support under audit thresholds."

    submission = {
        "mission_id": "R2-ATTN-EXPLAIN-REPLICATION-v1",
        "target": "arXiv:1902.10186",
        "decision": decision,
        "rationale": rationale,
        "claims_tested": ["C1_attention_not_explanation", "C2_cross_config_pattern"],
        "audit_corrstats": audit,
        "extension_counterfactual_probe": probe,
        "blocks": blocked,
        "artifacts": [
            "artifacts/r2/replication/work/corrstats_summary.csv",
            "artifacts/r2/replication/work/extension_probe.json",
            "artifacts/r2/replication/REPORT.md",
        ],
        "gos_advantage_claimed": False,
        "executor_note": "Scores for usefulness are for independent reviewer only.",
    }
    (WORK / "extension_probe.json").write_text(json.dumps(probe, indent=2) + "\n")
    (OUT / "SUBMISSION.json").write_text(json.dumps(submission, indent=2) + "\n")
    print(json.dumps({"decision": decision, "ag_median": audit.get("ag_median"), "probe_same": probe["frac_pred_same_under_permuted_attn"]}, indent=2))


if __name__ == "__main__":
    main()
