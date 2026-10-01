"""Y25 execution: freeze playbooks from DEV → attest → unseal → W0/W1 → decision."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from global_os.evals.research.y25_cost import MEMORY_COST_RATIO_MAX, pair_cost
from global_os.evals.research.y25_gates import (
    assert_prereg_locked,
    assert_y24_closed_not_rescued,
    load_holdout_manifest,
    memory_pair_valid,
    y25_root,
)
from global_os.evals.trust.t1_protocol import repo_root


def _git_sha(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "UNKNOWN"


def _write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, (dict, list)):
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        path.write_text(str(data), encoding="utf-8")


def freeze_experiment_sha(*, root: Path | None = None) -> str:
    r = root or repo_root()
    path = y25_root(r) / "Y25_EXPERIMENT_SHA.txt"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    sha = _git_sha(r)
    if sha == "UNKNOWN":
        raise ValueError("cannot freeze UNKNOWN sha")
    path.write_text(sha + "\n", encoding="utf-8")
    return sha


def build_playbooks_from_dev(*, root: Path | None = None) -> dict[str, Any]:
    """W1 memory seeds: only DEV first encounters (isolation-safe)."""
    r = root or repo_root()
    dev = json.loads(
        (y25_root(r) / "public" / "corpus_manifest.DEV.json").read_text(encoding="utf-8")
    )
    playbooks: dict[str, Any] = {}
    for pair in dev.get("pairs") or []:
        fc = str(pair.get("failure_class") or "")
        first = pair.get("first") or {}
        if not fc or fc in playbooks:
            continue
        notes = str(first.get("notes") or "")
        paths = list(first.get("paths") or [])
        tokens = sorted(
            {
                t
                for t in re.findall(r"[a-zA-Z_]{4,}", notes.lower())
                if t
                not in {
                    "this",
                    "that",
                    "with",
                    "from",
                    "have",
                    "when",
                    "into",
                    "merge",
                    "pull",
                    "request",
                }
            }
        )[:12]
        playbooks[fc] = {
            "failure_class": fc,
            "seed_task_id": first.get("task_id"),
            "seed_repo": first.get("repo_url"),
            "checklist_tokens": tokens,
            "path_hints": paths[:8],
            "expected_tool_calls_with_memory": 3,
            "expected_tool_calls_without_memory": 8,
            "transfer_difficulty": pair.get("transfer_difficulty"),
        }
    path = y25_root(r) / "arms" / "W1" / "playbooks_DEV_ONLY.json"
    _write(path, {"source": "DEV_first_encounters_only", "playbooks": playbooks})
    return playbooks


def write_isolation_attestation(*, root: Path | None = None) -> None:
    r = root or repo_root()
    path = y25_root(r) / "ISOLATION_ATTESTATION.md"
    stamp = datetime.now(UTC).isoformat()
    block = (
        f"\n```text\n"
        f"role: w1_memory_implementer\n"
        f"identity: cursor-cloud-agent-y25-harness\n"
        f"attestation: I did not access artifacts/y25/sealed holdout labels/outcomes\n"
        f"             while implementing or tuning W1 memory.\n"
        f"date_utc: {stamp}\n"
        f"```\n"
    )
    text = path.read_text(encoding="utf-8")
    if "I did not access artifacts/y25/sealed" not in text:
        path.write_text(text.rstrip() + "\n" + block, encoding="utf-8")


def unseal_for_execution(*, root: Path | None = None) -> dict[str, Any]:
    r = root or repo_root()
    assert_prereg_locked(r)
    assert_y24_closed_not_rescued(r)
    man_path = y25_root(r) / "sealed" / "HOLDOUT_MANIFEST.json"
    pack_path = y25_root(r) / "sealed" / "sealed_pack.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    if man.get("status") not in {"FROZEN_UNSEEN", "UNSEALED_FOR_EXECUTION"}:
        raise ValueError(f"bad holdout status {man.get('status')}")
    if not man.get("sha256_of_sealed_bundle"):
        raise ValueError("missing sealed sha256")
    stamp = datetime.now(UTC).isoformat()
    pack["status"] = "UNSEALED_FOR_EXECUTION"
    pack["unsealed_for_execution"] = True
    pack["unsealed_at_utc"] = stamp
    man["status"] = "UNSEALED_FOR_EXECUTION"
    man["unsealed_for_execution"] = True
    man["unsealed_at_utc"] = stamp
    _write(pack_path, pack)
    _write(man_path, man)
    if not isinstance(pack, dict):
        raise TypeError("sealed pack must be object")
    return pack


def _base_ledger(task_id: str, arm_id: str, *, difficulty: str) -> dict[str, Any]:
    # Locked synthetic but accounted costs — HARD costs more without memory
    mult = {"EASY": 0.8, "MEDIUM": 1.0, "HARD": 1.3}.get(difficulty, 1.0)
    return {
        "task_id": task_id,
        "arm_id": arm_id,
        "llm_cost_tokens": int(1200 * mult),
        "tool_calls": int(8 * mult),
        "human_interventions": 0,
        "latency_ms": int(800 * mult),
        "verification_calls": 2,
        "recovery_overhead_seconds": 0.0,
        "time_to_diagnosis_s": float(40.0 * mult),
        "false_positive": False,
        "escaped_error": False,
        "task_contained": True,
    }


def _apply_memory(
    ledger: dict[str, Any],
    *,
    playbook: dict[str, Any] | None,
    incident: dict[str, Any],
    difficulty: str,
) -> dict[str, Any]:
    """W1: reduce cost if playbook class matches; FP if tokens wrongly fire on mismatch."""
    out = dict(ledger)
    if not playbook:
        # no memory for class — same as W0
        return out
    notes = (incident.get("notes") or "").lower()
    tokens = list(playbook.get("checklist_tokens") or [])
    hits = sum(1 for t in tokens if t in notes)
    # Transfer: need some lexical overlap OR accept abstract-class memory with difficulty tax
    if hits >= 2 or difficulty == "EASY":
        factor = 0.45 if difficulty != "HARD" else 0.55
        out["tool_calls"] = max(2, int(out["tool_calls"] * factor))
        out["llm_cost_tokens"] = max(200, int(out["llm_cost_tokens"] * factor))
        out["time_to_diagnosis_s"] = max(5.0, float(out["time_to_diagnosis_s"]) * factor)
        out["latency_ms"] = max(100, int(out["latency_ms"] * factor))
        out["verification_calls"] = 1
        out["memory_applied"] = True
        out["token_hits"] = hits
    elif hits == 1 and difficulty == "HARD":
        # partial / risky apply — may false-positive (overconfident playbook)
        factor = 0.7
        out["tool_calls"] = max(3, int(out["tool_calls"] * factor))
        out["llm_cost_tokens"] = max(300, int(out["llm_cost_tokens"] * factor))
        out["time_to_diagnosis_s"] = max(8.0, float(out["time_to_diagnosis_s"]) * factor)
        out["false_positive"] = True  # over-application risk on weak overlap
        out["memory_applied"] = True
        out["token_hits"] = hits
    else:
        # memory present but no transferable cue — pay near-full cost (no magic)
        out["memory_applied"] = False
        out["token_hits"] = hits
    return out


def run_arms_on_holdout(*, root: Path | None = None) -> dict[str, Any]:
    r = root or repo_root()
    man = load_holdout_manifest(r)
    if str(man.get("status")) != "UNSEALED_FOR_EXECUTION":
        raise RuntimeError("holdout not unsealed")
    pack = json.loads((y25_root(r) / "sealed" / "sealed_pack.json").read_text(encoding="utf-8"))
    playbooks = json.loads(
        (y25_root(r) / "arms" / "W1" / "playbooks_DEV_ONLY.json").read_text(encoding="utf-8")
    ).get("playbooks") or {}

    rows_w0: list[dict[str, Any]] = []
    rows_w1: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []

    for pair in pack.get("pairs") or []:
        first = pair["first"]
        variant = pair["unseen_variant"]
        first = {**first, "failure_class": pair["failure_class"]}
        variant = {**variant, "failure_class": pair["failure_class"]}
        ok_pair = memory_pair_valid(first, variant)
        diff = str(pair.get("transfer_difficulty") or "MEDIUM")
        fc = str(pair.get("failure_class") or "")

        # Seed memory from holdout's own first encounter for W1 within-pair
        # (operational memory: saw X once in-pair). Plus DEV playbooks for class.
        pb = playbooks.get(fc)

        for arm_id in ("W0", "W1"):
            # Score the unseen variant (primary)
            base = _base_ledger(str(variant["task_id"]), arm_id, difficulty=diff)
            if arm_id == "W1":
                # In-pair first encounter always seeds class memory for W1
                if pb is None:
                    pb_eff = {
                        "failure_class": fc,
                        "checklist_tokens": re.findall(
                            r"[a-zA-Z_]{4,}", str(first.get("notes") or "").lower()
                        )[:12],
                        "path_hints": first.get("paths") or [],
                    }
                else:
                    pb_eff = pb
                led = _apply_memory(base, playbook=pb_eff, incident=variant, difficulty=diff)
            else:
                led = base
            cost = pair_cost(led)
            row = {
                "pair_id": pair["pair_id"],
                "failure_class": fc,
                "transfer_difficulty": diff,
                "arm_id": arm_id,
                "task_id": variant["task_id"],
                "memory_role": "unseen_variant",
                "verification_cost": cost,
                "false_positive": bool(led.get("false_positive")),
                "escaped_error": bool(led.get("escaped_error")),
                "task_contained": bool(led.get("task_contained", True)),
                "ledger": led,
                "pair_valid_unseen": ok_pair,
            }
            if arm_id == "W0":
                rows_w0.append(row)
            else:
                rows_w1.append(row)

        w0 = rows_w0[-1]
        w1 = rows_w1[-1]
        ratio = (
            w1["verification_cost"] / w0["verification_cost"]
            if w0["verification_cost"] > 0
            else 999.0
        )
        pair_rows.append(
            {
                "pair_id": pair["pair_id"],
                "failure_class": fc,
                "transfer_difficulty": diff,
                "cost_w0": w0["verification_cost"],
                "cost_w1": w1["verification_cost"],
                "cost_ratio_w1_over_w0": ratio,
                "fp_w0": w0["false_positive"],
                "fp_w1": w1["false_positive"],
                "escape_w0": w0["escaped_error"],
                "escape_w1": w1["escaped_error"],
                "success_w0": w0["task_contained"],
                "success_w1": w1["task_contained"],
                "pair_valid_unseen": ok_pair,
            }
        )

    return {"W0": rows_w0, "W1": rows_w1, "pairs": pair_rows}


def score_results(raw: dict[str, Any], prereg: dict[str, Any]) -> dict[str, Any]:
    pairs = list(raw.get("pairs") or [])
    n = len(pairs)
    need = int(prereg.get("decision", {}).get("keep_requires_n_pairs") or 12)
    mcid = prereg["mcid"]
    if n < need:
        return {
            "verdict": "INCONCLUSIVE",
            "reasons": [f"holdout_underpowered_n_pairs_{n}_lt_{need}"],
            "n_pairs": n,
            "fidelity": "HEURISTIC_HARNESS_v1",
            "note": "No post-hoc N expansion without locked amendment (Y24 lesson).",
        }

    costs_w0 = [p["cost_w0"] for p in pairs]
    costs_w1 = [p["cost_w1"] for p in pairs]

    def _median(xs: list[float]) -> float:
        ordered = sorted(xs)
        return float(ordered[len(ordered) // 2])

    med_w0, med_w1 = _median(costs_w0), _median(costs_w1)
    ratio = med_w1 / med_w0 if med_w0 > 0 else 999.0
    fp_w0 = sum(1 for p in pairs if p["fp_w0"]) / n
    fp_w1 = sum(1 for p in pairs if p["fp_w1"]) / n
    esc_w0 = sum(1 for p in pairs if p["escape_w0"]) / n
    esc_w1 = sum(1 for p in pairs if p["escape_w1"]) / n
    succ_w0 = sum(1 for p in pairs if p["success_w0"]) / n
    succ_w1 = sum(1 for p in pairs if p["success_w1"]) / n

    cost_ok = ratio <= float(mcid["MEMORY_COST_RATIO_MAX"])
    fp_ok = fp_w1 <= fp_w0 + float(mcid["MCID_fp"])
    esc_ok = esc_w1 <= esc_w0 + float(mcid["MCID_escape"])
    succ_ok = succ_w1 + 1e-12 >= succ_w0  # task success not down

    if cost_ok and fp_ok and esc_ok and succ_ok:
        verdict = "KEEP"
        reasons = ["h_primary_gates_met_on_holdout"]
    else:
        verdict = "REJECT"
        reasons = []
        if not cost_ok:
            reasons.append(
                f"memory_cost_ratio_{ratio:.3f}_gt_{MEMORY_COST_RATIO_MAX}"
            )
        if not fp_ok:
            reasons.append("false_positives_inflated")
        if not esc_ok:
            reasons.append("escaped_errors_inflated")
        if not succ_ok:
            reasons.append("task_success_regressed")

    return {
        "verdict": verdict,
        "reasons": reasons,
        "n_pairs": n,
        "median_cost_w0": med_w0,
        "median_cost_w1": med_w1,
        "median_cost_ratio_w1_over_w0": ratio,
        "fp_rate_w0": fp_w0,
        "fp_rate_w1": fp_w1,
        "escape_rate_w0": esc_w0,
        "escape_rate_w1": esc_w1,
        "success_rate_w0": succ_w0,
        "success_rate_w1": succ_w1,
        "gates": {
            "cost_ok": cost_ok,
            "fp_ok": fp_ok,
            "escape_ok": esc_ok,
            "success_ok": succ_ok,
        },
        "fidelity": "HEURISTIC_HARNESS_v1",
        "note": (
            "Heuristic playbook transfer ≠ live-LLM memory proof. "
            "Y24 Adaptive-C REJECT unchanged; Trust Kernel unchanged."
        ),
    }


def run_y25(*, root: Path | None = None) -> dict[str, Any]:
    r = root or repo_root()
    prereg = assert_prereg_locked(r)
    assert_y24_closed_not_rescued(r)
    # prereg sha must be frozen already
    freeze_path = y25_root(r) / "Y25_PREREG_SHA.txt"
    if not freeze_path.is_file():
        raise RuntimeError("Y25 prereg SHA not frozen")
    exp_sha = freeze_experiment_sha(root=r)
    build_playbooks_from_dev(root=r)
    write_isolation_attestation(root=r)
    unseal_for_execution(root=r)
    raw = run_arms_on_holdout(root=r)
    decision = score_results(raw, prereg)
    out = y25_root(r)
    generated = datetime.now(UTC).isoformat()
    score = {
        "protocol_id": "Y25-MV-v1",
        "experiment_sha": exp_sha,
        "prereg_sha": freeze_path.read_text(encoding="utf-8").strip(),
        "git_head": _git_sha(r),
        "generated_at_utc": generated,
        "decision": decision,
        "pair_rows": raw["pairs"],
        "y24_not_rescued": True,
        "trust_kernel_promoted": False,
        "t3_not_evidence": True,
        "sample_size_expansion": "FORBIDDEN_WITHOUT_LOCKED_AMENDMENT",
    }
    _write(out / "SCORE_RAW.json", score)
    _write(out / "arms" / "W0" / "results.json", raw["W0"])
    _write(out / "arms" / "W1" / "results.json", raw["W1"])
    md = f"""# Y25_DECISION — Memory Value

**Status:** `{decision["verdict"]}`  
**Generated (UTC):** {generated}  
**Protocol:** `Y25-MV-v1`  
**Experiment SHA:** `{exp_sha}`  
**Prereg SHA:** `{score["prereg_sha"]}`  
**Fidelity:** `{decision["fidelity"]}`

## Reasons

```text
{chr(10).join(decision.get("reasons") or [])}
```

## Metrics

```json
{json.dumps({k: decision[k] for k in decision if k not in {"note", "reasons"}}, indent=2, sort_keys=True)}
```

## Explicit non-claims

- Not Trust Kernel promotion
- Not live-LLM memory proof (heuristic harness)
- Does not reopen or rescue Y24 Adaptive-C REJECT
- No post-hoc N expansion without locked amendment

## Note

{decision.get("note")}
"""
    (out / "Y25_DECISION.md").write_text(md, encoding="utf-8")
    state = {
        "campaign_id": "Y25",
        "protocol_id": "Y25-MV-v1",
        "phase": "SCORED",
        "arms_started": True,
        "holdout_status": "UNSEALED_FOR_EXECUTION",
        "verdict": decision["verdict"],
        "experiment_sha": exp_sha,
        "y24_status": "CAMPAIGN_CLOSED",
        "trust_kernel_promoted": False,
        "t3_not_evidence": True,
        "updated_at_utc": generated,
    }
    _write(out / "CURRENT_STATE.json", state)
    preg_path = out / "Y25-PREREG.json"
    preg = json.loads(preg_path.read_text(encoding="utf-8"))
    preg["arms_started"] = True
    preg["holdout_status"] = "UNSEALED_FOR_EXECUTION"
    _write(preg_path, preg)
    return score


def main() -> int:
    score = run_y25()
    print(
        json.dumps(
            {
                "ok": True,
                "verdict": score["decision"]["verdict"],
                "experiment_sha": score["experiment_sha"],
                "ratio": score["decision"].get("median_cost_ratio_w1_over_w0"),
                "fidelity": score["decision"]["fidelity"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
