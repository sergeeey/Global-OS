"""Y20 — preregistered causal A/B harness (eval only, ADR-0009).

Synthetic statistical-causal world with sealed ground truth.
Arms receive only the public observational pack; scorer alone reads sealed GT.

Not a T0/T1 surface. Does not run Arm A/B.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

PROTOCOL_VERSION = "Y20-AB-v1"
MASTER_SEED = 20_250_925  # locked generator seed (sealed material derived from this)
N_VARS = 20
N_OBS = 2500
VAR_NAMES = tuple(f"X{i}" for i in range(N_VARS))

# Equal budget constants (immutable; must match Y20-PREREG.md)
BUDGETS: dict[str, int] = {
    "wall_seconds_max": 14400,
    "token_budget_max": 800000,
    "tool_calls_max": 400,
    "python_subprocess_max": 200,
}

Decision = Literal["SUPPORTED", "REJECTED", "INCONCLUSIVE"]


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    kind: str  # linear | quad | tanh


@dataclass(frozen=True)
class InterventionTarget:
    intervention_id: str
    do_var: str
    do_value: float
    target: str


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

        def random(self) -> float:
            return self.u32() / 0xFFFFFFFF

        def gauss(self) -> float:
            # Box-Muller
            u1 = max(self.random(), 1e-12)
            u2 = self.random()
            return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)

        def uniform(self, a: float, b: float) -> float:
            return a + (b - a) * self.random()

        def choice(self, seq: list[Any]) -> Any:
            return seq[self.u32() % len(seq)]

        def shuffle(self, xs: list[Any]) -> None:
            for i in range(len(xs) - 1, 0, -1):
                j = self.u32() % (i + 1)
                xs[i], xs[j] = xs[j], xs[i]

    return R(seed)


def _build_dag(seed: int = MASTER_SEED) -> dict[str, Any]:
    """Construct a fixed-topology SCM with confounders, mediators, nonlinearities."""
    rng = _rng(seed)
    order = list(VAR_NAMES)
    # Structural skeleton (indices in topological order 0..19)
    # Confounder C=X0 → X3, X5; mediator X3 → X8 → X12; nonlinear X5 → X12
    # Spurious: collider X7 ← X2 → X9 and X7 ← X4 creates selection-like assoc if conditioned,
    # plus correlated noise pair (X14, X17) without edge.
    structural: list[Edge] = [
        Edge("X0", "X3", "linear"),
        Edge("X0", "X5", "linear"),
        Edge("X1", "X3", "tanh"),
        Edge("X2", "X7", "linear"),
        Edge("X4", "X7", "linear"),
        Edge("X2", "X9", "quad"),
        Edge("X3", "X8", "linear"),
        Edge("X8", "X12", "linear"),
        Edge("X5", "X12", "quad"),
        Edge("X6", "X10", "tanh"),
        Edge("X9", "X13", "linear"),
        Edge("X10", "X13", "linear"),
        Edge("X8", "X15", "tanh"),
        Edge("X12", "X16", "linear"),
        Edge("X13", "X16", "quad"),
        Edge("X15", "X18", "linear"),
        Edge("X16", "X18", "tanh"),
        Edge("X11", "X19", "linear"),
        Edge("X18", "X19", "linear"),
    ]
    # Extra weak linear edges for density (still DAG)
    extras = [
        Edge("X1", "X6", "linear"),
        Edge("X4", "X11", "linear"),
        Edge("X7", "X14", "linear"),
        Edge("X9", "X14", "linear"),
    ]
    edges = structural + extras
    weights: dict[tuple[str, str], float] = {}
    for e in edges:
        base = rng.uniform(0.45, 1.25)
        sign = -1.0 if rng.random() < 0.35 else 1.0
        weights[(e.src, e.dst)] = sign * base

    # Correlated noise without edge: pair (X14 shared component already via parents;
    # add latent-like shared noise ids for X17 with X11 — observational association)
    shared_noise_pairs = [("X11", "X17")]

    return {
        "protocol_version": PROTOCOL_VERSION,
        "master_seed": seed,
        "variables": list(VAR_NAMES),
        "topo_order": order,
        "edges": [asdict(e) for e in edges],
        "weights": {f"{a}->{b}": w for (a, b), w in weights.items()},
        "shared_noise_pairs": [list(p) for p in shared_noise_pairs],
        "scoring_edge_set": [[e.src, e.dst] for e in structural],
    }


def _parents(world: dict[str, Any], node: str) -> list[Edge]:
    return [Edge(**e) for e in world["edges"] if e["dst"] == node]


def _link(kind: str, x: float) -> float:
    if kind == "linear":
        return x
    if kind == "quad":
        return x * x
    if kind == "tanh":
        return math.tanh(x)
    raise ValueError(f"unknown link kind {kind}")


def _sample_row(
    world: dict[str, Any],
    rng: Any,
    *,
    do: dict[str, float] | None = None,
) -> dict[str, float]:
    values: dict[str, float] = {}
    shared: dict[str, float] = {}
    for a, b in world["shared_noise_pairs"]:
        shared[f"{a}|{b}"] = rng.gauss()

    for node in world["topo_order"]:
        if do is not None and node in do:
            values[node] = float(do[node])
            continue
        total = 0.0
        for e in _parents(world, node):
            w = float(world["weights"][f"{e.src}->{e.dst}"])
            total += w * _link(e.kind, values[e.src])
        noise = 0.35 * rng.gauss()
        for a, b in world["shared_noise_pairs"]:
            if node in (a, b):
                noise += 0.55 * shared[f"{a}|{b}"]
        values[node] = total + noise
    return values


def _mean_under_do(
    world: dict[str, Any],
    do_var: str,
    do_value: float,
    target: str,
    *,
    n: int = 4000,
    seed: int,
) -> float:
    rng = _rng(seed)
    acc = 0.0
    for _ in range(n):
        row = _sample_row(world, rng, do={do_var: do_value})
        acc += row[target]
    return acc / n


def intervention_schedule(world: dict[str, Any]) -> list[InterventionTarget]:
    """Fixed sealed intervention targets (ids stable)."""
    return [
        InterventionTarget("I1", "X0", 1.5, "X12"),
        InterventionTarget("I2", "X3", -1.0, "X16"),
        InterventionTarget("I3", "X8", 2.0, "X18"),
        InterventionTarget("I4", "X5", 0.0, "X12"),
        InterventionTarget("I5", "X16", 1.0, "X19"),
    ]


def build_world(seed: int = MASTER_SEED) -> dict[str, Any]:
    return _build_dag(seed)


def generate_observational(world: dict[str, Any], *, n: int = N_OBS) -> list[dict[str, float]]:
    rng = _rng(int(world["master_seed"]) ^ 0xA5A5A5A5)
    return [_sample_row(world, rng) for _ in range(n)]


def build_sealed_pack(world: dict[str, Any] | None = None) -> dict[str, Any]:
    world = world or build_world()
    targets = intervention_schedule(world)
    truths = []
    for i, t in enumerate(targets):
        mu = _mean_under_do(
            world,
            t.do_var,
            t.do_value,
            t.target,
            seed=int(world["master_seed"]) + 1000 + i,
        )
        truths.append(
            {
                "intervention_id": t.intervention_id,
                "do_var": t.do_var,
                "do_value": t.do_value,
                "target": t.target,
                "true_mean": mu,
            }
        )
    return {
        "protocol_version": PROTOCOL_VERSION,
        "world": world,
        "intervention_truth": truths,
        "scoring_edges": world["scoring_edge_set"],
    }


def build_public_pack(world: dict[str, Any] | None = None) -> dict[str, Any]:
    world = world or build_world()
    rows = generate_observational(world)
    targets = intervention_schedule(world)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "variables": list(VAR_NAMES),
        "n_obs": len(rows),
        "rows": rows,
        "intervention_targets": [
            {
                "intervention_id": t.intervention_id,
                "do_var": t.do_var,
                "do_value": t.do_value,
                "target": t.target,
            }
            for t in targets
        ],
        "task": (
            "Recover a limited causal structure and predict E[target | do(do_var=do_value)] "
            "for each intervention_id. Ground truth is sealed."
        ),
        # Explicitly absent: edges, weights, true_mean, master_seed
    }


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _dir_sha256(path: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file():
            rel = p.relative_to(path).as_posix().encode()
            h.update(rel)
            h.update(p.read_bytes())
    return h.hexdigest()


def write_public_pack(out_dir: Path, public: dict[str, Any] | None = None) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    public = public or build_public_pack()
    # CSV
    csv_path = out_dir / "observational.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(VAR_NAMES))
        w.writeheader()
        for row in public["rows"]:
            w.writerow({k: f"{row[k]:.10g}" for k in VAR_NAMES})
    meta = {
        "protocol_version": public["protocol_version"],
        "variables": public["variables"],
        "n_obs": public["n_obs"],
        "intervention_targets": public["intervention_targets"],
        "task": public["task"],
        "submission_schema": {
            "claimed_edges": "list of [src,dst]",
            "intervention_predictions": "list of {intervention_id,target,predicted_mean}",
            "decision": "SUPPORTED|REJECTED|INCONCLUSIVE",
        },
        "forbidden": [
            "read artifacts/y20/sealed",
            "read generator master seed for answers",
            "unequal budget vs other arm",
        ],
    }
    (out_dir / "public_meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        "# Y20 public pack\n\n"
        "Observational data only. Sealed ground truth is NOT here.\n"
        "Predict interventions listed in `public_meta.json`.\n",
        encoding="utf-8",
    )
    return _dir_sha256(out_dir)


def write_sealed_pack(out_dir: Path, sealed: dict[str, Any] | None = None) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    sealed = sealed or build_sealed_pack()
    (out_dir / "WARNING.txt").write_text(
        "SEALED — for blind scorer only. Do not provide to Arm A/B prompts.\n",
        encoding="utf-8",
    )
    (out_dir / "world.json").write_text(
        json.dumps(sealed["world"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "intervention_truth.json").write_text(
        json.dumps(sealed["intervention_truth"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "scoring_edges.json").write_text(
        json.dumps(sealed["scoring_edges"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return _dir_sha256(out_dir)


def export_packs(
    *,
    public_dir: Path,
    sealed_dir: Path,
    seed: int = MASTER_SEED,
) -> dict[str, str]:
    world = build_world(seed)
    public_hash = write_public_pack(public_dir, build_public_pack(world))
    sealed_hash = write_sealed_pack(sealed_dir, build_sealed_pack(world))
    return {
        "protocol_version": PROTOCOL_VERSION,
        "public_pack_sha256": public_hash,
        "sealed_pack_sha256": sealed_hash,
    }


def public_pack_leaks_secrets(public: dict[str, Any]) -> list[str]:
    """Return list of leak field names if public pack exposes GT."""
    leaks: list[str] = []
    banned = {
        "edges",
        "weights",
        "scoring_edge_set",
        "scoring_edges",
        "intervention_truth",
        "true_mean",
        "master_seed",
        "world",
    }
    for k in banned:
        if k in public:
            leaks.append(k)
    for t in public.get("intervention_targets", []):
        if "true_mean" in t:
            leaks.append("intervention_targets.true_mean")
    return leaks


def score_submission(
    submission: dict[str, Any],
    sealed: dict[str, Any],
) -> dict[str, Any]:
    """Blind scientific scorer. Process/cost metrics supplied separately by operator log."""
    truth_edges = {tuple(e) for e in sealed["scoring_edges"]}
    claimed = submission.get("claimed_edges") or []
    claimed_set = {(str(a), str(b)) for a, b in claimed}
    tp = len(claimed_set & truth_edges)
    fp = len(claimed_set - truth_edges)
    fn = len(truth_edges - claimed_set)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    truth_by_id = {t["intervention_id"]: t for t in sealed["intervention_truth"]}
    preds = submission.get("intervention_predictions") or []
    abs_errs: list[float] = []
    missing = 0
    for p in preds:
        tid = str(p.get("intervention_id"))
        if tid not in truth_by_id:
            missing += 1
            continue
        true_mu = float(truth_by_id[tid]["true_mean"])
        pred_mu = float(p.get("predicted_mean"))
        abs_errs.append(abs(pred_mu - true_mu))
    for tid in truth_by_id:
        if not any(str(p.get("intervention_id")) == tid for p in preds):
            missing += 1
    mae = sum(abs_errs) / len(abs_errs) if abs_errs else float("inf")

    decision = submission.get("decision")
    if decision not in ("SUPPORTED", "REJECTED", "INCONCLUSIVE"):
        decision_ok = False
    else:
        decision_ok = True

    return {
        "protocol_version": PROTOCOL_VERSION,
        "edge_precision": precision,
        "edge_recall": recall,
        "edge_tp": tp,
        "edge_fp": fp,
        "edge_fn": fn,
        "intervention_mae": mae if mae != float("inf") else None,
        "intervention_n_scored": len(abs_errs),
        "intervention_missing": missing,
        "decision_field_ok": decision_ok,
        "claimed_edge_count": len(claimed_set),
        "truth_edge_count": len(truth_edges),
    }


def validate_budget_usage(usage: dict[str, Any], budgets: dict[str, int] | None = None) -> dict[str, Any]:
    budgets = budgets or BUDGETS
    violations: list[str] = []
    checked: dict[str, Any] = {}
    for key, cap in budgets.items():
        used_key = key.replace("_max", "_used")
        # also accept short names
        alts = [used_key, key.replace("_max", ""), key]
        used = None
        for a in alts:
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


def budgets_schema() -> dict[str, int]:
    return dict(BUDGETS)


PROCESS_LOG_REQUIRED: tuple[str, ...] = (
    "arm_id",
    "model_pin",
    "prereg_boundary_sha",
    "public_pack_sha256",
    "started_at",
    "ended_at",
    "wall_seconds_used",
    "token_budget_used",
    "tool_calls_used",
    "python_subprocess_used",
    "human_interventions",
    "dispatcher_asks",
    "hypotheses_tried",
    "failed_experiments",
    "unsupported_claims",
    "recovery_events",
    "state_loss_events",
    "premature_stop",
    "evidence_trace_completeness",
    "stop_reason",
    "submission_path",
)


def validate_process_log(log: dict[str, Any]) -> dict[str, Any]:
    """Validate arm process_log against prereg schema (does not touch science scorer)."""
    missing = [k for k in PROCESS_LOG_REQUIRED if k not in log]
    errors: list[str] = []
    if missing:
        errors.append(f"missing:{','.join(missing)}")
    if (
        "prereg_boundary_sha" in log
        and log.get("prereg_boundary_sha") not in (None, "278c10d")
        and log["prereg_boundary_sha"] != "278c10d"
    ):
        errors.append("prereg_boundary_sha_mismatch")
    if "evidence_trace_completeness" in log:
        try:
            v = float(log["evidence_trace_completeness"])
            if v < 0.0 or v > 1.0:
                errors.append("evidence_trace_completeness_range")
        except (TypeError, ValueError):
            errors.append("evidence_trace_completeness_type")
    budget_check = validate_budget_usage(
        {
            "wall_seconds_used": log.get("wall_seconds_used", 0),
            "token_budget_used": log.get("token_budget_used", 0),
            "tool_calls_used": log.get("tool_calls_used", 0),
            "python_subprocess_used": log.get("python_subprocess_used", 0),
        }
    )
    if not budget_check["ok"]:
        errors.extend(budget_check["violations"])
    return {"ok": not errors, "errors": errors, "budget": budget_check}
