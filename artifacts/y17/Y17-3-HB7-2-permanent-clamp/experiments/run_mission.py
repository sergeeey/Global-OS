"""Y17-3 — independent causal recompute of H-B7-2 permanent clamps (do(Rb=0), do(p27=0)).

Imports Y-17 H-B7-1/H-B7-2 helpers read-only. Never writes into the Y-17 tree.
Different class from Y17-1 (Fisher) and Y17-2 (model selection): Boolean causal do-operator.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

Y17 = Path("/workspace/Y-17-100-gipotez/experiments")
H1 = Y17 / "20260906-kauffman-cellcycle-attractors-h1" / "run.py"
H2 = Y17 / "20260906-kauffman-cellcycle-perturbation-h2" / "run.py"
H2_PRIOR_METRICS = Y17 / "20260906-kauffman-cellcycle-perturbation-h2" / "metrics" / "run.json"
# Y-17 clone in this environment lacks experiments/.../data/*.bnet — fetch public source
# into Global OS artifacts (does not write into Y-17).
LOCAL_BNET = Path(__file__).resolve().parents[1] / "data" / "faure_cellcycle.bnet"
BNET_PUBLIC_URL = (
    "https://raw.githubusercontent.com/hklarner/pyboolnet/master/"
    "pyboolnet/repository/faure_cellcycle/faure_cellcycle.bnet"
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def run_experiment() -> dict[str, Any]:
    h1 = _load("y17_h1", H1)
    h2 = _load("y17_h2", H2)

    y17_data_missing = not (H1.parent / "data" / "faure_cellcycle.bnet").exists()
    if not LOCAL_BNET.exists():
        raise FileNotFoundError(
            f"missing local bnet at {LOCAL_BNET}; download from {BNET_PUBLIC_URL}"
        )
    text = LOCAL_BNET.read_text(encoding="utf-8")
    rules = h1.parse_bnet(text)
    node_names = [name for name, _ in rules]
    wild_type_rules = h1.compile_rules(rules)
    cycd_index = node_names.index("CycD")

    def is_cycd_zero(state_str: str) -> bool:
        return state_str[cycd_index] == "0"

    interventions: dict[str, Any] = {}
    for node in ("Rb", "p27"):
        clamped = h2.clamp_rule(wild_type_rules, node, False)
        result = h2.find_attractors_with_membership(node_names, clamped)
        cycd0_idx = {
            idx for s, idx in result["initial_state_to_attractor"].items() if is_cycd_zero(s)
        }
        types = {result["attractors"][idx]["type"] for idx in cycd0_idx}
        periods = sorted({result["attractors"][idx]["period"] for idx in cycd0_idx})
        interventions[f"do({node}=0)"] = {
            "n_attractors_total": result["n_attractors"],
            "attractors": result["attractors"],
            "cycd0_reaches_attractor_types": sorted(types),
            "cycd0_reaches_complex_attractor": "complex" in types,
            "cycd0_attractor_periods": periods,
            "n_cycd0_states": sum(
                1 for s in result["initial_state_to_attractor"] if is_cycd_zero(s)
            ),
        }

    rb = interventions["do(Rb=0)"]
    p27 = interventions["do(p27=0)"]

    # Primary (locked): Rb arm — complex attractor from CycD=0 region
    if rb["cycd0_reaches_complex_attractor"]:
        decision = "SUPPORTED"
        nulls: list[dict[str, Any]] = []
    else:
        decision = "REJECTED"
        nulls = [
            {
                "id": "rb_clamp_no_complex",
                "interpretation": "do(Rb=0) did not produce complex attractor in CycD=0 region",
            }
        ]

    contradictory: list[dict[str, Any]] = []
    if p27["cycd0_reaches_complex_attractor"]:
        contradictory.append(
            {
                "note": "do(p27=0) also reached complex — breaks expected Rb/p27 differential",
                "rule": "walled descriptive",
            }
        )
    elif decision != "SUPPORTED":
        contradictory.append(
            {
                "note": "both arms point-only — differential collapsed",
                "rule": "walled",
            }
        )

    prior_match: dict[str, Any] | None = None
    if H2_PRIOR_METRICS.exists():
        prior = json.loads(H2_PRIOR_METRICS.read_text(encoding="utf-8"))
        prior_match = {
            "rb_complex_prior": prior["interventions"]["do(Rb=0)"]["cycd0_reaches_complex_attractor"],
            "rb_complex_now": rb["cycd0_reaches_complex_attractor"],
            "p27_complex_prior": prior["interventions"]["do(p27=0)"]["cycd0_reaches_complex_attractor"],
            "p27_complex_now": p27["cycd0_reaches_complex_attractor"],
            "types_rb_match": (
                prior["interventions"]["do(Rb=0)"]["cycd0_reaches_attractor_types"]
                == rb["cycd0_reaches_attractor_types"]
            ),
            "types_p27_match": (
                prior["interventions"]["do(p27=0)"]["cycd0_reaches_attractor_types"]
                == p27["cycd0_reaches_attractor_types"]
            ),
        }
        if not prior_match["types_rb_match"] or not prior_match["types_p27_match"]:
            contradictory.append(
                {
                    "note": "independent recompute attractor-type set differs from H-B7-2 committed metrics",
                    "prior_match": prior_match,
                    "rule": "report only — primary decision uses this run's kill criterion alone",
                }
            )

    rb_complex_attractors = [a for a in rb["attractors"] if a["type"] == "complex"]
    scope = {
        "rb_complex_periods": [a["period"] for a in rb_complex_attractors],
        "qualification": (
            "SUPPORTED means permanent do(Rb=0) yields complex attractor in CycD=0; "
            "does NOT claim the attractor pre-existed in the unperturbed network "
            "(H-B7-2 CONFIRMED-WEAKENED scope)."
        ),
    }

    return {
        "config": {
            "network": "Fauré et al. 2006 via public pyboolnet .bnet",
            "bnet_path": str(LOCAL_BNET),
            "bnet_public_url": BNET_PUBLIC_URL,
            "y17_data_dir_missing": y17_data_missing,
            "interventions": ["do(Rb=0)", "do(p27=0)"],
            "primary_arm": "do(Rb=0)",
            "update_scheme": "synchronous",
            "y17_writes": False,
        },
        "node_order": node_names,
        "interventions": interventions,
        "scope": scope,
        "prior_match": prior_match,
        "decision": decision,
        "nulls": nulls,
        "contradictory_evidence": contradictory,
        "p27_secondary_point_preserved": (not p27["cycd0_reaches_complex_attractor"]),
        "failure_cases_extra": (
            [
                {
                    "id": "Y17-3-FC-DATA",
                    "class": "ENVIRONMENT_GAP",
                    "title": "Y-17 clone missing data/*.bnet",
                    "detail": "Fetched public pyboolnet faure_cellcycle.bnet into Global OS artifacts only",
                }
            ]
            if y17_data_missing
            else []
        ),
    }


def decide_fn(raw: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    return raw["decision"], raw.get("nulls", [])


def deterministic_verify(raw: dict[str, Any]) -> tuple[str, list[str]]:
    checks: list[str] = []
    ok = True
    rb = raw["interventions"]["do(Rb=0)"]
    p27 = raw["interventions"]["do(p27=0)"]
    if rb["n_cycd0_states"] != 512:
        ok = False
        checks.append(f"expected 512 CycD=0 states, got {rb['n_cycd0_states']}")
    else:
        checks.append("512 CycD=0 states under do(Rb=0)")
    expected = "SUPPORTED" if rb["cycd0_reaches_complex_attractor"] else "REJECTED"
    if raw["decision"] != expected:
        ok = False
        checks.append("decision mismatches kill criterion")
    else:
        checks.append("decision matches kill criterion")
    if "complex" in p27["cycd0_reaches_attractor_types"] and "point" not in str(
        p27["cycd0_reaches_attractor_types"]
    ):
        # still OK computationally; just note
        checks.append("p27 arm types recorded")
    else:
        checks.append(f"p27 types={p27['cycd0_reaches_attractor_types']}")
    if raw["config"]["y17_writes"] is not False:
        ok = False
        checks.append("y17_writes flag must be false")
    else:
        checks.append("no Y-17 writes declared")
    return ("PASS" if ok else "FAIL", checks)


if __name__ == "__main__":
    out = run_experiment()
    print(
        json.dumps(
            {
                "decision": out["decision"],
                "rb": out["interventions"]["do(Rb=0)"]["cycd0_reaches_attractor_types"],
                "p27": out["interventions"]["do(p27=0)"]["cycd0_reaches_attractor_types"],
                "prior_match": out["prior_match"],
            },
            indent=2,
        )
    )
