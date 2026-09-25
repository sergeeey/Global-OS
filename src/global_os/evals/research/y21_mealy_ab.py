"""Y21 — algorithmic reverse-engineering A/B harness (eval only, ADR-0009).

Hidden Mealy machine: recover I/O behavior from observational traces.
Primary sealed metric: exact output-sequence match rate on holdout inputs.

Authorship note: this module defines the sealed generator. Arm runners must not
import world/GT helpers during arm execution — only consume artifacts/y21/public/.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = "Y21-AB-v1"
MASTER_SEED = 21_260_925
N_STATES = 4
INPUT_ALPH = (0, 1, 2)
OUTPUT_ALPH = (0, 1, 2)
N_TRAIN = 220
N_SEALED = 90
MIN_LEN = 6
MAX_LEN = 14

BUDGETS: dict[str, int] = {
    "wall_seconds_max": 14400,
    "token_budget_max": 800000,
    "tool_calls_max": 400,
    "python_subprocess_max": 200,
}

# Primary win: B exact_match_rate >= A + MCID (absolute)
PRIMARY_MCID = 0.05


@dataclass(frozen=True)
class Mealy:
    n_states: int
    # delta[state][symbol] -> next_state
    delta: tuple[tuple[int, ...], ...]
    # lambda_[state][symbol] -> output
    lambda_: tuple[tuple[int, ...], ...]
    start: int = 0


def _rng(seed: int) -> Any:
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

        def randint(self, a: int, b: int) -> int:
            return a + (self.u32() % (b - a + 1))

        def choice(self, seq: tuple[int, ...]) -> int:
            return seq[self.u32() % len(seq)]

    return R(seed)


def build_mealy(seed: int = MASTER_SEED) -> Mealy:
    rng = _rng(seed)
    delta: list[list[int]] = []
    lam: list[list[int]] = []
    for _s in range(N_STATES):
        drow = [rng.randint(0, N_STATES - 1) for _ in INPUT_ALPH]
        lrow = [rng.choice(OUTPUT_ALPH) for _ in INPUT_ALPH]
        delta.append(drow)
        lam.append(lrow)
    # Ensure mild connectivity from start by forcing a cycle cover on symbol 0
    for s in range(N_STATES):
        delta[s][0] = (s + 1) % N_STATES
    return Mealy(
        n_states=N_STATES,
        delta=tuple(tuple(r) for r in delta),
        lambda_=tuple(tuple(r) for r in lam),
        start=0,
    )


def run_mealy(m: Mealy, inputs: list[int]) -> list[int]:
    s = m.start
    outs: list[int] = []
    for x in inputs:
        outs.append(m.lambda_[s][x])
        s = m.delta[s][x]
    return outs


def _gen_inputs(rng: Any, n: int) -> list[list[int]]:
    traces: list[list[int]] = []
    for _ in range(n):
        length = rng.randint(MIN_LEN, MAX_LEN)
        traces.append([rng.choice(INPUT_ALPH) for _ in range(length)])
    return traces


def build_world(seed: int = MASTER_SEED) -> dict[str, Any]:
    m = build_mealy(seed)
    rng_train = _rng(seed ^ 0x11111111)
    rng_seal = _rng(seed ^ 0x22222222)
    train_in = _gen_inputs(rng_train, N_TRAIN)
    seal_in = _gen_inputs(rng_seal, N_SEALED)
    train = [
        {
            "trace_id": f"T{i:03d}",
            "input": inp,
            "output": run_mealy(m, inp),
        }
        for i, inp in enumerate(train_in)
    ]
    sealed = [
        {
            "trace_id": f"S{i:03d}",
            "input": inp,
            "output": run_mealy(m, inp),
        }
        for i, inp in enumerate(seal_in)
    ]
    return {
        "protocol_version": PROTOCOL_VERSION,
        "master_seed": seed,
        "mealy": {
            "n_states": m.n_states,
            "delta": [list(r) for r in m.delta],
            "lambda": [list(r) for r in m.lambda_],
            "start": m.start,
            "input_alphabet": list(INPUT_ALPH),
            "output_alphabet": list(OUTPUT_ALPH),
        },
        "train": train,
        "sealed": sealed,
    }


def build_public_pack(world: dict[str, Any] | None = None) -> dict[str, Any]:
    world = world or build_world()
    return {
        "protocol_version": PROTOCOL_VERSION,
        "task": (
            "Reverse-engineer the hidden deterministic transducer from observational "
            "input/output traces. Predict output sequences for sealed holdout inputs."
        ),
        "input_alphabet": list(INPUT_ALPH),
        "output_alphabet": list(OUTPUT_ALPH),
        "train_traces": [
            {"trace_id": t["trace_id"], "input": t["input"], "output": t["output"]}
            for t in world["train"]
        ],
        "predict_inputs": [
            {"trace_id": t["trace_id"], "input": t["input"]} for t in world["sealed"]
        ],
        "submission_schema": {
            "predicted_outputs": "list of {trace_id, output: list[int]}",
            "claimed_n_states": "optional int",
            "decision": "SUPPORTED|REJECTED|INCONCLUSIVE",
        },
        "primary_metric": "sealed_exact_match_rate",
        "forbidden": [
            "read artifacts/y21/sealed",
            "import generator mealy tables for answers",
            "unequal budget vs other arm",
        ],
    }


def build_sealed_pack(world: dict[str, Any] | None = None) -> dict[str, Any]:
    world = world or build_world()
    return {
        "protocol_version": PROTOCOL_VERSION,
        "mealy": world["mealy"],
        "sealed_traces": world["sealed"],
        "primary_metric": "sealed_exact_match_rate",
        "primary_mcid": PRIMARY_MCID,
    }


def _dir_sha256(path: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file():
            h.update(p.relative_to(path).as_posix().encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def write_public_pack(out_dir: Path, public: dict[str, Any] | None = None) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    public = public or build_public_pack()
    (out_dir / "public_pack.json").write_text(
        json.dumps(public, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        "# Y21 public pack\n\n"
        "Observational transducer traces only. Predict outputs for `predict_inputs`.\n"
        "Sealed GT is not here.\n",
        encoding="utf-8",
    )
    return _dir_sha256(out_dir)


def write_sealed_pack(out_dir: Path, sealed: dict[str, Any] | None = None) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    sealed = sealed or build_sealed_pack()
    (out_dir / "WARNING.txt").write_text(
        "SEALED — scorer only. Do not provide to Arm A/B.\n", encoding="utf-8"
    )
    (out_dir / "sealed_pack.json").write_text(
        json.dumps(sealed, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return _dir_sha256(out_dir)


def export_packs(*, public_dir: Path, sealed_dir: Path, seed: int = MASTER_SEED) -> dict[str, str]:
    world = build_world(seed)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "public_pack_sha256": write_public_pack(public_dir, build_public_pack(world)),
        "sealed_pack_sha256": write_sealed_pack(sealed_dir, build_sealed_pack(world)),
        "generator_module_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
    }


def public_pack_leaks_secrets(public: dict[str, Any]) -> list[str]:
    leaks: list[str] = []
    banned = {"mealy", "delta", "lambda", "sealed_traces", "master_seed", "world"}
    for k in banned:
        if k in public:
            leaks.append(k)
    blob = json.dumps(public)
    if "delta" in blob and "mealy" in blob:
        leaks.append("embedded_mealy")
    return leaks


def score_submission(submission: dict[str, Any], sealed: dict[str, Any]) -> dict[str, Any]:
    truth = {t["trace_id"]: t["output"] for t in sealed["sealed_traces"]}
    preds = submission.get("predicted_outputs") or []
    exact = 0
    hamming_ok = 0
    hamming_tot = 0
    missing = 0
    seen: set[str] = set()
    for p in preds:
        tid = str(p.get("trace_id"))
        if tid not in truth:
            missing += 1
            continue
        seen.add(tid)
        pred = [int(x) for x in (p.get("output") or [])]
        true = [int(x) for x in truth[tid]]
        if pred == true:
            exact += 1
        n = max(len(pred), len(true))
        for i in range(n):
            hamming_tot += 1
            a = pred[i] if i < len(pred) else None
            b = true[i] if i < len(true) else None
            if a == b:
                hamming_ok += 1
    for tid in truth:
        if tid not in seen:
            missing += 1
    n_truth = len(truth)
    exact_rate = exact / n_truth if n_truth else 0.0
    hamming_acc = hamming_ok / hamming_tot if hamming_tot else 0.0
    decision = submission.get("decision")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "primary_metric": "sealed_exact_match_rate",
        "sealed_exact_match_rate": exact_rate,
        "sealed_exact_matches": exact,
        "sealed_n": n_truth,
        "hamming_accuracy": hamming_acc,
        "missing_or_extra": missing,
        "decision_field_ok": decision in ("SUPPORTED", "REJECTED", "INCONCLUSIVE"),
        "primary_mcid": PRIMARY_MCID,
    }


def compare_primary(score_a: dict[str, Any], score_b: dict[str, Any]) -> dict[str, Any]:
    a = float(score_a["sealed_exact_match_rate"])
    b = float(score_b["sealed_exact_match_rate"])
    if b >= a + PRIMARY_MCID:
        verdict = "B_WINS_PRIMARY"
    elif a >= b + PRIMARY_MCID:
        verdict = "A_WINS_PRIMARY"
    else:
        verdict = "TIE_WITHIN_MCID"
    return {
        "verdict": verdict,
        "a": a,
        "b": b,
        "mcid": PRIMARY_MCID,
        "note": "Secondary metrics must not override this primary verdict.",
    }


def validate_budget_usage(usage: dict[str, Any], budgets: dict[str, int] | None = None) -> dict[str, Any]:
    budgets = budgets or BUDGETS
    violations: list[str] = []
    checked: dict[str, Any] = {}
    for key, cap in budgets.items():
        used = None
        for a in (key.replace("_max", "_used"), key.replace("_max", ""), key):
            if a in usage:
                used = usage[a]
                break
        if used is None:
            violations.append(f"missing_usage:{key}")
            continue
        used_f = float(used)
        checked[key] = {"cap": cap, "used": used_f, "ok": used_f <= float(cap)}
        if used_f > float(cap):
            violations.append(f"exceeded:{key}")
    return {"ok": not violations, "violations": violations, "checked": checked}
