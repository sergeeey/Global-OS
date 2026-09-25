"""Arm A baseline causal discovery — observational CSV only.

No Global OS research loop. No sealed GT. No generator DAG imports.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "observational.csv"
META_PATH = ROOT / "public_meta.json"
OUT = ROOT.parent  # arms/A


def load_rows() -> tuple[list[str], list[dict[str, float]]]:
    with CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        names = list(reader.fieldnames or [])
        rows = [{k: float(r[k]) for k in names} for r in reader]
    return names, rows


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def cov(xs: list[float], ys: list[float]) -> float:
    mx, my = mean(xs), mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)


def corr(xs: list[float], ys: list[float]) -> float:
    c = cov(xs, ys)
    vx = cov(xs, xs)
    vy = cov(ys, ys)
    if vx <= 1e-18 or vy <= 1e-18:
        return 0.0
    return c / math.sqrt(vx * vy)


def col(rows: list[dict[str, float]], name: str) -> list[float]:
    return [r[name] for r in rows]


def residualize(y: list[float], predictors: list[list[float]]) -> list[float]:
    """OLS residuals of y on predictors + intercept via normal equations (small p)."""
    n = len(y)
    p = len(predictors)
    # Design X: n x (p+1)
    xtx = [[0.0] * (p + 1) for _ in range(p + 1)]
    xty = [0.0] * (p + 1)
    for i in range(n):
        row = [1.0] + [predictors[j][i] for j in range(p)]
        for a in range(p + 1):
            xty[a] += row[a] * y[i]
            for b in range(p + 1):
                xtx[a][b] += row[a] * row[b]
    # Solve xtx beta = xty (Gaussian elimination)
    m = p + 1
    a = [xtx[i][:] + [xty[i]] for i in range(m)]
    for col_i in range(m):
        pivot = max(range(col_i, m), key=lambda r: abs(a[r][col_i]))
        a[col_i], a[pivot] = a[pivot], a[col_i]
        piv = a[col_i][col_i]
        if abs(piv) < 1e-12:
            continue
        for j in range(col_i, m + 1):
            a[col_i][j] /= piv
        for r in range(m):
            if r == col_i:
                continue
            factor = a[r][col_i]
            for j in range(col_i, m + 1):
                a[r][j] -= factor * a[col_i][j]
    beta = [a[i][m] for i in range(m)]
    resid = []
    for i in range(n):
        pred = beta[0] + sum(beta[j + 1] * predictors[j][i] for j in range(p))
        resid.append(y[i] - pred)
    return resid


def partial_corr(
    rows: list[dict[str, float]], a: str, b: str, cond: list[str]
) -> float:
    ya = col(rows, a)
    yb = col(rows, b)
    if not cond:
        return corr(ya, yb)
    preds = [col(rows, c) for c in cond]
    ra = residualize(ya, preds)
    rb = residualize(yb, preds)
    return corr(ra, rb)


def fisher_z(r: float, n: int, k: int) -> float:
    r = max(min(r, 0.999999), -0.999999)
    z = 0.5 * math.log((1 + r) / (1 - r))
    df = max(n - k - 3, 1)
    return abs(z) * math.sqrt(df)


def discover_edges(names: list[str], rows: list[dict[str, float]]) -> list[list[str]]:
    """Conservative PC-like skeleton + score-based orientation heuristics."""
    n = len(rows)
    # Unconditional correlations
    pairs: list[tuple[str, str, float]] = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            r = corr(col(rows, a), col(rows, b))
            pairs.append((a, b, abs(r)))
    pairs.sort(key=lambda t: -t[2])

    # Keep strong unconditional associations as candidate undirected edges
    thresh_r = 0.12
    z_thresh = 2.5
    undirected: set[tuple[str, str]] = set()
    for a, b, ar in pairs:
        if ar < thresh_r:
            continue
        # Screen: remain dependent given each single other variable with high |r|
        survive = True
        # Condition on top correlated others
        others = [x for x in names if x not in (a, b)]
        others.sort(
            key=lambda o: -(abs(corr(col(rows, a), col(rows, o))) + abs(corr(col(rows, b), col(rows, o))))
        )
        for o in others[:6]:
            pc = partial_corr(rows, a, b, [o])
            if fisher_z(pc, n, 1) < z_thresh:
                survive = False
                break
        if survive:
            undirected.add(tuple(sorted((a, b))))

    # Orient by regression R^2 asymmetry + temporal-like index heuristic (lower index more exogenous)
    claimed: list[list[str]] = []
    for a, b in sorted(undirected):
        # Prefer direction with larger |coef| when regressing each on the other + shared neighbors
        neighbors_a = [x for x in names if tuple(sorted((a, x))) in undirected and x != b]
        neighbors_b = [x for x in names if tuple(sorted((b, x))) in undirected and x != a]
        shared = list(set(neighbors_a) & set(neighbors_b))[:3]

        def fit_coef(y_name: str, x_name: str, extra: list[str]) -> float:
            y = col(rows, y_name)
            preds = [col(rows, x_name)] + [col(rows, e) for e in extra]
            # reuse residualize internals by computing beta via small solve
            n_ = len(y)
            p = len(preds)
            xtx = [[0.0] * (p + 1) for _ in range(p + 1)]
            xty = [0.0] * (p + 1)
            for i in range(n_):
                rowv = [1.0] + [preds[j][i] for j in range(p)]
                for aa in range(p + 1):
                    xty[aa] += rowv[aa] * y[i]
                    for bb in range(p + 1):
                        xtx[aa][bb] += rowv[aa] * rowv[bb]
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
            return abs(aug[1][m])  # coef on x

        c_ab = fit_coef(b, a, shared)  # a -> b strength
        c_ba = fit_coef(a, b, shared)
        # Index prior: smaller index more likely parent if coefs close
        ia, ib = int(a[1:]), int(b[1:])
        if c_ab > c_ba * 1.15:
            claimed.append([a, b])
        elif c_ba > c_ab * 1.15:
            claimed.append([b, a])
        elif ia < ib:
            claimed.append([a, b])
        else:
            claimed.append([b, a])

    # Cap claimed edges to avoid FP explosion (limited structure recovery)
    # Rank by |corr|
    claimed.sort(key=lambda e: -abs(corr(col(rows, e[0]), col(rows, e[1]))))
    return claimed[:18]


def predict_interventions(
    names: list[str],
    rows: list[dict[str, float]],
    edges: list[list[str]],
    targets: list[dict],
) -> list[dict]:
    """Naive intervention prediction: regress target on do_var + parents-of-target excluding do_var descendants approx.

    Uses observational regression E[target|do_var] as crude proxy when adjusting for
    other parents of target that are not descendants of do_var (approx: all other claimed parents).
    """
    parents: dict[str, list[str]] = {n: [] for n in names}
    for s, d in edges:
        parents[d].append(s)

    preds_out = []
    for t in targets:
        do_var = t["do_var"]
        do_value = float(t["do_value"])
        target = t["target"]
        # Adjustors: claimed parents of target except do_var
        adj = [p for p in parents[target] if p != do_var][:4]
        # Also include do_var as regressor
        y = col(rows, target)
        preds = [col(rows, do_var)] + [col(rows, a) for a in adj]
        n = len(y)
        p = len(preds)
        xtx = [[0.0] * (p + 1) for _ in range(p + 1)]
        xty = [0.0] * (p + 1)
        for i in range(n):
            rowv = [1.0] + [preds[j][i] for j in range(p)]
            for aa in range(p + 1):
                xty[aa] += rowv[aa] * y[i]
                for bb in range(p + 1):
                    xtx[aa][bb] += rowv[aa] * rowv[bb]
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
        beta = [aug[i][m] for i in range(m)]
        # Predict at do_value with adjustors at their means
        pred = beta[0] + beta[1] * do_value
        for j, a in enumerate(adj):
            pred += beta[j + 2] * mean(col(rows, a))
        preds_out.append(
            {
                "intervention_id": t["intervention_id"],
                "target": target,
                "predicted_mean": float(pred),
            }
        )
    return preds_out


def main() -> None:
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    names, rows = load_rows()
    edges = discover_edges(names, rows)
    interventions = predict_interventions(names, rows, edges, meta["intervention_targets"])

    # Decision: we recovered a limited claimed structure + made intervention forecasts;
    # without holdout labels this arm marks INCONCLUSIVE on scientific certainty,
    # but still submits concrete claims for scoring.
    submission = {
        "arm_id": "A",
        "claimed_edges": edges,
        "intervention_predictions": interventions,
        "decision": "INCONCLUSIVE",
        "stop_reason": "completed_baseline_discovery_under_budget",
        "notes": (
            "Strong-agent baseline: partial-correlation skeleton + regression orientation; "
            "intervention forecasts via observational regression with claimed parents as adjustors. "
            "No sealed peek. No GOS durable loop."
        ),
    }
    (OUT / "submission.json").write_text(
        json.dumps(submission, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "workdir" / "discovery_summary.json").write_text(
        json.dumps(
            {
                "n_edges_claimed": len(edges),
                "edges": edges,
                "method": "partial_corr_screen + coef_asymmetry_orientation + OLS_do_proxy",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"edges": len(edges), "interventions": len(interventions)}, indent=2))


if __name__ == "__main__":
    main()
