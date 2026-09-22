"""Phase 6 — minimal org A vs B datapoint on Y17-3 compute (no H-ORG claim).

A: single solver runs full experiment once.
B: manager + specialized workers (parse | Rb-clamp | p27-clamp | decide).

Sample size = 1 task → INCONCLUSIVE_REAL_SAMPLE_TOO_SMALL by default.
"""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path
from typing import Any

OUT = Path("/workspace/artifacts/hardening/org_ab_y17_3.json")
RUN = Path("/workspace/artifacts/y17/Y17-3-HB7-2-permanent-clamp/experiments/run_mission.py")


def _load():
    spec = importlib.util.spec_from_file_location("y17_3_org", RUN)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _single(mod) -> dict[str, Any]:
    t0 = time.perf_counter()
    raw = mod.run_experiment()
    wall = time.perf_counter() - t0
    return {
        "mode": "A_single_solver",
        "wall_s": wall,
        "completion": raw["decision"] in {"SUPPORTED", "REJECTED", "WEAKENED", "INCONCLUSIVE"},
        "decision": raw["decision"],
        "escaped_errors": 0,
        "duplicate_work": 0,
        "information_loss": False,
        "human_intervention": 0,
        "evidence_integrity": raw["prior_match"]["types_rb_match"] and raw["p27_secondary_point_preserved"],
        "tokens_cost": None,
    }


def _manager_workers(mod) -> dict[str, Any]:
    """Split stages with explicit handoff dicts (no shared mutable goal overwrite)."""
    t0 = time.perf_counter()
    escaped = 0
    handoffs = 0
    try:
        h1 = mod._load("org_h1", mod.H1)
        h2 = mod._load("org_h2", mod.H2)
        text = mod.LOCAL_BNET.read_text(encoding="utf-8")
        # worker: parse
        rules = h1.parse_bnet(text)
        node_names = [name for name, _ in rules]
        wild = h1.compile_rules(rules)
        handoffs += 1
        parse_msg = {"node_names": node_names, "n_rules": len(rules)}

        cycd_index = node_names.index("CycD")

        def cycd0_types(clamped):
            result = h2.find_attractors_with_membership(node_names, clamped)
            idxs = {
                idx
                for s, idx in result["initial_state_to_attractor"].items()
                if s[cycd_index] == "0"
            }
            return sorted({result["attractors"][i]["type"] for i in idxs}), result

        # worker: Rb
        rb_types, rb_result = cycd0_types(h2.clamp_rule(wild, "Rb", False))
        handoffs += 1
        rb_msg = {"types": rb_types, "complex": "complex" in rb_types}

        # worker: p27
        p27_types, _ = cycd0_types(h2.clamp_rule(wild, "p27", False))
        handoffs += 1
        p27_msg = {"types": p27_types, "complex": "complex" in p27_types}

        # manager decide
        decision = "SUPPORTED" if rb_msg["complex"] else "REJECTED"
        handoffs += 1
        # information loss check: manager only saw type summaries, not full attractor lists
        info_loss = "attractors" not in rb_msg
        wall = time.perf_counter() - t0
        # duplicate: both workers re-enumerate full 1024-state space independently
        duplicate = 1  # intentional specialized parallel recompute of state space
        return {
            "mode": "B_manager_specialized_workers",
            "wall_s": wall,
            "completion": True,
            "decision": decision,
            "escaped_errors": escaped,
            "duplicate_work": duplicate,
            "information_loss": info_loss,
            "human_intervention": 0,
            "evidence_integrity": rb_msg["complex"] and (not p27_msg["complex"]),
            "tokens_cost": None,
            "handoffs": handoffs,
            "parse_summary": parse_msg,
            "rb_periods_visible_to_manager": False,
            "n_attractors_rb": rb_result["n_attractors"],
        }
    except Exception as e:  # noqa: BLE001 — record escaped error for org metrics
        return {
            "mode": "B_manager_specialized_workers",
            "wall_s": time.perf_counter() - t0,
            "completion": False,
            "decision": "INCONCLUSIVE",
            "escaped_errors": 1,
            "duplicate_work": 0,
            "information_loss": True,
            "human_intervention": 1,
            "evidence_integrity": False,
            "tokens_cost": None,
            "error": str(e),
        }


def main() -> dict[str, Any]:
    mod = _load()
    a = _single(mod)
    b = _manager_workers(mod)
    report = {
        "task": "Y17-3 permanent-clamp Boolean recompute",
        "sample_size": 1,
        "A": a,
        "B": b,
        "comparison": {
            "same_decision": a["decision"] == b["decision"],
            "wall_ratio_B_over_A": (b["wall_s"] / a["wall_s"]) if a["wall_s"] > 0 else None,
            "B_more_duplicate_work": b["duplicate_work"] > a["duplicate_work"],
            "B_information_loss_flag": b["information_loss"],
        },
        "verdict": "INCONCLUSIVE_REAL_SAMPLE_TOO_SMALL",
        "scientific_claim_accepted": False,
        "note": "First datapoint only; do not claim H-ORG supported.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"verdict": report["verdict"], "same_decision": report["comparison"]["same_decision"], "wall_A": a["wall_s"], "wall_B": b["wall_s"]}, indent=2))
    return report


if __name__ == "__main__":
    main()
