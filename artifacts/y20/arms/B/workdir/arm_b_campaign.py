"""Arm B — Global OS research loop on public CSV only.

Competing hypotheses H_B1/H_B2/H_B3/H_B4 with internal fold falsification.
Does not read Arm A outputs or sealed GT.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARM = ROOT.parent
CSV_PATH = ROOT / "observational.csv"
META_PATH = ROOT / "public_meta.json"


def load_rows() -> tuple[list[str], list[dict[str, float]]]:
    with CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        names = list(reader.fieldnames or [])
        rows = [{k: float(r[k]) for k in names} for r in reader]
    return names, rows


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def cov(xs: list[float], ys: list[float]) -> float:
    mx, my = mean(xs), mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)


def corr(xs: list[float], ys: list[float]) -> float:
    c = cov(xs, ys)
    vx, vy = cov(xs, xs), cov(ys, ys)
    if vx <= 1e-18 or vy <= 1e-18:
        return 0.0
    return c / math.sqrt(vx * vy)


def col(rows: list[dict[str, float]], name: str) -> list[float]:
    return [r[name] for r in rows]


def ols_beta(y: list[float], predictors: list[list[float]]) -> list[float]:
    n = len(y)
    p = len(predictors)
    xtx = [[0.0] * (p + 1) for _ in range(p + 1)]
    xty = [0.0] * (p + 1)
    for i in range(n):
        rowv = [1.0] + [predictors[j][i] for j in range(p)]
        for a in range(p + 1):
            xty[a] += rowv[a] * y[i]
            for b in range(p + 1):
                xtx[a][b] += rowv[a] * rowv[b]
    m = p + 1
    aug = [xtx[i][:] + [xty[i]] for i in range(m)]
    for col_i in range(m):
        pivot = max(range(col_i, m), key=lambda r: abs(aug[r][col_i]))
        aug[col_i], aug[pivot] = aug[pivot], aug[col_i]
        piv = aug[col_i][col_i]
        if abs(piv) < 1e-12:
            continue
        for j in range(col_i, m + 1):
            aug[col_i][j] /= piv
        for r in range(m):
            if r == col_i:
                continue
            factor = aug[r][col_i]
            for j in range(col_i, m + 1):
                aug[r][j] -= factor * aug[col_i][j]
    return [aug[i][m] for i in range(m)]


def residualize(y: list[float], predictors: list[list[float]]) -> list[float]:
    beta = ols_beta(y, predictors)
    out = []
    for i in range(len(y)):
        pred = beta[0] + sum(beta[j + 1] * predictors[j][i] for j in range(len(predictors)))
        out.append(y[i] - pred)
    return out


def partial_corr(rows: list[dict[str, float]], a: str, b: str, cond: list[str]) -> float:
    ya, yb = col(rows, a), col(rows, b)
    if not cond:
        return corr(ya, yb)
    preds = [col(rows, c) for c in cond]
    return corr(residualize(ya, preds), residualize(yb, preds))


def fisher_z(r: float, n: int, k: int) -> float:
    r = max(min(r, 0.999999), -0.999999)
    z = 0.5 * math.log((1 + r) / (1 - r))
    return abs(z) * math.sqrt(max(n - k - 3, 1))


def orient(rows: list[dict[str, float]], undirected: set[tuple[str, str]], names: list[str]) -> list[list[str]]:
    claimed: list[list[str]] = []
    for a, b in sorted(undirected):
        neighbors_a = [x for x in names if tuple(sorted((a, x))) in undirected and x != b]
        neighbors_b = [x for x in names if tuple(sorted((b, x))) in undirected and x != a]
        shared = list(set(neighbors_a) & set(neighbors_b))[:3]

        def coef(y_name: str, x_name: str) -> float:
            beta = ols_beta(col(rows, y_name), [col(rows, x_name)] + [col(rows, e) for e in shared])
            return abs(beta[1])

        c_ab, c_ba = coef(b, a), coef(a, b)
        ia, ib = int(a[1:]), int(b[1:])
        if c_ab > c_ba * 1.15:
            claimed.append([a, b])
        elif c_ba > c_ab * 1.15:
            claimed.append([b, a])
        elif ia < ib:
            claimed.append([a, b])
        else:
            claimed.append([b, a])
    claimed.sort(key=lambda e: -abs(corr(col(rows, e[0]), col(rows, e[1]))))
    return claimed


def method_dense(names: list[str], rows: list[dict[str, float]], top_k: int = 30) -> list[list[str]]:
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            pairs.append((a, b, abs(corr(col(rows, a), col(rows, b)))))
    pairs.sort(key=lambda t: -t[2])
    undirected = {tuple(sorted((a, b))) for a, b, ar in pairs[:top_k] if ar >= 0.08}
    return orient(rows, undirected, names)[:24]


def method_sparse(names: list[str], rows: list[dict[str, float]]) -> list[list[str]]:
    n = len(rows)
    undirected: set[tuple[str, str]] = set()
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            if abs(corr(col(rows, a), col(rows, b))) < 0.12:
                continue
            others = [x for x in names if x not in (a, b)]
            others.sort(
                key=lambda o: -(
                    abs(corr(col(rows, a), col(rows, o))) + abs(corr(col(rows, b), col(rows, o)))
                )
            )
            survive = True
            for o in others[:6]:
                if fisher_z(partial_corr(rows, a, b, [o]), n, 1) < 2.5:
                    survive = False
                    break
            if survive:
                undirected.add(tuple(sorted((a, b))))
    return orient(rows, undirected, names)[:18]


def parents_map(edges: list[list[str]], names: list[str]) -> dict[str, list[str]]:
    p = {n: [] for n in names}
    for s, d in edges:
        p[d].append(s)
    return p


def predict_do(
    rows: list[dict[str, float]],
    edges: list[list[str]],
    names: list[str],
    targets: list[dict],
    *,
    path_aware: bool = False,
) -> list[dict]:
    parents = parents_map(edges, names)
    # children map for mediators
    children: dict[str, list[str]] = {n: [] for n in names}
    for s, d in edges:
        children[s].append(d)
    out = []
    for t in targets:
        do_var, do_value, target = t["do_var"], float(t["do_value"]), t["target"]
        adj = [p for p in parents[target] if p != do_var][:4]
        if path_aware:
            # add one mediator on claimed path do_var -> * -> target if present
            for mid in children.get(do_var, []):
                if target in children.get(mid, []) or mid in parents.get(target, []):
                    if mid not in adj and mid != target:
                        adj.append(mid)
                        break
        beta = ols_beta(col(rows, target), [col(rows, do_var)] + [col(rows, a) for a in adj])
        pred = beta[0] + beta[1] * do_value
        for j, a in enumerate(adj):
            pred += beta[j + 2] * mean(col(rows, a))
        out.append(
            {
                "intervention_id": t["intervention_id"],
                "target": target,
                "predicted_mean": float(pred),
            }
        )
    return out


def soft_intervention_mae(
    train: list[dict[str, float]],
    hold: list[dict[str, float]],
    edges: list[list[str]],
    names: list[str],
    targets: list[dict],
    *,
    path_aware: bool = False,
) -> float:
    """Falsification proxy: compare predicted do-mean vs empirical mean of target
    among hold rows where do_var is near do_value (local observational slice).
    """
    preds = predict_do(train, edges, names, targets, path_aware=path_aware)
    abs_errs = []
    for t, p in zip(targets, preds):
        do_var, do_value, target = t["do_var"], float(t["do_value"]), t["target"]
        xs = col(hold, do_var)
        # bandwidth: 25% of hold closest to do_value
        idxs = sorted(range(len(hold)), key=lambda i: abs(xs[i] - do_value))
        k = max(40, len(hold) // 8)
        emp = mean([hold[i][target] for i in idxs[:k]])
        abs_errs.append(abs(p["predicted_mean"] - emp))
    return sum(abs_errs) / len(abs_errs)


def split(rows: list[dict[str, float]], frac: float = 0.8) -> tuple[list, list]:
    n = len(rows)
    cut = int(n * frac)
    return rows[:cut], rows[cut:]


def main() -> None:
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    names, rows = load_rows()
    train, hold = split(rows)
    targets = meta["intervention_targets"]

    log_hyp: list[dict] = []

    # --- H_B1 dense ---
    e1 = method_dense(names, train)
    mae1 = soft_intervention_mae(train, hold, e1, names, targets)
    log_hyp.append({"id": "H_B1_dense", "n_edges": len(e1), "soft_mae": mae1, "decision": "candidate"})

    # --- H_B2 sparse ---
    e2 = method_sparse(names, train)
    mae2 = soft_intervention_mae(train, hold, e2, names, targets)
    better_sparse = mae2 < mae1 * 0.97  # small MCID-like improvement
    log_hyp.append(
        {
            "id": "H_B2_sparse",
            "n_edges": len(e2),
            "soft_mae": mae2,
            "beats_dense": better_sparse,
            "decision": "SUPPORTED" if better_sparse else "REJECTED",
        }
    )

    # choose structure
    if better_sparse:
        edges = e2
        winner_struct = "H_B2_sparse"
        struct_mae = mae2
    else:
        edges = e1
        winner_struct = "H_B1_dense"
        struct_mae = mae1

    # --- H_B3 path-aware on chosen structure ---
    mae3 = soft_intervention_mae(train, hold, edges, names, targets, path_aware=True)
    path_helps = mae3 < struct_mae * 0.97
    log_hyp.append(
        {
            "id": "H_B3_path_aware",
            "soft_mae": mae3,
            "base_mae": struct_mae,
            "decision": "SUPPORTED" if path_helps else "REJECTED",
        }
    )

    # --- H_B4 null: predict train mean of target ---
    null_errs = []
    for t in targets:
        target = t["target"]
        do_var, do_value = t["do_var"], float(t["do_value"])
        pred = mean(col(train, target))
        xs = col(hold, do_var)
        idxs = sorted(range(len(hold)), key=lambda i: abs(xs[i] - do_value))
        k = max(40, len(hold) // 8)
        emp = mean([hold[i][target] for i in idxs[:k]])
        null_errs.append(abs(pred - emp))
    mae_null = sum(null_errs) / len(null_errs)
    best_mae = mae3 if path_helps else struct_mae
    beats_null = best_mae < mae_null * 0.97
    log_hyp.append(
        {
            "id": "H_B4_null_mean",
            "soft_mae": mae_null,
            "best_method_mae": best_mae,
            "method_beats_null": beats_null,
            "decision": "REJECTED" if beats_null else "SUPPORTED",
        }
    )

    path_aware = path_helps
    # Refit on full data for submission
    if winner_struct == "H_B2_sparse":
        final_edges = method_sparse(names, rows)
    else:
        final_edges = method_dense(names, rows)
    interventions = predict_do(rows, final_edges, names, targets, path_aware=path_aware)

    if not beats_null:
        decision = "INCONCLUSIVE"
        stop = "methods_not_above_null_on_internal_soft_intervention"
    elif path_helps or better_sparse:
        decision = "SUPPORTED"
        stop = "internal_falsification_selected_structure_beats_null"
    else:
        decision = "INCONCLUSIVE"
        stop = "dense_only_marginal_vs_null"

    submission = {
        "arm_id": "B",
        "claimed_edges": final_edges,
        "intervention_predictions": interventions,
        "decision": decision,
        "stop_reason": stop,
        "notes": (
            f"GOS loop: closed {log_hyp}. winner_struct={winner_struct}, "
            f"path_aware={path_aware}. Sealed unseen; Arm A unread."
        ),
    }
    (ARM / "submission.json").write_text(json.dumps(submission, indent=2) + "\n", encoding="utf-8")
    (ARM / "HYPOTHESIS_TRACE.json").write_text(json.dumps(log_hyp, indent=2) + "\n", encoding="utf-8")
    (ARM / "WHAT_WE_KNOW.md").write_text(
        f"# Arm B WHAT_WE_KNOW\n\n"
        f"- Structure winner: `{winner_struct}`\n"
        f"- Path-aware: `{path_aware}`\n"
        f"- Beats null on soft-intervention proxy: `{beats_null}`\n"
        f"- Decision: `{decision}`\n"
        f"- Sealed: UNSEEN · Arm A outputs: UNREAD\n",
        encoding="utf-8",
    )
    state = {
        "arm": "B",
        "goal": "Y20-ARM-B-CAUSAL",
        "phase": "TERMINAL",
        "active_question": None,
        "closed": {h["id"]: h["decision"] for h in log_hyp},
        "winning_structure": winner_struct,
        "path_aware": path_aware,
        "decision": decision,
        "gos_components_in_use": [
            "goal_contract",
            "competing_hypotheses",
            "durable_research_state",
            "falsification_internal_folds",
            "terminal_stop_rule",
        ],
        "sealed_unseen": True,
        "arm_a_outputs_unread": True,
    }
    (ARM / "CURRENT_STATE.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "edges": len(final_edges), "hyp": log_hyp}, indent=2))


if __name__ == "__main__":
    main()
