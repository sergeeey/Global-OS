"""Y21 Arm A — strong baseline Mealy learner from public traces only.

No GOS loop. No sealed. No import of generator mealy tables.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARM = ROOT.parent
PUBLIC = Path("artifacts/y21/public/public_pack.json")


def load_public() -> dict:
    # Prefer local copy if present
    local = ROOT / "public_pack.json"
    path = local if local.is_file() else PUBLIC
    return json.loads(path.read_text(encoding="utf-8"))


def build_prefix_maps(train: list[dict]) -> tuple[dict, dict]:
    """Map prefix(tuple) -> observed next outputs by symbol; and transition counts."""
    # After consuming prefix p, on input x we saw output o and went to p+(x,)
    out_obs: dict[tuple[int, ...], dict[int, dict[int, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )
    for tr in train:
        inp, out = tr["input"], tr["output"]
        pref: tuple[int, ...] = ()
        for x, o in zip(inp, out):
            out_obs[pref][x][o] += 1
            pref = pref + (x,)
    return out_obs, {}


def majority(counter: dict[int, int]) -> int:
    return max(counter.items(), key=lambda kv: (kv[1], -kv[0]))[0]


def signature(out_obs: dict, pref: tuple[int, ...], depth: int = 2) -> tuple:
    """Finite signature of future I/O behavior from prefix (for state merging)."""
    parts: list[tuple] = []

    def walk(p: tuple[int, ...], d: int) -> None:
        if d == 0:
            return
        row = []
        for x in (0, 1, 2):
            ctr = out_obs.get(p, {}).get(x)
            if not ctr:
                row.append((-1, None))
            else:
                o = majority(ctr)
                row.append((o, "has"))
                walk(p + (x,), d - 1)
        parts.append((p[-1] if p else -1, tuple(row)))

    # Only use local outgoing distribution as signature (bounded)
    row = []
    for x in (0, 1, 2):
        ctr = out_obs.get(pref, {}).get(x)
        row.append(majority(ctr) if ctr else -1)
    # depth-2 signatures on reached prefs
    row2 = []
    for x in (0, 1, 2):
        if out_obs.get(pref, {}).get(x):
            p2 = pref + (x,)
            row2.append(tuple(majority(out_obs.get(p2, {}).get(y, { -1: 1 })) if out_obs.get(p2, {}).get(y) else -1 for y in (0, 1, 2)))
        else:
            row2.append((-1, -1, -1))
    return (tuple(row), tuple(row2))


def learn_states(out_obs: dict) -> dict[tuple, int]:
    """Assign state ids by signature clustering of observed prefixes."""
    prefs = list(out_obs.keys())
    # also include one-step extensions that appear as keys transitively
    sig_to_id: dict[tuple, int] = {}
    pref_to_state: dict[tuple, int] = {}
    for p in sorted(prefs, key=len):
        sig = signature(out_obs, p)
        if sig not in sig_to_id:
            sig_to_id[sig] = len(sig_to_id)
        pref_to_state[p] = sig_to_id[sig]
    return pref_to_state


def build_mealy_tables(
    out_obs: dict, pref_to_state: dict[tuple, int]
) -> tuple[dict[int, dict[int, int]], dict[int, dict[int, int]], int]:
    """Aggregate delta/lambda by state majority votes from prefix observations."""
    # state -> symbol -> counts of (next_state, output)
    lam_counts: dict[int, dict[int, dict[int, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    delta_counts: dict[int, dict[int, dict[int, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for pref, s in pref_to_state.items():
        for x, ctr in out_obs.get(pref, {}).items():
            o = majority(ctr)
            lam_counts[s][x][o] += sum(ctr.values())
            nxt_pref = pref + (x,)
            # map next prefix to state if known; else keep same signature attempt
            if nxt_pref in pref_to_state:
                ns = pref_to_state[nxt_pref]
            else:
                # fallback: signature of nxt if present in out_obs else s
                if nxt_pref in out_obs:
                    # find any pref with same sig
                    ns = pref_to_state.get(nxt_pref, s)
                else:
                    ns = s
            delta_counts[s][x][ns] += sum(ctr.values())

    states = sorted(set(pref_to_state.values()))
    lam: dict[int, dict[int, int]] = {s: {} for s in states}
    delta: dict[int, dict[int, int]] = {s: {} for s in states}
    for s in states:
        for x in (0, 1, 2):
            if lam_counts[s][x]:
                lam[s][x] = majority(lam_counts[s][x])
            else:
                # backoff global majority output for x across states
                glob: dict[int, int] = defaultdict(int)
                for s2 in states:
                    for o, c in lam_counts[s2][x].items():
                        glob[o] += c
                lam[s][x] = majority(glob) if glob else 0
            if delta_counts[s][x]:
                delta[s][x] = majority(delta_counts[s][x])
            else:
                delta[s][x] = s
    start = pref_to_state.get((), 0)
    return delta, lam, start


def run(delta: dict, lam: dict, start: int, inputs: list[int]) -> list[int]:
    s = start
    outs: list[int] = []
    for x in inputs:
        if s not in lam or x not in lam[s]:
            # unknown — predict 0
            outs.append(0)
            s = delta.get(s, {}).get(x, s)
            continue
        outs.append(lam[s][x])
        s = delta[s][x]
    return outs


def train_accuracy(train: list[dict], delta, lam, start: int) -> float:
    ok = 0
    for tr in train:
        pred = run(delta, lam, start, tr["input"])
        if pred == tr["output"]:
            ok += 1
    return ok / len(train) if train else 0.0


def main() -> None:
    public = load_public()
    train = public["train_traces"]
    predict = public["predict_inputs"]
    out_obs, _ = build_prefix_maps(train)
    pref_to_state = learn_states(out_obs)
    delta, lam, start = build_mealy_tables(out_obs, pref_to_state)
    acc = train_accuracy(train, delta, lam, start)

    # Hypothesis H1: signature-merge Mealy sufficient
    # If train exact-match low, try Markov order-3 backoff as H2 and pick better on train
    def markov_predict(inputs: list[int], order: int = 3) -> list[int]:
        # map context (last order inputs) -> output distribution from train alignments... 
        # simpler: use learned mealy only; markov on (prev inputs window)-> next out from flat events
        table: dict[tuple[int, ...], dict[int, int]] = defaultdict(lambda: defaultdict(int))
        for tr in train:
            hist: list[int] = []
            for x, o in zip(tr["input"], tr["output"]):
                ctx = tuple(hist[-order:])
                table[ctx][o] += 1
                # also condition lightly on x by appending x into ctx key
                table[ctx + (-9, x)][o] += 1
                hist.append(x)
        outs: list[int] = []
        hist = []
        for x in inputs:
            ctx = tuple(hist[-order:])
            key = ctx + (-9, x)
            if table[key]:
                outs.append(majority(table[key]))
            elif table[ctx]:
                outs.append(majority(table[ctx]))
            else:
                outs.append(lam.get(start, {}).get(x, 0))
            hist.append(x)
        return outs

    markov_ok = 0
    for tr in train:
        if markov_predict(tr["input"]) == tr["output"]:
            markov_ok += 1
    markov_acc = markov_ok / len(train)

    use_markov = markov_acc > acc + 0.02
    preds = []
    for item in predict:
        if use_markov:
            output = markov_predict(item["input"])
        else:
            output = run(delta, lam, start, item["input"])
        preds.append({"trace_id": item["trace_id"], "output": output})

    decision = "SUPPORTED" if max(acc, markov_acc) >= 0.5 else "INCONCLUSIVE"
    submission = {
        "arm_id": "A",
        "predicted_outputs": preds,
        "claimed_n_states": len(set(pref_to_state.values())),
        "decision": decision,
        "stop_reason": "baseline_learner_completed",
        "notes": (
            f"signature-merge Mealy train_exact={acc:.3f}; markov3 train_exact={markov_acc:.3f}; "
            f"selected={'markov3' if use_markov else 'mealy_merge'}. No sealed peek. No GOS loop."
        ),
    }
    (ARM / "submission.json").write_text(json.dumps(submission, indent=2) + "\n", encoding="utf-8")
    (ARM / "workdir" / "learner_summary.json").write_text(
        json.dumps(
            {
                "mealy_train_exact": acc,
                "markov_train_exact": markov_acc,
                "selected": "markov3" if use_markov else "mealy_merge",
                "n_states_claimed": len(set(pref_to_state.values())),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(submission["notes"], indent=2))
    print("n_pred", len(preds), "decision", decision)


if __name__ == "__main__":
    main()
