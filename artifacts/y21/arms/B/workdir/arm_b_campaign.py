"""Y21 Arm B — GOS research loop on public Mealy traces only.

Competing hypotheses with internal holdout exact-match falsification.
Does not read Arm A outputs or sealed GT.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARM = ROOT.parent
PUBLIC = ROOT / "public_pack.json"


def majority(counter: dict[int, int]) -> int:
    return max(counter.items(), key=lambda kv: (kv[1], -kv[0]))[0]


def load() -> dict:
    return json.loads(PUBLIC.read_text(encoding="utf-8"))


def split_train(train: list[dict], frac: float = 0.8) -> tuple[list[dict], list[dict]]:
    cut = int(len(train) * frac)
    return train[:cut], train[cut:]


def build_out_obs(train: list[dict]):
    out_obs: dict[tuple[int, ...], dict[int, dict[int, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )
    for tr in train:
        pref: tuple[int, ...] = ()
        for x, o in zip(tr["input"], tr["output"]):
            out_obs[pref][x][o] += 1
            pref = pref + (x,)
    return out_obs


def signature(out_obs, pref: tuple[int, ...]) -> tuple:
    row = []
    for x in (0, 1, 2):
        ctr = out_obs.get(pref, {}).get(x)
        row.append(majority(ctr) if ctr else -1)
    row2 = []
    for x in (0, 1, 2):
        if out_obs.get(pref, {}).get(x):
            p2 = pref + (x,)
            row2.append(
                tuple(
                    majority(out_obs.get(p2, {}).get(y, {-1: 1}))
                    if out_obs.get(p2, {}).get(y)
                    else -1
                    for y in (0, 1, 2)
                )
            )
        else:
            row2.append((-1, -1, -1))
    return (tuple(row), tuple(row2))


def learn_mealy(train: list[dict]):
    out_obs = build_out_obs(train)
    pref_to_state: dict[tuple, int] = {}
    sig_to_id: dict[tuple, int] = {}
    for p in sorted(out_obs.keys(), key=len):
        sig = signature(out_obs, p)
        if sig not in sig_to_id:
            sig_to_id[sig] = len(sig_to_id)
        pref_to_state[p] = sig_to_id[sig]

    lam_counts: dict[int, dict[int, dict[int, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )
    delta_counts: dict[int, dict[int, dict[int, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )
    for pref, s in pref_to_state.items():
        for x, ctr in out_obs.get(pref, {}).items():
            o = majority(ctr)
            lam_counts[s][x][o] += sum(ctr.values())
            nxt = pref + (x,)
            ns = pref_to_state.get(nxt, s)
            delta_counts[s][x][ns] += sum(ctr.values())

    states = sorted(set(pref_to_state.values()) or {0})
    lam: dict[int, dict[int, int]] = {s: {} for s in states}
    delta: dict[int, dict[int, int]] = {s: {} for s in states}
    for s in states:
        for x in (0, 1, 2):
            if lam_counts[s][x]:
                lam[s][x] = majority(lam_counts[s][x])
            else:
                glob: dict[int, int] = defaultdict(int)
                for s2 in states:
                    for o, c in lam_counts[s2][x].items():
                        glob[o] += c
                lam[s][x] = majority(glob) if glob else 0
            delta[s][x] = majority(delta_counts[s][x]) if delta_counts[s][x] else s
    start = pref_to_state.get((), states[0])
    return delta, lam, start, len(states)


def run_mealy(delta, lam, start, inputs: list[int]) -> list[int]:
    s = start
    outs: list[int] = []
    for x in inputs:
        outs.append(lam.get(s, {}).get(x, 0))
        s = delta.get(s, {}).get(x, s)
    return outs


def build_markov(train: list[dict], order: int):
    table: dict[tuple, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    sym_out: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for tr in train:
        hist: list[int] = []
        for x, o in zip(tr["input"], tr["output"]):
            ctx = tuple(hist[-order:])
            table[ctx + (-9, x)][o] += 1
            table[ctx][o] += 1
            sym_out[x][o] += 1
            hist.append(x)
    return table, sym_out


def run_markov(table, sym_out, inputs: list[int], order: int) -> list[int]:
    outs: list[int] = []
    hist: list[int] = []
    for x in inputs:
        ctx = tuple(hist[-order:])
        key = ctx + (-9, x)
        if table[key]:
            outs.append(majority(table[key]))
        elif table[ctx]:
            outs.append(majority(table[ctx]))
        elif sym_out[x]:
            outs.append(majority(sym_out[x]))
        else:
            outs.append(0)
        hist.append(x)
    return outs


def run_hybrid(delta, lam, start, table, sym_out, inputs: list[int], order: int) -> list[int]:
    """Mealy primary; if transition never observed strongly, Markov backoff."""
    # strength: use mealy always but blend — actually: run mealy, also compute markov,
    # prefer mealy unless state has weak lambda counts — simplified: average not possible for discrete.
    # Use Markov for first `order` steps then Mealy.
    m_out = run_markov(table, sym_out, inputs, order)
    y_out = run_mealy(delta, lam, start, inputs)
    return [m_out[i] if i < order else y_out[i] for i in range(len(inputs))]


def exact_rate(train: list[dict], predict_fn) -> float:
    if not train:
        return 0.0
    ok = 0
    for tr in train:
        if predict_fn(tr["input"]) == tr["output"]:
            ok += 1
    return ok / len(train)


def null_rate(train: list[dict], hold: list[dict]) -> float:
    # per-symbol majority from train
    sym_out: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for tr in train:
        for x, o in zip(tr["input"], tr["output"]):
            sym_out[x][o] += 1

    def pred(inputs: list[int]) -> list[int]:
        return [majority(sym_out[x]) if sym_out[x] else 0 for x in inputs]

    return exact_rate(hold, pred)


def main() -> None:
    public = load()
    train_all = public["train_traces"]
    predict_items = public["predict_inputs"]
    fit, hold = split_train(train_all, 0.8)

    hyp_log: list[dict] = []

    # H_B1 Mealy
    delta, lam, start, n_states = learn_mealy(fit)
    mae1 = exact_rate(hold, lambda inp: run_mealy(delta, lam, start, inp))
    hyp_log.append(
        {"id": "H_B1_mealy_merge", "hold_exact": mae1, "n_states": n_states, "decision": "candidate"}
    )

    # H_B2 Markov orders
    best_markov = None
    best_m = -1.0
    best_order = 3
    for order in (2, 3, 4, 5):
        table, sym_out = build_markov(fit, order)
        r = exact_rate(hold, lambda inp, o=order, t=table, s=sym_out: run_markov(t, s, inp, o))
        hyp_log.append({"id": f"H_B2_markov_{order}", "hold_exact": r, "decision": "candidate"})
        if r > best_m:
            best_m, best_order, best_markov = r, order, (table, sym_out)

    better_markov = best_m >= mae1 + 0.02
    hyp_log.append(
        {
            "id": "H_B2_markov_select",
            "best_order": best_order,
            "hold_exact": best_m,
            "beats_mealy": better_markov,
            "decision": "SUPPORTED" if better_markov else "REJECTED",
        }
    )

    # H_B3 hybrid
    table, sym_out = best_markov if best_markov else build_markov(fit, 3)
    # refit mealy on fit already have
    hyb = exact_rate(
        hold,
        lambda inp: run_hybrid(delta, lam, start, table, sym_out, inp, best_order),
    )
    base = max(mae1, best_m)
    path_helps = hyb >= base + 0.02
    hyp_log.append(
        {
            "id": "H_B3_hybrid",
            "hold_exact": hyb,
            "base": base,
            "decision": "SUPPORTED" if path_helps else "REJECTED",
        }
    )

    # H_B4 null
    nrate = null_rate(fit, hold)
    best = max(mae1, best_m, hyb)
    beats_null = best >= nrate + 0.02
    hyp_log.append(
        {
            "id": "H_B4_null",
            "hold_exact": nrate,
            "best": best,
            "beats_null": beats_null,
            "decision": "REJECTED" if beats_null else "SUPPORTED",
        }
    )

    # Select method for full-data refit
    if path_helps:
        method = "hybrid"
    elif better_markov:
        method = "markov"
    else:
        method = "mealy"

    # Refit on all train
    delta_f, lam_f, start_f, n_states_f = learn_mealy(train_all)
    table_f, sym_f = build_markov(train_all, best_order)

    def predict_one(inputs: list[int]) -> list[int]:
        if method == "hybrid":
            return run_hybrid(delta_f, lam_f, start_f, table_f, sym_f, inputs, best_order)
        if method == "markov":
            return run_markov(table_f, sym_f, inputs, best_order)
        return run_mealy(delta_f, lam_f, start_f, inputs)

    train_acc = exact_rate(train_all, predict_one)
    preds = [
        {"trace_id": item["trace_id"], "output": predict_one(item["input"])}
        for item in predict_items
    ]

    if not beats_null:
        decision = "INCONCLUSIVE"
        stop = "methods_not_above_null_on_internal_holdout"
    elif best >= 0.45:
        decision = "SUPPORTED"
        stop = "internal_holdout_selected_method_beats_null"
    else:
        decision = "INCONCLUSIVE"
        stop = "selected_method_weak_on_internal_holdout"

    submission = {
        "arm_id": "B",
        "predicted_outputs": preds,
        "claimed_n_states": n_states_f,
        "decision": decision,
        "stop_reason": stop,
        "notes": (
            f"GOS loop selected method={method}, order={best_order}, "
            f"hold_best={best:.3f}, train_exact={train_acc:.3f}, null={nrate:.3f}. "
            f"Sealed unseen; Arm A unread. hyp={hyp_log}"
        ),
    }
    (ARM / "submission.json").write_text(json.dumps(submission, indent=2) + "\n", encoding="utf-8")
    (ARM / "HYPOTHESIS_TRACE.json").write_text(json.dumps(hyp_log, indent=2) + "\n", encoding="utf-8")
    (ARM / "WHAT_WE_KNOW.md").write_text(
        f"# Arm B WHAT_WE_KNOW\n\n"
        f"- Selected method: `{method}` (order={best_order})\n"
        f"- Internal holdout best exact: `{best:.3f}` vs null `{nrate:.3f}`\n"
        f"- Decision: `{decision}`\n"
        f"- Sealed: UNSEEN · Arm A: UNREAD\n",
        encoding="utf-8",
    )
    (ARM / "CURRENT_STATE.json").write_text(
        json.dumps(
            {
                "arm": "B",
                "phase": "TERMINAL",
                "method": method,
                "decision": decision,
                "closed": {h["id"]: h.get("decision") for h in hyp_log},
                "gos_components_in_use": [
                    "goal_contract",
                    "competing_hypotheses",
                    "durable_research_state",
                    "falsification_internal_holdout",
                    "terminal_stop_rule",
                ],
                "sealed_unseen": True,
                "arm_a_outputs_unread": True,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"method": method, "decision": decision, "hold_best": best, "null": nrate}, indent=2))


if __name__ == "__main__":
    main()
