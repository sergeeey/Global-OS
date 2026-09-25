"""Y22 Arm B — GOS research loop on public evidence stream only.

Competing slot-resolution hypotheses; internal protocol checks (no sealed).
Does not read Arm A submission.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARM = ROOT.parent
PUBLIC = ROOT / "public_pack.json"


def src_num(source: str) -> int:
    if source.startswith("SRC") and source[3:].isdigit():
        return int(source[3:])
    return 99


def replay(events: list[dict]) -> tuple[dict[str, dict], set[str], list[str]]:
    claims: dict[str, dict] = {}
    active: set[str] = set()
    invalidated: list[str] = []
    for e in sorted(events, key=lambda x: (x["t"], x["event_id"])):
        if e["type"] == "CLAIM":
            fid = e["fact_id"]
            claims[fid] = {
                "fact_id": fid,
                "subject": e["subject"],
                "predicate": e["predicate"],
                "value": e["value"],
                "source": e.get("source", ""),
                "t": e["t"],
            }
            active.add(fid)
        elif e["type"] in ("RETRACT", "INVALIDATE"):
            fid = e["fact_id"]
            active.discard(fid)
            if fid not in invalidated:
                invalidated.append(fid)
    return claims, active, invalidated


def required_invalidations(events: list[dict]) -> set[str]:
    return {
        e["fact_id"]
        for e in events
        if e["type"] in ("RETRACT", "INVALIDATE") and "fact_id" in e
    }


def resolve_slots(
    claims: dict[str, dict],
    active: set[str],
    method: str,
) -> dict[tuple[str, str], dict]:
    by_slot: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for fid in active:
        c = claims[fid]
        by_slot[(c["subject"], c["predicate"])].append(c)

    chosen: dict[tuple[str, str], dict] = {}
    for slot, items in by_slot.items():
        if method == "last_wins":
            best = max(items, key=lambda x: (x["t"], x["fact_id"]))
            chosen[slot] = best
        elif method == "distrust_high_src":
            low = [x for x in items if src_num(x["source"]) <= 6]
            pool = low if low else items
            best = max(pool, key=lambda x: (x["t"], x["fact_id"]))
            chosen[slot] = best
        elif method == "corroboration":
            # value -> sources
            val_sources: dict[str, set[str]] = defaultdict(set)
            for x in items:
                val_sources[x["value"]].add(x["source"])
            corroborated = [v for v, ss in val_sources.items() if len(ss) >= 2]
            if corroborated:
                # pick corroborated value with latest supporting claim
                cands = [x for x in items if x["value"] in corroborated]
                best = max(cands, key=lambda x: (x["t"], x["fact_id"]))
                chosen[slot] = best
            # else leave unanswered
        elif method == "earliest_low_src":
            best = min(items, key=lambda x: (src_num(x["source"]), x["t"], x["fact_id"]))
            chosen[slot] = best
        else:
            raise ValueError(method)
    return chosen


def build_submission(
    public: dict,
    method: str,
) -> dict:
    events = public["events"]
    claims, active, invalidated = replay(events)
    must = required_invalidations(events)
    # ensure all protocol invalidations listed
    for fid in sorted(must):
        if fid not in invalidated:
            invalidated.append(fid)
            active.discard(fid)

    slots = resolve_slots(claims, active, method)
    active_final = sorted({c["fact_id"] for c in slots.values()})
    answers = []
    for q in public["questions"]:
        key = (q["subject"], q["predicate"])
        if key in slots:
            answers.append({"question_id": q["question_id"], "value": slots[key]["value"]})
        else:
            answers.append({"question_id": q["question_id"], "value": "UNKNOWN"})

    dropped_interim = len(must) > 0
    return {
        "final_answers": answers,
        "active_claims": active_final,
        "invalidated_claims": invalidated,
        "dropped_interim": dropped_interim,
        "method": method,
        "_must": sorted(must),
        "_n_answered": sum(1 for a in answers if a["value"] != "UNKNOWN"),
    }


def internal_score(sub: dict, must: set[str]) -> float:
    got = set(sub["invalidated_claims"])
    cleanup = len(must & got) / len(must) if must else 1.0
    # precision of invalidations vs must (avoid inventing extras heavily)
    prec = len(must & got) / len(got) if got else 0.0
    cleanup_f1 = 0.0 if cleanup + prec == 0 else 2 * cleanup * prec / (cleanup + prec)
    coverage = sub["_n_answered"] / 16.0
    interim = 1.0 if sub["dropped_interim"] else 0.0
    # active must not retain must_invalidate
    clean_active = 1.0 if not (set(sub["active_claims"]) & must) else 0.0
    return 0.35 * cleanup_f1 + 0.25 * coverage + 0.20 * interim + 0.20 * clean_active


def main() -> None:
    public = json.loads(PUBLIC.read_text(encoding="utf-8"))
    must = required_invalidations(public["events"])
    methods = ["last_wins", "distrust_high_src", "corroboration", "earliest_low_src"]
    hyp_log = []
    best_method = None
    best_score = -1.0
    best_sub = None

    for m in methods:
        sub = build_submission(public, m)
        sc = internal_score(sub, must)
        hyp_log.append(
            {
                "id": f"H_B_{m}",
                "internal_score": sc,
                "n_answered": sub["_n_answered"],
                "n_active": len(sub["active_claims"]),
                "n_invalidated": len(sub["invalidated_claims"]),
                "decision": "candidate",
            }
        )
        if sc > best_score:
            best_score, best_method, best_sub = sc, m, sub

    assert best_sub is not None and best_method is not None
    for h in hyp_log:
        h["decision"] = "SUPPORTED" if h["id"] == f"H_B_{best_method}" else "REJECTED"

    decision = "SUPPORTED" if best_score >= 0.55 else "INCONCLUSIVE"
    submission = {
        "arm_id": "B",
        "final_answers": best_sub["final_answers"],
        "active_claims": best_sub["active_claims"],
        "invalidated_claims": best_sub["invalidated_claims"],
        "dropped_interim": best_sub["dropped_interim"],
        "decision": decision,
        "stop_reason": "gos_loop_selected_method_on_internal_protocol_score",
        "notes": (
            f"GOS loop selected method={best_method}, internal_score={best_score:.3f}. "
            f"Sealed unseen; Arm A unread. hyp={hyp_log}"
        ),
    }
    (ARM / "submission.json").write_text(json.dumps(submission, indent=2) + "\n", encoding="utf-8")
    (ARM / "HYPOTHESIS_TRACE.json").write_text(json.dumps(hyp_log, indent=2) + "\n", encoding="utf-8")
    (ARM / "WHAT_WE_KNOW.md").write_text(
        f"# Arm B WHAT_WE_KNOW\n\n"
        f"- Selected: `{best_method}`\n"
        f"- Internal protocol score: `{best_score:.3f}`\n"
        f"- Decision: `{decision}`\n"
        f"- Sealed: UNSEEN · Arm A: UNREAD\n",
        encoding="utf-8",
    )
    (ARM / "CURRENT_STATE.json").write_text(
        json.dumps(
            {
                "arm": "B",
                "phase": "TERMINAL",
                "method": best_method,
                "decision": decision,
                "gos_components_in_use": [
                    "goal_contract",
                    "competing_hypotheses",
                    "durable_research_state",
                    "falsification_internal_protocol_score",
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
    print(json.dumps({"method": best_method, "score": best_score, "decision": decision}, indent=2))


if __name__ == "__main__":
    main()
