"""Y22 Arm A — strong baseline evidence replay (public pack only).

No GOS loop. No sealed. No import of generator truth helpers.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARM = ROOT.parent
PUBLIC = ROOT / "public_pack.json"


def main() -> None:
    public = json.loads(PUBLIC.read_text(encoding="utf-8"))
    events = sorted(public["events"], key=lambda e: (e["t"], e["event_id"]))
    questions = public["questions"]
    interim = public.get("interim_prompt") or {}

    # fact_id -> claim payload
    claims: dict[str, dict] = {}
    active: set[str] = set()
    invalidated: list[str] = []
    # last-claim-wins per (subject, predicate) among still-active facts
    slot_to_fid: dict[tuple[str, str], str] = {}

    saw_retract_or_invalidate = False

    for e in events:
        et = e["type"]
        if et == "CLAIM":
            fid = e["fact_id"]
            claims[fid] = {
                "fact_id": fid,
                "subject": e["subject"],
                "predicate": e["predicate"],
                "value": e["value"],
                "source": e.get("source"),
                "t": e["t"],
            }
            active.add(fid)
            slot_to_fid[(e["subject"], e["predicate"])] = fid
        elif et in ("RETRACT", "INVALIDATE"):
            fid = e["fact_id"]
            saw_retract_or_invalidate = True
            if fid in active:
                active.discard(fid)
            if fid not in invalidated:
                invalidated.append(fid)
            # clear slot if it pointed at this fact
            for slot, cur in list(slot_to_fid.items()):
                if cur == fid:
                    del slot_to_fid[slot]
            # restore previous active claim for same slot if any remains
            c = claims.get(fid)
            if c:
                subj, pred = c["subject"], c["predicate"]
                candidates = [
                    claims[f]
                    for f in active
                    if claims[f]["subject"] == subj and claims[f]["predicate"] == pred
                ]
                if candidates:
                    best = max(candidates, key=lambda x: (x["t"], x["fact_id"]))
                    slot_to_fid[(subj, pred)] = best["fact_id"]

    # Rebuild slots strictly from remaining active (last t wins)
    by_slot: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for fid in active:
        c = claims[fid]
        by_slot[(c["subject"], c["predicate"])].append(c)
    slot_value: dict[tuple[str, str], str] = {}
    active_final: list[str] = []
    for slot, items in by_slot.items():
        best = max(items, key=lambda x: (x["t"], x["fact_id"]))
        slot_value[slot] = best["value"]
        active_final.append(best["fact_id"])
    # keep other non-conflicting active facts too (same slot already collapsed)
    for fid in sorted(active):
        if fid not in active_final:
            # only add if not superseded in slot
            c = claims[fid]
            if slot_to_fid.get((c["subject"], c["predicate"])) == fid or (
                c["subject"],
                c["predicate"],
            ) not in {
                (claims[a]["subject"], claims[a]["predicate"]) for a in active_final
            }:
                if fid not in active_final:
                    # already represented by best in slot
                    pass

    # Prefer only one active per slot (best)
    active_final = []
    for items in by_slot.values():
        best = max(items, key=lambda x: (x["t"], x["fact_id"]))
        active_final.append(best["fact_id"])

    final_answers = []
    for q in questions:
        key = (q["subject"], q["predicate"])
        val = slot_value.get(key)
        if val is None:
            # no active claim — leave blank marker (scorer will count miss)
            val = "UNKNOWN"
        final_answers.append({"question_id": q["question_id"], "value": val})

    # Interim: SRC7-SRC12 validity claim — drop if we saw any retract/invalidate
    # (conservative baseline: any correction stream falsifies blanket interim)
    dropped_interim = bool(saw_retract_or_invalidate)

    # Also drop interim if statement mentions SRC7-12 and we invalidated claims from those sources
    if interim and not dropped_interim:
        for fid in invalidated:
            src = (claims.get(fid) or {}).get("source") or ""
            if src.startswith("SRC") and src[3:].isdigit() and int(src[3:]) >= 7:
                dropped_interim = True
                break

    n_answered = sum(1 for a in final_answers if a["value"] != "UNKNOWN")
    decision = "SUPPORTED" if n_answered >= len(final_answers) * 0.75 and dropped_interim else "INCONCLUSIVE"

    submission = {
        "arm_id": "A",
        "final_answers": final_answers,
        "active_claims": sorted(active_final),
        "invalidated_claims": invalidated,
        "dropped_interim": dropped_interim,
        "decision": decision,
        "stop_reason": "baseline_chronological_replay_completed",
        "notes": (
            "Strong baseline: chronological CLAIM/RETRACT/INVALIDATE replay; "
            "last-active claim wins per (subject,predicate). No GOS loop. No sealed peek."
        ),
    }
    (ARM / "submission.json").write_text(json.dumps(submission, indent=2) + "\n", encoding="utf-8")
    (ROOT / "replay_summary.json").write_text(
        json.dumps(
            {
                "n_events": len(events),
                "n_active": len(active_final),
                "n_invalidated": len(invalidated),
                "n_answered": n_answered,
                "dropped_interim": dropped_interim,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "decision": decision,
        "active": len(active_final),
        "invalidated": len(invalidated),
        "answered": n_answered,
        "dropped_interim": dropped_interim,
    }, indent=2))


if __name__ == "__main__":
    main()
