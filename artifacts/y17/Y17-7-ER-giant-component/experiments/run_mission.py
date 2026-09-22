"""Y17-7 — network: ER giant-component threshold near p=1/n?

Class: network / random-graph phase transition (distinct from Y17-1..6).
Does empirical p50 (Prob[|LCC|/n ≥ 0.5] = 0.5) lie within relative TOL of 1/n?

Protocol locked:
  N = 200 nodes
  p_grid relative to p_c = 1/N: factors {0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0}
  N_GRAPH = 60 graphs per p (seeds 800+)
  Giant iff largest connected component size / N ≥ 0.5
  Estimate p50 by linear interpolation on empirical giant rates
  SUPPORTED iff |p50 - 1/N| / (1/N) ≤ 0.35
"""

from __future__ import annotations

from typing import Any

import numpy as np

N_NODES = 200
P_C = 1.0 / N_NODES
FACTORS = (0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0)
N_GRAPH = 60
SEED_START = 800
GIANT_FRAC = 0.5
REL_TOL = 0.35


def largest_cc_frac(n: int, p: float, rng: np.random.Generator) -> float:
    """Erdős–Rényi G(n,p) via adjacency; DFS largest component fraction."""
    # Build undirected edges
    # For n=200, upper triangle ~ 20k checks — fine
    adj: list[list[int]] = [[] for _ in range(n)]
    for i in range(n):
        # vectorized coin flips for j>i
        js = np.arange(i + 1, n)
        if js.size == 0:
            continue
        mask = rng.random(js.size) < p
        for j in js[mask]:
            j = int(j)
            adj[i].append(j)
            adj[j].append(i)
    seen = [False] * n
    best = 0
    for start in range(n):
        if seen[start]:
            continue
        stack = [start]
        seen[start] = True
        size = 0
        while stack:
            u = stack.pop()
            size += 1
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        if size > best:
            best = size
    return best / n


def run_experiment() -> dict[str, Any]:
    rates: dict[str, Any] = {}
    ps: list[float] = []
    giant_rates: list[float] = []
    seed = SEED_START
    for fac in FACTORS:
        p = P_C * fac
        giants = 0
        fracs = []
        for _ in range(N_GRAPH):
            rng = np.random.default_rng(seed)
            seed += 1
            frac = largest_cc_frac(N_NODES, p, rng)
            fracs.append(frac)
            if frac >= GIANT_FRAC:
                giants += 1
        rate = giants / N_GRAPH
        ps.append(p)
        giant_rates.append(rate)
        rates[f"{fac:.1f}"] = {
            "factor": fac,
            "p": p,
            "giant_rate": rate,
            "mean_lcc_frac": float(np.mean(fracs)),
        }

    # interpolate p50 where giant_rate crosses 0.5
    p50 = None
    for i in range(len(giant_rates) - 1):
        r0, r1 = giant_rates[i], giant_rates[i + 1]
        if r0 <= 0.5 <= r1 or r1 <= 0.5 <= r0:
            if abs(r1 - r0) < 1e-12:
                p50 = ps[i]
            else:
                t = (0.5 - r0) / (r1 - r0)
                p50 = ps[i] + t * (ps[i + 1] - ps[i])
            break
    if p50 is None:
        # never crossed — use endpoint heuristic
        if giant_rates[-1] < 0.5:
            p50 = ps[-1] * 1.5  # beyond grid
        else:
            p50 = ps[0] * 0.5

    rel_err = abs(p50 - P_C) / P_C
    in_band = rel_err <= REL_TOL

    if in_band:
        decision = "SUPPORTED"
        nulls: list[dict[str, Any]] = []
    else:
        decision = "REJECTED"
        nulls = [
            {
                "id": "p50_far_from_theory",
                "p50": p50,
                "p_c": P_C,
                "rel_err": rel_err,
                "rel_tol": REL_TOL,
            }
        ]

    contradictory: list[dict[str, Any]] = []
    # At p=p_c theory predicts mean LCC ~ n^{2/3} for critical window — rate at factor=1 may be <<0.5
    if rates["1.0"]["giant_rate"] > 0.7:
        contradictory.append(
            {
                "note": "at exact p_c giant_rate unexpectedly high for finite n — finite-size effect",
                "giant_rate_at_pc": rates["1.0"]["giant_rate"],
                "rule": "walled descriptive",
            }
        )

    return {
        "config": {
            "class": "network_random_graph_phase_transition",
            "model": "erdos_renyi_Gnp",
            "n_nodes": N_NODES,
            "p_c_theory": P_C,
            "factors": list(FACTORS),
            "n_graph_per_p": N_GRAPH,
            "seed_start": SEED_START,
            "giant_frac_threshold": GIANT_FRAC,
            "rel_tol": REL_TOL,
            "y17_writes": False,
            "catalog_bridge": "network phase transition / motif stability probes",
        },
        "primary": {
            "p50": float(p50),
            "p_c": P_C,
            "rel_err": float(rel_err),
            "in_band": in_band,
            "rates": rates,
            "giant_rates": giant_rates,
            "ps": ps,
        },
        "decision": decision,
        "nulls": nulls,
        "contradictory_evidence": contradictory,
        "scope": {
            "qualification": (
                "SUPPORTED means empirical p50 for |LCC|/n≥0.5 is within 35% of 1/n for N=200 "
                "— not a proof of ER continuum limit theorems."
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
    rel = raw["primary"]["rel_err"]
    expected = "SUPPORTED" if rel <= REL_TOL else "REJECTED"
    if raw["decision"] != expected:
        ok = False
        checks.append(f"decision {raw['decision']} != expected {expected}")
    else:
        checks.append("decision matches prereg band rule")
    # monotonicity soft check: giant rate should generally increase with p
    rates = raw["primary"]["giant_rates"]
    if rates[-1] + 1e-9 < rates[0]:
        ok = False
        checks.append("giant_rate not increasing overall")
    else:
        checks.append("giant_rate increases overall")
    return ("PASS" if ok else "FAIL", checks)


if __name__ == "__main__":
    import json

    out = run_experiment()
    print(
        json.dumps(
            {
                "decision": out["decision"],
                "p50": out["primary"]["p50"],
                "p_c": out["primary"]["p_c"],
                "rel_err": out["primary"]["rel_err"],
            },
            indent=2,
        )
    )
