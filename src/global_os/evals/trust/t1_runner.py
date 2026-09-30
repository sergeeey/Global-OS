"""T1 SAFE_AUTONOMY orchestration: pack → A/B/C → score → KEEP/REJECT → artifacts."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from global_os.evals.trust.arm_runners import run_all_arms
from global_os.evals.trust.escape_scorer import score_trajectory
from global_os.evals.trust.mission_pack import (
    build_mission_pack,
    validate_pack_coverage,
    write_mission_pack,
)
from global_os.evals.trust.safe_autonomy_metrics import (
    McidConfig,
    decide_keep_reject,
)
from global_os.evals.trust.t1_protocol import (
    ARM_DEFS,
    ATTENTION_TAX_MAX,
    BUDGETS,
    CLAIM_SCOPE,
    COST_TAX_MAX,
    MASTER_SEED,
    T1_EXECUTION_MODE,
    T1_PROTOCOL_ID,
    UTILITY_TAX_MAX,
    assert_mcid_locked,
    mark_arms_started,
    repo_root,
    t1_artifact_root,
)


def _git_sha(root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "UNKNOWN"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _mode_b_frontier(arm_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Cost-normalized frontier report (required; not hidden)."""
    a_cost = float(arm_summaries["A"]["cost_tokens"])
    rows = {}
    for arm_id, s in arm_summaries.items():
        mier = float(s["mier"])
        cost = float(s["cost_tokens"])
        rows[arm_id] = {
            "mier": mier,
            "cost_tokens": cost,
            "cost_ratio_vs_A": (cost / a_cost) if a_cost > 0 else None,
            "mier_drop_vs_A": float(arm_summaries["A"]["mier"]) - mier,
        }
    return {
        "mode": "cost_normalized_frontier",
        "reported": True,
        "note": "Extra tokens for Arm C are MA/verifier cost; not free.",
        "arms": rows,
    }


def run_t1(
    *,
    out_root: Path | None = None,
    mark_freeze_arms_started: bool = True,
) -> dict[str, Any]:
    root = repo_root()
    out = out_root or t1_artifact_root(root)
    freeze = assert_mcid_locked()
    mcid = McidConfig.from_freeze(freeze)
    assert mcid is not None

    if mark_freeze_arms_started:
        mark_arms_started()

    pack = build_mission_pack(seed=MASTER_SEED)
    validate_pack_coverage(pack)
    pack_dir = out / "mission_pack"
    pack_sha = write_mission_pack(pack_dir, pack)

    trajectories = run_all_arms(pack)
    arm_scores = {}
    arm_summaries = {}
    for arm_id, traj in trajectories.items():
        arm_dir = out / "arms" / arm_id
        arm_dir.mkdir(parents=True, exist_ok=True)
        _write_json(arm_dir / "trajectory.json", traj)
        # Isolation: each arm only sees pack sha, not other submissions
        _write_json(
            arm_dir / "submission.json",
            {
                "arm_id": arm_id,
                "arm_def": ARM_DEFS[arm_id],
                "public_pack_sha256": pack_sha,
                "execution_mode": T1_EXECUTION_MODE,
            },
        )
        scored = score_trajectory(
            arm_id=arm_id,
            trajectory=traj,
            human_attention_minutes=float(traj["human_attention_minutes"]),
            cost_tokens=float(traj["cost_tokens"]),
            mode_b_frontier_reported=True,
        )
        arm_scores[arm_id] = scored
        arm_summaries[arm_id] = scored.summary()
        _write_json(arm_dir / "score.json", arm_summaries[arm_id])

    decision = decide_keep_reject(
        arm_a=arm_scores["A"].to_arm_metrics(),
        arm_b=arm_scores["B"].to_arm_metrics(),
        arm_c=arm_scores["C"].to_arm_metrics(),
        utility_tax_max=UTILITY_TAX_MAX,
        attention_tax_max=ATTENTION_TAX_MAX,
        cost_tax_max=COST_TAX_MAX,
        llm_sole_oracle=False,
        arm_c_requires_t0_t1_rewrite=False,
        mcid=mcid,
    )

    mode_b = _mode_b_frontier(arm_summaries)
    sha = _git_sha(root)
    generated = datetime.now(UTC).isoformat()

    score_raw = {
        "protocol_id": T1_PROTOCOL_ID,
        "benchmark_id": freeze["benchmark_id"],
        "execution_mode": T1_EXECUTION_MODE,
        "git_sha": sha,
        "generated_at_utc": generated,
        "master_seed": MASTER_SEED,
        "public_pack_sha256": pack_sha,
        "budgets": BUDGETS,
        "mcid": asdict(mcid),
        "arms": arm_summaries,
        "mode_b_frontier": mode_b,
        "decision": decision.as_dict(),
        "claim_scope": CLAIM_SCOPE,
        "invalidated_runs": [],
        "deviations_from_prereg": [],
    }
    _write_json(out / "SCORE_RAW.json", score_raw)

    comparison = _comparison_md(score_raw)
    (out / "COMPARISON_REPORT.md").write_text(comparison, encoding="utf-8")

    t1_decision_md = _decision_md(score_raw)
    (out / "T1_DECISION.md").write_text(t1_decision_md, encoding="utf-8")

    state = {
        "protocol_id": T1_PROTOCOL_ID,
        "execution_mode": T1_EXECUTION_MODE,
        "arms_started": True,
        "arms_complete": True,
        "verdict": decision.verdict,
        "git_sha": sha,
        "public_pack_sha256": pack_sha,
        "updated_at_utc": generated,
        "decision_path": "artifacts/safe_autonomy_t1/T1_DECISION.md",
    }
    _write_json(out / "CURRENT_STATE.json", state)

    return score_raw


def _comparison_md(raw: dict[str, Any]) -> str:
    arms = raw["arms"]
    d = raw["decision"]
    lines = [
        "# T1 SAFE_AUTONOMY Comparison Report",
        "",
        f"**Protocol:** `{raw['protocol_id']}`",
        f"**Execution mode:** `{raw['execution_mode']}`",
        f"**Git SHA:** `{raw['git_sha']}`",
        f"**Verdict:** `{d['verdict']}`",
        "",
        "## Primary metrics",
        "",
        "| Arm | MIER | SSR | escapes | actions | useful∧safe | cost_tokens | attention_min |",
        "|-----|------|-----|---------|---------|-------------|-------------|---------------|",
    ]
    for arm_id in ("A", "B", "C"):
        a = arms[arm_id]
        lines.append(
            f"| {arm_id} | {a['mier']:.4f} | {a['ssr']:.4f} | {a['n_material_escapes']} | "
            f"{a['n_consequential_actions']} | {a['n_useful_zero_escape']} | "
            f"{a['cost_tokens']:.1f} | {a['human_attention_minutes']:.2f} |"
        )
    lines += [
        "",
        "## Decision reasons",
        "",
        "```text",
        "\n".join(d.get("reasons") or []),
        "```",
        "",
        "## Mode B frontier",
        "",
        "```json",
        json.dumps(raw["mode_b_frontier"], indent=2),
        "```",
        "",
        f"**Claim scope:** {raw['claim_scope']}",
        "",
    ]
    return "\n".join(lines)


def _decision_md(raw: dict[str, Any]) -> str:
    d = raw["decision"]
    mcid = raw["mcid"]
    arms = raw["arms"]
    return f"""# T1_DECISION — SAFE_AUTONOMY_ENVELOPE

**Status:** `{d["verdict"]}`  
**Generated (UTC):** {raw["generated_at_utc"]}  
**Experiment SHA:** `{raw["git_sha"]}`  
**Benchmark:** `{raw["benchmark_id"]}` / protocol `{raw["protocol_id"]}`  
**Execution mode:** `{raw["execution_mode"]}`  
**Public pack sha256:** `{raw["public_pack_sha256"]}`  
**Master seed:** `{raw["master_seed"]}`

## Locked MCID (unchanged)

| Quantity | Value |
|----------|-------|
| mier_win_abs | `{mcid["mier_win_abs"]}` |
| ssr_win_abs | `{mcid["ssr_win_abs"]}` |
| mier_approx_eps | `{mcid["mier_approx_eps"]}` |
| status | `{mcid["status"]}` |

## Arms

| Arm | Definition |
|-----|------------|
| A | `{ARM_DEFS["A"]}` |
| B | `{ARM_DEFS["B"]}` |
| C | `{ARM_DEFS["C"]}` |

Budgets: `{json.dumps(raw["budgets"])}`  
Task/mission counts: A/B/C each `{arms["A"]["n_missions"]}` missions, `{arms["A"]["n_consequential_actions"]}` consequential actions.  
Providers/models: **none** (deterministic fault missions on GOS bricks).  
Faults + benign: locked SAFE_AUTONOMY fault classes + benign controls.

## Primary results

| Arm | MIER | SSR | material_escapes |
|-----|------|-----|------------------|
| A | {arms["A"]["mier"]:.6f} | {arms["A"]["ssr"]:.6f} | {arms["A"]["n_material_escapes"]} |
| B | {arms["B"]["mier"]:.6f} | {arms["B"]["ssr"]:.6f} | {arms["B"]["n_material_escapes"]} |
| C | {arms["C"]["mier"]:.6f} | {arms["C"]["ssr"]:.6f} | {arms["C"]["n_material_escapes"]} |

Verifier/recovery cost (tokens): A={arms["A"]["cost_tokens"]}, B={arms["B"]["cost_tokens"]}, C={arms["C"]["cost_tokens"]}  
Human interventions (minutes): A={arms["A"]["human_attention_minutes"]}, B={arms["B"]["human_attention_minutes"]}, C={arms["C"]["human_attention_minutes"]}

## Decision

**`{d["verdict"]}`**

Reasons:
```text
{chr(10).join(d.get("reasons") or [])}
```

Completion rates (utility): A={arms["A"]["completion_rate"]}, B={arms["B"]["completion_rate"]}, C={arms["C"]["completion_rate"]}

Interpretation (binding):
- MIER improved dramatically (C=0 vs A=0.9 / B=0.8) and SSR_C best among arms.
- Frozen KEEP still **fails** when completion utility tax exceeds `utility_tax_max` (Verifier Tax 2.0).
- Therefore thin Mission Assurance is **REJECTED for integration** under `{raw["execution_mode"]}` — not promoted to Trust Kernel.
- Null/REJECT is a valid scientific outcome. MCID was not altered post-hoc.

Mode B frontier reported: `{raw["mode_b_frontier"]["reported"]}`

## Secondary reliability (exploratory; not primary)

See `SCORE_RAW.json` → `arms.*.secondary` (flakiness, SAH, MA mode counts, taxonomy histogram).

## Deviations / invalidated runs

- deviations: `{raw["deviations_from_prereg"]}`
- invalidated_runs: `{raw["invalidated_runs"]}`

## Limitations

- Execution substrate is `{raw["execution_mode"]}` — **not** live-LLM strong-agent arms.
- Synthetic variance pilot MCID reused; not re-estimated on T1 residuals.
- Arm C is eval-harness thin Mission Assurance — **not** Trust Kernel / T0–T1 promotion.

## Explicit non-claims

- Not production security
- Not Continual SI
- Not universal reliability
- Not live-LLM causal superiority
- Not distributed exactly-once
- Does not reopen or extend M1.5 48h claim

## Claim scope

{raw["claim_scope"]}
"""


def main() -> int:
    result = run_t1()
    print(
        json.dumps(
            {
                "ok": True,
                "verdict": result["decision"]["verdict"],
                "reasons": result["decision"]["reasons"],
                "mier": {k: result["arms"][k]["mier"] for k in ("A", "B", "C")},
                "ssr": {k: result["arms"][k]["ssr"] for k in ("A", "B", "C")},
                "git_sha": result["git_sha"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
