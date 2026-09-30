"""T2 SAFE_AUTONOMY orchestration: SHA freeze → unseal PACK-v2 → A/B/C1/C2 → KEEP/REJECT."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from global_os.evals.trust.arm_runners import run_t2_arms
from global_os.evals.trust.escape_scorer import score_trajectory
from global_os.evals.trust.pack_v2 import (
    PACK_V2_ID,
    assert_pack_v2_integrity,
    pack_v2_root,
    unseal_pack_v2,
)
from global_os.evals.trust.t1_protocol import assert_mcid_locked, repo_root
from global_os.evals.trust.t2_metrics import (
    decide_t2_keep_reject,
    extract_t2_diagnostics,
)
from global_os.evals.trust.t2_protocol import (
    ARM_DEFS_T2,
    CLAIM_SCOPE_T2,
    FSR_MIN,
    MIER_ABS_CEILING,
    MIER_APPROX_EPS,
    MIER_WIN_ABS,
    SSR_WIN_ABS,
    STOP_RULE_ON_REJECT,
    T2_EXECUTION_MODE,
    T2_FAILURE_CLASS,
    T2_PROTOCOL_ID,
    assert_prereg_locked,
    t2_artifact_root,
    t2_experiment_sha_path,
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


def freeze_experiment_sha(*, root: Path | None = None, sha: str | None = None) -> str:
    """Write-once freeze of implementation SHA before PACK-v2 unseal."""
    r = root or repo_root()
    path = t2_experiment_sha_path(r)
    resolved = sha or _git_sha(r)
    if resolved == "UNKNOWN":
        raise ValueError("cannot freeze UNKNOWN git SHA")
    if path.is_file():
        existing = path.read_text(encoding="utf-8").strip()
        if existing != resolved:
            raise ValueError(
                f"T2_EXPERIMENT_SHA already frozen to {existing}; "
                f"refusing overwrite with {resolved}"
            )
        return existing
    path.write_text(resolved + "\n", encoding="utf-8")
    return resolved


def load_frozen_experiment_sha(*, root: Path | None = None) -> str:
    path = t2_experiment_sha_path(root)
    if not path.is_file():
        raise FileNotFoundError("T2_EXPERIMENT_SHA.txt missing — freeze SHA before unseal")
    sha = path.read_text(encoding="utf-8").strip()
    if not sha or sha == "UNKNOWN":
        raise ValueError("frozen experiment SHA invalid")
    return sha


def _mode_b_frontier(arm_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    a_cost = float(arm_summaries["A"]["cost_tokens"])
    rows = {}
    for arm_id, s in arm_summaries.items():
        cost = float(s["cost_tokens"])
        rows[arm_id] = {
            "mier": float(s["mier"]),
            "ssr": float(s["ssr"]),
            "cost_tokens": cost,
            "cost_ratio_vs_A": (cost / a_cost) if a_cost > 0 else None,
            "mier_drop_vs_A": float(arm_summaries["A"]["mier"]) - float(s["mier"]),
        }
    return {
        "mode": "cost_normalized_frontier",
        "reported": True,
        "note": "C1=containment-only; C2=selective recovery cost; not free.",
        "arms": rows,
    }


def run_t2(
    *,
    out_root: Path | None = None,
    freeze_sha: bool = True,
    unseal: bool = True,
    pack: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute T2. By default freezes SHA and unseals PACK-v2 (production path).

    Tests may pass ``pack=`` and ``unseal=False`` to avoid mutating sealed holdout.
    """
    root = repo_root()
    out = out_root or t2_artifact_root(root)
    out.mkdir(parents=True, exist_ok=True)

    assert_prereg_locked(root)
    assert_mcid_locked()
    artifact_root = t2_artifact_root(root).parent  # artifacts/safe_autonomy_t1
    assert_pack_v2_integrity(root=artifact_root)

    if freeze_sha:
        experiment_sha = freeze_experiment_sha(root=root)
    else:
        experiment_sha = load_frozen_experiment_sha(root=root)

    head = _git_sha(root)
    if head != "UNKNOWN" and head != experiment_sha:
        # Allow running from a later docs-only commit only if caller froze earlier;
        # record both for honesty.
        sha_note = f"frozen={experiment_sha}; head={head}"
    else:
        sha_note = experiment_sha

    if unseal:
        pack = unseal_pack_v2(
            root=artifact_root,
            experiment_sha=experiment_sha,
            protocol_id=T2_PROTOCOL_ID,
        )
    elif pack is None:
        raise ValueError("pack required when unseal=False")

    trajectories = run_t2_arms(pack)
    arm_scores = {}
    arm_summaries = {}
    for arm_id, traj in trajectories.items():
        arm_dir = out / "arms" / arm_id
        arm_dir.mkdir(parents=True, exist_ok=True)
        _write_json(arm_dir / "trajectory.json", traj)
        _write_json(
            arm_dir / "submission.json",
            {
                "arm_id": arm_id,
                "arm_def": ARM_DEFS_T2[arm_id],
                "pack_id": PACK_V2_ID,
                "execution_mode": T2_EXECUTION_MODE,
                "experiment_sha": experiment_sha,
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
        # Attach T2 router secondary for C2
        if arm_id == "C2":
            arm_summaries[arm_id]["secondary"] = {
                **arm_summaries[arm_id].get("secondary", {}),
                "router_actions": dict(traj.get("router_actions") or {}),
                "recovery_attempts": int(traj.get("recovery_attempts") or 0),
                "unsafe_recovery_escapes": int(traj.get("unsafe_recovery_escapes") or 0),
            }
        _write_json(arm_dir / "score.json", arm_summaries[arm_id])

    diag_c2 = extract_t2_diagnostics(trajectories["C2"])
    decision = decide_t2_keep_reject(
        arm_a=arm_scores["A"].to_arm_metrics(),
        arm_b=arm_scores["B"].to_arm_metrics(),
        arm_c1=arm_scores["C1"].to_arm_metrics(),
        arm_c2=arm_scores["C2"].to_arm_metrics(),
        diagnostics_c2=diag_c2,
        llm_sole_oracle=False,
        requires_t0_t1_rewrite=False,
        mode_b_frontier_reported=True,
    )

    mode_b = _mode_b_frontier(arm_summaries)
    generated = datetime.now(UTC).isoformat()

    # C1 reference diagnostics (containment-only salvage for contrast)
    diag_c1 = extract_t2_diagnostics(trajectories["C1"])

    score_raw = {
        "protocol_id": T2_PROTOCOL_ID,
        "pack_id": PACK_V2_ID,
        "execution_mode": T2_EXECUTION_MODE,
        "t1_failure_class": T2_FAILURE_CLASS,
        "experiment_sha": experiment_sha,
        "git_head": head,
        "sha_note": sha_note,
        "generated_at_utc": generated,
        "mcid_reuse": {
            "mier_win_abs": MIER_WIN_ABS,
            "ssr_win_abs": SSR_WIN_ABS,
            "mier_approx_eps": MIER_APPROX_EPS,
            "mier_abs_ceiling": MIER_ABS_CEILING,
            "fsr_min": FSR_MIN,
        },
        "arms": arm_summaries,
        "diagnostics": {
            "C1": diag_c1.as_dict(),
            "C2": diag_c2.as_dict(),
        },
        "mode_b_frontier": mode_b,
        "decision": decision.as_dict(),
        "stop_rule_on_reject": STOP_RULE_ON_REJECT,
        "claim_scope": CLAIM_SCOPE_T2,
        "h_trust_status": (
            "KEEP_CONTINUE_MISSION_ASSURANCE"
            if decision.verdict == "KEEP"
            else "PARKED" if decision.verdict == "REJECT" else "INVALID"
        ),
        "deviations_from_prereg": [],
        "invalidated_runs": [],
    }
    _write_json(out / "SCORE_RAW.json", score_raw)
    (out / "COMPARISON_REPORT.md").write_text(_comparison_md(score_raw), encoding="utf-8")
    (out / "T2_DECISION.md").write_text(_decision_md(score_raw), encoding="utf-8")

    state = {
        "protocol_id": T2_PROTOCOL_ID,
        "execution_mode": T2_EXECUTION_MODE,
        "pack_id": PACK_V2_ID,
        "arms_complete": True,
        "verdict": decision.verdict,
        "experiment_sha": experiment_sha,
        "h_trust_status": score_raw["h_trust_status"],
        "updated_at_utc": generated,
        "decision_path": "artifacts/safe_autonomy_t1/T2/T2_DECISION.md",
    }
    _write_json(out / "CURRENT_STATE.json", state)

    # Mirror PARKED stop-rule artifact at T1 root for discoverability
    if decision.verdict == "REJECT":
        park = {
            "status": "H_TRUST_PARKED",
            "reason": "T2_REJECT",
            "stop_rule": STOP_RULE_ON_REJECT,
            "experiment_sha": experiment_sha,
            "reasons": decision.reasons,
            "next": "M2_scientific_utility_Y19_plus",
            "no_t3_without_independent_evidence": True,
        }
        _write_json(t2_artifact_root(root).parent / "H_TRUST_PARKED.json", park)
        (t2_artifact_root(root).parent / "H_TRUST_PARKED.md").write_text(
            "# H_TRUST PARKED\n\n"
            f"**Trigger:** T2 REJECT under `{T2_PROTOCOL_ID}`\n"
            f"**Experiment SHA:** `{experiment_sha}`\n"
            f"**Stop rule:** `{STOP_RULE_ON_REJECT}`\n\n"
            "No T3/T4 rescue without independent new evidence + new prereg.\n"
            "Roadmap → M2 / scientific utility (Y19+).\n"
            "T1 REJECT under pack v1 remains immutable.\n",
            encoding="utf-8",
        )

    return score_raw


def _comparison_md(raw: dict[str, Any]) -> str:
    arms = raw["arms"]
    d = raw["decision"]
    diag = raw["diagnostics"]
    lines = [
        "# T2 SAFE_AUTONOMY Comparison Report",
        "",
        f"**Protocol:** `{raw['protocol_id']}`",
        f"**Pack:** `{raw['pack_id']}`",
        f"**Execution mode:** `{raw['execution_mode']}`",
        f"**Experiment SHA:** `{raw['experiment_sha']}`",
        f"**Verdict:** `{d['verdict']}`",
        f"**H_TRUST:** `{raw['h_trust_status']}`",
        "",
        "## Primary metrics",
        "",
        "| Arm | MIER | SSR | escapes | useful∧safe | cost_tokens |",
        "|-----|------|-----|---------|-------------|-------------|",
    ]
    for arm_id in ("A", "B", "C1", "C2"):
        a = arms[arm_id]
        lines.append(
            f"| {arm_id} | {a['mier']:.4f} | {a['ssr']:.4f} | {a['n_material_escapes']} | "
            f"{a['n_useful_zero_escape']} | {a['cost_tokens']:.1f} |"
        )
    lines += [
        "",
        "## T2 diagnostics (C2 primary; C1 reference)",
        "",
        "| Metric | C1 | C2 |",
        "|--------|----|----|",
        f"| FSR | {diag['C1']['fsr']:.4f} | {diag['C2']['fsr']:.4f} |",
        f"| HBR | {diag['C1']['hbr']:.4f} | {diag['C2']['hbr']:.4f} |",
        f"| URR | {diag['C1']['urr']:.4f} | {diag['C2']['urr']:.4f} |",
        "",
        "## Decision reasons",
        "",
        "```text",
        "\n".join(d.get("reasons") or []),
        "```",
        "",
        f"**Claim scope:** {raw['claim_scope']}",
        "",
    ]
    return "\n".join(lines)


def _decision_md(raw: dict[str, Any]) -> str:
    d = raw["decision"]
    arms = raw["arms"]
    diag = raw["diagnostics"]["C2"]
    mcid = raw["mcid_reuse"]
    stop = d.get("stop_rule") or "(none — KEEP)"
    return f"""# T2_DECISION — SAFE_AUTONOMY selective recovery

**Status:** `{d["verdict"]}`  
**H_TRUST:** `{raw["h_trust_status"]}`  
**Generated (UTC):** {raw["generated_at_utc"]}  
**Experiment SHA:** `{raw["experiment_sha"]}`  
**Protocol:** `{raw["protocol_id"]}`  
**Pack:** `{raw["pack_id"]}`  
**Execution mode:** `{raw["execution_mode"]}`  
**T1 failure class (diagnostic):** `{raw["t1_failure_class"]}`

## Mechanism under test

```text
fault → risk class → HARD_BLOCK | SAFE_RECOVERY → reverify → continue OR honest stop
```

Not Trust Kernel. Not T0/T1 rewrite. Not blind verifier weakening. Not T1 MCID rewrite.

## Reused MCID floors

| Quantity | Value |
|----------|-------|
| mier_win_abs | `{mcid["mier_win_abs"]}` |
| ssr_win_abs | `{mcid["ssr_win_abs"]}` |
| mier_approx_eps | `{mcid["mier_approx_eps"]}` |
| mier_abs_ceiling | `{mcid["mier_abs_ceiling"]}` |
| fsr_min | `{mcid["fsr_min"]}` |

## Arms

| Arm | Definition |
|-----|------------|
| A | `{ARM_DEFS_T2["A"]}` |
| B | `{ARM_DEFS_T2["B"]}` |
| C1 | `{ARM_DEFS_T2["C1"]}` |
| C2 | `{ARM_DEFS_T2["C2"]}` |

## Primary results

| Arm | MIER | SSR | material_escapes | completion |
|-----|------|-----|------------------|------------|
| A | {arms["A"]["mier"]:.6f} | {arms["A"]["ssr"]:.6f} | {arms["A"]["n_material_escapes"]} | {arms["A"]["completion_rate"]:.4f} |
| B | {arms["B"]["mier"]:.6f} | {arms["B"]["ssr"]:.6f} | {arms["B"]["n_material_escapes"]} | {arms["B"]["completion_rate"]:.4f} |
| C1 | {arms["C1"]["mier"]:.6f} | {arms["C1"]["ssr"]:.6f} | {arms["C1"]["n_material_escapes"]} | {arms["C1"]["completion_rate"]:.4f} |
| C2 | {arms["C2"]["mier"]:.6f} | {arms["C2"]["ssr"]:.6f} | {arms["C2"]["n_material_escapes"]} | {arms["C2"]["completion_rate"]:.4f} |

## T2 diagnostics (C2)

| Metric | Value |
|--------|-------|
| Fault Salvage Rate (FSR) | {diag["fsr"]:.4f} |
| Hard Block Rate (HBR) | {diag["hbr"]:.4f} |
| Unsafe Recovery Rate (URR) | {diag["urr"]:.4f} |
| useful recovered / recoverable | {diag["n_useful_recovered"]} / {diag["n_recoverable_fault_missions"]} |

## Decision

**`{d["verdict"]}`**

Reasons:
```text
{chr(10).join(d.get("reasons") or [])}
```

Stop rule: `{stop}`

## Interpretation

- T1 REJECT under pack v1 stands forever for that experiment.
- T2 asks whether selective bounded recovery raises fault salvage without material escapes.
- C1 remains containment-only reference; KEEP judged on **C2**.

## Explicit non-claims

- Not production security
- Not Trust Kernel / T0–T1 promotion
- Not live-LLM strong-agent arms
- Not M1.5 reopen
- Not T1 MCID rewrite

## Claim scope

{raw["claim_scope"]}
"""


def main() -> int:
    # Ensure pack root exists for integrity check messaging
    _ = pack_v2_root()
    result = run_t2()
    print(
        json.dumps(
            {
                "ok": True,
                "verdict": result["decision"]["verdict"],
                "h_trust_status": result["h_trust_status"],
                "reasons": result["decision"]["reasons"],
                "mier": {k: result["arms"][k]["mier"] for k in ("A", "B", "C1", "C2")},
                "ssr": {k: result["arms"][k]["ssr"] for k in ("A", "B", "C1", "C2")},
                "fsr_c2": result["diagnostics"]["C2"]["fsr"],
                "urr_c2": result["diagnostics"]["C2"]["urr"],
                "experiment_sha": result["experiment_sha"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
