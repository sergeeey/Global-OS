"""Y22 — evidence-synthesis with invalidation/recovery A/B harness (ADR-0009).

Mechanism hypothesis (preregistered):
  If GOS value is reliability/provenance/recovery rather than raw reasoning,
  it should show primary composite gain on a long evidence stream with
  retractions, contradictions, and required claim cleanup — vs strong baseline.

NOT a rescue of Y20/Y21 exact-match nulls. Y20/Y21 scorers remain frozen forever.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = "Y22-AB-v1"
MASTER_SEED = 22_260_925

BUDGETS: dict[str, int] = {
    "wall_seconds_max": 14400,
    "token_budget_max": 800000,
    "tool_calls_max": 400,
    "python_subprocess_max": 200,
}

# Composite primary = weighted sum of component scores in [0,1]
# Weights frozen before arms.
WEIGHTS: dict[str, float] = {
    "final_factual_correctness": 0.35,
    "invalidated_claim_cleanup": 0.25,
    "unsupported_claims_score": 0.20,  # 1 - unsupported_rate
    "recovery_fidelity": 0.20,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9
PRIMARY_MCID = 0.05


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

        def choice(self, seq: list[Any]) -> Any:
            return seq[self.u32() % len(seq)]

        def shuffle(self, xs: list[Any]) -> None:
            for i in range(len(xs) - 1, 0, -1):
                j = self.u32() % (i + 1)
                xs[i], xs[j] = xs[j], xs[i]

    return R(seed)


@dataclass(frozen=True)
class Fact:
    fact_id: str
    subject: str
    predicate: str
    value: str
    true: bool  # ground-truth whether this holds in world


def build_world(seed: int = MASTER_SEED) -> dict[str, Any]:
    """Deterministic multi-phase evidence world with retractions/contradictions."""
    rng = _rng(seed)
    subjects = ["Alpha", "Beta", "Gamma", "Delta"]
    predicates = ["status", "owner", "region", "tier"]
    values = {
        "status": ["active", "paused", "retired"],
        "owner": ["OrgA", "OrgB", "OrgC"],
        "region": ["EU", "US", "APAC"],
        "tier": ["T1", "T2", "T3"],
    }

    # True world assignment
    truth: dict[tuple[str, str], str] = {}
    for s in subjects:
        for p in predicates:
            truth[(s, p)] = rng.choice(values[p])

    # Timeline events
    events: list[dict[str, Any]] = []
    sources = [f"SRC{i}" for i in range(1, 13)]
    fact_bank: list[dict[str, Any]] = []
    fid = 0

    def add_claim(t: int, source: str, subj: str, pred: str, val: str, *, reliable: bool) -> str:
        nonlocal fid
        fid += 1
        fact_id = f"F{fid:03d}"
        true_val = truth[(subj, pred)]
        is_true = val == true_val
        # unreliable sources may still randomly say truth
        item = {
            "fact_id": fact_id,
            "t": t,
            "source": source,
            "subject": subj,
            "predicate": pred,
            "value": val,
            "is_true": is_true,
            "reliable": reliable,
        }
        fact_bank.append(item)
        events.append(
            {
                "event_id": f"E{len(events)+1:03d}",
                "t": t,
                "type": "CLAIM",
                "source": source,
                "fact_id": fact_id,
                "subject": subj,
                "predicate": pred,
                "value": val,
            }
        )
        return fact_id

    # Phase 1: mixed claims (t=1..20)
    for t in range(1, 21):
        subj = rng.choice(subjects)
        pred = rng.choice(predicates)
        source = rng.choice(sources)
        reliable = source in sources[:6]
        if reliable and rng.randint(0, 9) < 8:
            val = truth[(subj, pred)]
        else:
            # inject error often for unreliable
            wrongs = [v for v in values[pred] if v != truth[(subj, pred)]]
            val = rng.choice(wrongs if (not reliable or rng.randint(0, 2) == 0) else values[pred])
            if reliable and rng.randint(0, 4) == 0:
                val = truth[(subj, pred)]
        add_claim(t, source, subj, pred, val, reliable=reliable)

    # Identify some false claims to retract later
    false_ids = [f["fact_id"] for f in fact_bank if not f["is_true"]]
    rng.shuffle(false_ids)
    retract_ids = false_ids[:6]
    contradict_pairs: list[tuple[str, str]] = []

    # Phase 2: retractions (t=21..26)
    for i, fact_id in enumerate(retract_ids):
        events.append(
            {
                "event_id": f"E{len(events)+1:03d}",
                "t": 21 + i,
                "type": "RETRACT",
                "fact_id": fact_id,
                "reason": "source_correction",
            }
        )

    # Phase 3: explicit contradictions (t=30..35) — new false claim then notice
    for i in range(4):
        subj = subjects[i % len(subjects)]
        pred = predicates[i % len(predicates)]
        source = sources[6 + (i % 6)]
        wrong = rng.choice([v for v in values[pred] if v != truth[(subj, pred)]])
        bad_id = add_claim(30 + i, source, subj, pred, wrong, reliable=False)
        notice_t = 36 + i
        events.append(
            {
                "event_id": f"E{len(events)+1:03d}",
                "t": notice_t,
                "type": "INVALIDATE",
                "fact_id": bad_id,
                "reason": "contradicted_by_audit",
            }
        )
        contradict_pairs.append((bad_id, f"audit_{i}"))

    must_invalidate = sorted(set(retract_ids + [p[0] for p in contradict_pairs]))

    # Intermediate trap: early summary that will be wrong if not updated
    intermediate_wrong = {
        "claim_id": "INTERIM_001",
        "t": 15,
        "statement": "All SRC7-SRC12 claims remain valid through end of mission.",
        "should_be_invalid_by_t": 40,
    }

    # Sealed questions about final true world
    questions = []
    for i, subj in enumerate(subjects):
        for j, pred in enumerate(predicates):
            questions.append(
                {
                    "question_id": f"Q{i}{j}",
                    "subject": subj,
                    "predicate": pred,
                    "answer": truth[(subj, pred)],
                }
            )

    # Recovery probe: after all invalidations, which interim must be dropped
    recovery = {
        "interim_claim_id": intermediate_wrong["claim_id"],
        "must_drop_by_final": True,
        "must_invalidate_fact_ids": must_invalidate,
    }

    return {
        "protocol_version": PROTOCOL_VERSION,
        "master_seed": seed,
        "truth": {f"{s}|{p}": v for (s, p), v in truth.items()},
        "events": events,
        "fact_bank": fact_bank,
        "questions": questions,
        "intermediate_trap": intermediate_wrong,
        "recovery": recovery,
        "must_invalidate": must_invalidate,
    }


def build_public_pack(world: dict[str, Any] | None = None) -> dict[str, Any]:
    world = world or build_world()
    # Public timeline: events without is_true / reliability labels
    public_events = []
    for e in world["events"]:
        pe = {k: v for k, v in e.items()}
        public_events.append(pe)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "task": (
            "Long evidence-synthesis mission. Ingest chronological events (CLAIMS, "
            "RETRACTs, INVALIDATEs). Some intermediate conclusions become invalid. "
            "Produce final answers and a cleaned claim set with provenance. "
            "Do not keep retracted/invalidated claims as active."
        ),
        "mechanism_hypothesis": (
            "GOS helps as reliability/provenance/recovery layer on stateful evidence "
            "change — not as raw reasoning amplifier (Y20/Y21 null on sealed exact tasks)."
        ),
        "events": public_events,
        "questions": [
            {
                "question_id": q["question_id"],
                "subject": q["subject"],
                "predicate": q["predicate"],
            }
            for q in world["questions"]
        ],
        "interim_prompt": {
            "claim_id": world["intermediate_trap"]["claim_id"],
            "t": world["intermediate_trap"]["t"],
            "statement": world["intermediate_trap"]["statement"],
            "note": "You may accept or reject this interim; final submission must reflect later evidence.",
        },
        "submission_schema": {
            "final_answers": "list of {question_id, value}",
            "active_claims": "list of fact_ids still believed",
            "invalidated_claims": "list of fact_ids dropped due to RETRACT/INVALIDATE",
            "dropped_interim": "bool — whether INTERIM_001 dropped by final",
            "decision": "SUPPORTED|REJECTED|INCONCLUSIVE",
        },
        "primary": {
            "type": "composite",
            "weights": WEIGHTS,
            "mcid": PRIMARY_MCID,
            "note": "Secondary process metrics cannot override composite primary.",
        },
        "forbidden": [
            "read artifacts/y22/sealed",
            "read world truth tables from generator",
            "unequal budget vs other arm",
            "retune Y20/Y21 scorers",
        ],
    }


def build_sealed_pack(world: dict[str, Any] | None = None) -> dict[str, Any]:
    world = world or build_world()
    return {
        "protocol_version": PROTOCOL_VERSION,
        "truth": world["truth"],
        "questions": world["questions"],
        "must_invalidate": world["must_invalidate"],
        "recovery": world["recovery"],
        "weights": WEIGHTS,
        "primary_mcid": PRIMARY_MCID,
        "allowed_true_fact_ids": [f["fact_id"] for f in world["fact_bank"] if f["is_true"]],
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
        "# Y22 public pack\n\n"
        "Chronological evidence stream with retractions/invalidations.\n"
        "Sealed answers are not here.\n",
        encoding="utf-8",
    )
    return _dir_sha256(out_dir)


def write_sealed_pack(out_dir: Path, sealed: dict[str, Any] | None = None) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    sealed = sealed or build_sealed_pack()
    (out_dir / "WARNING.txt").write_text(
        "SEALED — scorer only. Do not feed to Arm A/B.\n", encoding="utf-8"
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
        "generator_module_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def public_pack_leaks_secrets(public: dict[str, Any]) -> list[str]:
    leaks: list[str] = []
    banned = {"truth", "must_invalidate", "is_true", "allowed_true_fact_ids", "master_seed"}
    blob = json.dumps(public)
    for k in banned:
        if k in public:
            leaks.append(k)
    if '"is_true"' in blob:
        leaks.append("embedded_is_true")
    return leaks


def _component_scores(submission: dict[str, Any], sealed: dict[str, Any]) -> dict[str, float]:
    # 1) final factual correctness
    answers = {a["question_id"]: str(a.get("value")) for a in submission.get("final_answers") or []}
    ok = 0
    for q in sealed["questions"]:
        if answers.get(q["question_id"]) == q["answer"]:
            ok += 1
    factual = ok / len(sealed["questions"]) if sealed["questions"] else 0.0

    # 2) invalidated claim cleanup — F1 vs must_invalidate
    must = set(sealed["must_invalidate"])
    got = {str(x) for x in (submission.get("invalidated_claims") or [])}
    tp = len(must & got)
    precision = tp / len(got) if got else 0.0
    recall = tp / len(must) if must else 0.0
    cleanup = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)

    # 3) unsupported claims: active_claims that are not allowed true facts
    allowed = set(sealed["allowed_true_fact_ids"])
    active = {str(x) for x in (submission.get("active_claims") or [])}
    # also penalize keeping must_invalidate in active
    bad = active & must
    unsupported = active - allowed
    denom = max(len(active), 1)
    unsupported_rate = len(unsupported | bad) / denom
    unsupported_score = max(0.0, 1.0 - unsupported_rate)

    # 4) recovery fidelity: dropped interim + no must_invalidate left active
    dropped = bool(submission.get("dropped_interim"))
    clean_active = len(active & must) == 0
    recovery = (0.5 if dropped else 0.0) + (0.5 if clean_active else 0.0)

    return {
        "final_factual_correctness": factual,
        "invalidated_claim_cleanup": cleanup,
        "unsupported_claims_score": unsupported_score,
        "recovery_fidelity": recovery,
    }


def score_submission(submission: dict[str, Any], sealed: dict[str, Any]) -> dict[str, Any]:
    comps = _component_scores(submission, sealed)
    composite = sum(WEIGHTS[k] * comps[k] for k in WEIGHTS)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "primary_metric": "reliability_composite",
        "composite": composite,
        "components": comps,
        "weights": dict(WEIGHTS),
        "primary_mcid": PRIMARY_MCID,
        "decision_field_ok": submission.get("decision")
        in ("SUPPORTED", "REJECTED", "INCONCLUSIVE"),
    }


def compare_primary(score_a: dict[str, Any], score_b: dict[str, Any]) -> dict[str, Any]:
    a = float(score_a["composite"])
    b = float(score_b["composite"])
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
        "note": "Secondary process metrics cannot override this primary verdict.",
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
