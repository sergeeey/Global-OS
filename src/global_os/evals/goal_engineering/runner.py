"""GE-STUDY-v1 experiment runner — reproducible, seed-locked."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from global_os.evals.goal_engineering import MASTER_SEED, PROTOCOL_VERSION
from global_os.evals.goal_engineering.agents import EpisodeResult, run_episode
from global_os.evals.goal_engineering.independent_evaluator import (
    EvalVerdict,
    evaluate,
)
from global_os.evals.goal_engineering.stats import Interval, bootstrap_diff_ci, bootstrap_mean_ci
from global_os.evals.goal_engineering.strategies import STRATEGY_IDS
from global_os.evals.goal_engineering.tasks import DOMAIN_IDS, all_task_specs, build_world


@dataclass
class TrialRow:
    trial_id: str
    seed: int
    strategy_id: str
    task_id: str
    domain: str
    oracle_success: float
    claimed_success: float
    false_claim: float
    evidence_fidelity: float
    autonomy: float  # 1 - interventions/budget proxy
    cost_tokens: int
    latency_ms: int
    steps: int
    details: dict[str, Any] = field(default_factory=dict)


def _autonomy(episode: EpisodeResult, budget: int) -> float:
    # Higher = more autonomous completion without human intervention
    interventions = float(episode.human_interventions)
    return max(0.0, 1.0 - interventions / max(budget, 1))


def run_trial(strategy_id: str, task_id: str, seed: int) -> TrialRow:
    spec = next(s for s in all_task_specs() if s.task_id == task_id)
    world = build_world(spec.domain, seed + spec.seed_offset)
    packet = spec.packets()[strategy_id]
    episode = run_episode(world, packet, seed)
    verdict: EvalVerdict = evaluate(world, episode)
    return TrialRow(
        trial_id=f"{strategy_id}:{task_id}:{seed}",
        seed=seed,
        strategy_id=strategy_id,
        task_id=task_id,
        domain=spec.domain,
        oracle_success=1.0 if verdict.oracle_success else 0.0,
        claimed_success=1.0 if episode.claimed_success else 0.0,
        false_claim=1.0 if verdict.false_claim else 0.0,
        evidence_fidelity=verdict.evidence_fidelity,
        autonomy=_autonomy(episode, int(world.state["budget_steps"])),
        cost_tokens=int(episode.token_cost),
        latency_ms=int(episode.wall_ms),
        steps=int(episode.steps),
        details={
            "claimed_blocked": episode.claimed_blocked,
            "missed_claim": verdict.missed_claim,
            "eval": verdict.details,
            "ledger_len": len(episode.evidence_ledger),
        },
    )


def run_suite(*, n_seeds: int = 20, master_seed: int = MASTER_SEED) -> list[TrialRow]:
    rows: list[TrialRow] = []
    specs = all_task_specs()
    for i in range(n_seeds):
        seed = master_seed + i * 97
        for spec in specs:
            for sid in STRATEGY_IDS:
                rows.append(run_trial(sid, spec.task_id, seed))
    return rows


def _metric_vectors(
    rows: list[TrialRow], strategy_id: str, metric: str, domain: str | None = None
) -> list[float]:
    out: list[float] = []
    for r in rows:
        if r.strategy_id != strategy_id:
            continue
        if domain is not None and r.domain != domain:
            continue
        out.append(float(getattr(r, metric)))
    return out


def summarize(rows: list[TrialRow]) -> dict[str, Any]:
    metrics = [
        "oracle_success",
        "claimed_success",
        "false_claim",
        "evidence_fidelity",
        "autonomy",
        "cost_tokens",
        "latency_ms",
        "steps",
    ]
    by_strategy: dict[str, Any] = {}
    for sid in STRATEGY_IDS:
        cell: dict[str, Any] = {"overall": {}, "by_domain": {}}
        for m in metrics:
            xs = _metric_vectors(rows, sid, m)
            ci = bootstrap_mean_ci(xs, seed=hash(sid + m) & 0xFFFFFFFF)
            cell["overall"][m] = _ci_dict(ci)
        for dom in DOMAIN_IDS:
            cell["by_domain"][dom] = {}
            for m in metrics:
                xs = _metric_vectors(rows, sid, m, domain=dom)
                ci = bootstrap_mean_ci(xs, seed=hash(sid + dom + m) & 0xFFFFFFFF)
                cell["by_domain"][dom][m] = _ci_dict(ci)
        by_strategy[sid] = cell

    contrasts: dict[str, Any] = {}
    for base in ("S_TRAD", "S_DETAIL"):
        for m in ("oracle_success", "false_claim", "evidence_fidelity", "cost_tokens", "latency_ms"):
            a = _metric_vectors(rows, "S_GE", m)
            b = _metric_vectors(rows, base, m)
            # For false_claim, lower is better — still report GE - base
            ci = bootstrap_diff_ci(a, b, seed=hash(f"GE-{base}-{m}") & 0xFFFFFFFF)
            contrasts[f"S_GE_minus_{base}__{m}"] = _ci_dict(ci)

    # Conditional winners by domain (oracle_success primary; ties listed)
    winners: dict[str, str] = {}
    for dom in DOMAIN_IDS:
        scores: dict[str, float] = {}
        for sid in STRATEGY_IDS:
            xs = _metric_vectors(rows, sid, "oracle_success", domain=dom)
            scores[sid] = sum(xs) / max(len(xs), 1)
        best_val = max(scores.values()) if scores else -1.0
        tied = [sid for sid, val in scores.items() if abs(val - best_val) < 1e-12]
        winners[dom] = "=".join(tied) if tied else "NONE"

    return {
        "protocol_version": PROTOCOL_VERSION,
        "n_trials": len(rows),
        "by_strategy": by_strategy,
        "contrasts_GE_minus_baseline": contrasts,
        "conditional_winners_oracle_success": winners,
        "fidelity": "deterministic_behavioral_agents",
        "live_llm": "NOT_EXECUTED",
    }


def _ci_dict(ci: Interval) -> dict[str, Any]:
    return {
        "estimate": ci.estimate,
        "ci90_low": ci.low,
        "ci90_high": ci.high,
        "n": ci.n,
        "level": ci.level,
    }


def hypothesis_verdicts(summary: dict[str, Any]) -> dict[str, Any]:
    """Map preregistered hypotheses to CONFIRMED / REJECTED / INCONCLUSIVE.

    Confirmation requires CI excluding 0 in the predicted direction on the
    primary metric, under this fidelity class only.
    """
    c = summary["contrasts_GE_minus_baseline"]

    def _pos(key: str) -> str:
        d = c[key]
        if d["ci90_low"] > 0:
            return "CONFIRMED"
        if d["ci90_high"] < 0:
            return "REJECTED"
        return "INCONCLUSIVE"

    def _neg(key: str) -> str:
        """Predicted GE - base < 0 (e.g. false_claim)."""
        d = c[key]
        if d["ci90_high"] < 0:
            return "CONFIRMED"
        if d["ci90_low"] > 0:
            return "REJECTED"
        return "INCONCLUSIVE"

    h = {
        "H1_GE_oracle_gt_TRAD": {
            "statement": (
                "S_GE oracle_success > S_TRAD on aggregate under GE-STUDY-v1 "
                "behavioral agents"
            ),
            "verdict": _pos("S_GE_minus_S_TRAD__oracle_success"),
            "estimate": c["S_GE_minus_S_TRAD__oracle_success"],
        },
        "H2_GE_oracle_gt_DETAIL": {
            "statement": (
                "S_GE oracle_success > S_DETAIL on aggregate under GE-STUDY-v1"
            ),
            "verdict": _pos("S_GE_minus_S_DETAIL__oracle_success"),
            "estimate": c["S_GE_minus_S_DETAIL__oracle_success"],
        },
        "H3_GE_false_claim_lt_TRAD": {
            "statement": "S_GE false_claim rate < S_TRAD",
            "verdict": _neg("S_GE_minus_S_TRAD__false_claim"),
            "estimate": c["S_GE_minus_S_TRAD__false_claim"],
        },
        "H4_GE_evidence_gt_baselines": {
            "statement": "S_GE evidence_fidelity > S_TRAD and > S_DETAIL",
            "verdict": (
                "CONFIRMED"
                if (
                    _pos("S_GE_minus_S_TRAD__evidence_fidelity") == "CONFIRMED"
                    and _pos("S_GE_minus_S_DETAIL__evidence_fidelity") == "CONFIRMED"
                )
                else (
                    "REJECTED"
                    if (
                        _pos("S_GE_minus_S_TRAD__evidence_fidelity") == "REJECTED"
                        or _pos("S_GE_minus_S_DETAIL__evidence_fidelity") == "REJECTED"
                    )
                    else "INCONCLUSIVE"
                )
            ),
            "estimate_vs_trad": c["S_GE_minus_S_TRAD__evidence_fidelity"],
            "estimate_vs_detail": c["S_GE_minus_S_DETAIL__evidence_fidelity"],
        },
        "H5_GE_not_free": {
            "statement": (
                "S_GE has higher cost_tokens or latency_ms than S_TRAD "
                "(reliability tax)"
            ),
            "verdict": (
                "CONFIRMED"
                if (
                    _pos("S_GE_minus_S_TRAD__cost_tokens") == "CONFIRMED"
                    or _pos("S_GE_minus_S_TRAD__latency_ms") == "CONFIRMED"
                )
                else (
                    "REJECTED"
                    if (
                        _pos("S_GE_minus_S_TRAD__cost_tokens") == "REJECTED"
                        and _pos("S_GE_minus_S_TRAD__latency_ms") == "REJECTED"
                    )
                    else "INCONCLUSIVE"
                )
            ),
            "estimate_cost": c["S_GE_minus_S_TRAD__cost_tokens"],
            "estimate_latency": c["S_GE_minus_S_TRAD__latency_ms"],
        },
    }
    return h


def run_and_seal(
    out_dir: Path,
    *,
    n_seeds: int = 20,
    master_seed: int = MASTER_SEED,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = run_suite(n_seeds=n_seeds, master_seed=master_seed)
    summary = summarize(rows)
    hyps = hypothesis_verdicts(summary)
    report = {
        "protocol_version": PROTOCOL_VERSION,
        "master_seed": master_seed,
        "n_seeds": n_seeds,
        "recorded_at": datetime.now(UTC).isoformat(),
        "execution_class": "EXECUTED_DETERMINISTIC",
        "live_llm_class": "PROTOCOL_ONLY_NOT_EXECUTED",
        "summary": summary,
        "hypotheses": hyps,
        "limitations": [
            "Agents are deterministic behavioral models, not live LLMs",
            "Task suite is small (3 tasks × 3 domains)",
            (
                "DETAIL steps intentionally incomplete on research/multi_step to "
                "model brittle procedures — not an attack on well-authored runbooks"
            ),
            "No network, no provider variance, no human-in-the-loop study",
            "Independent evaluator shares process but not strategy/agent policy code",
        ],
        "rows": [asdict(r) for r in rows],
    }
    (out_dir / "results.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    # Compact human table
    lines = [
        "# GE-STUDY-v1 sealed results",
        "",
        f"- protocol: `{PROTOCOL_VERSION}`",
        f"- master_seed: `{master_seed}`",
        f"- n_seeds: `{n_seeds}`",
        f"- n_trials: `{len(rows)}`",
        "- execution_class: **EXECUTED_DETERMINISTIC**",
        "- live_llm: **NOT_EXECUTED**",
        "",
        "## Aggregate oracle_success (mean, 90% CI)",
        "",
    ]
    for sid in STRATEGY_IDS:
        m = summary["by_strategy"][sid]["overall"]["oracle_success"]
        lines.append(
            f"- `{sid}`: {m['estimate']:.3f} "
            f"[{m['ci90_low']:.3f}, {m['ci90_high']:.3f}]"
        )
    lines.extend(["", "## Hypotheses", ""])
    for hid, body in hyps.items():
        lines.append(f"- `{hid}`: **{body['verdict']}** — {body['statement']}")
    lines.extend(["", "## Conditional winners (oracle_success)", ""])
    for dom, sid in summary["conditional_winners_oracle_success"].items():
        lines.append(f"- `{dom}`: `{sid}`")
    (out_dir / "RESULTS_SEAL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    root = Path(__file__).resolve().parents[4]
    out = root / "artifacts" / "goal_engineering" / "results"
    report = run_and_seal(out)
    print(json.dumps({"n_trials": report["summary"]["n_trials"], "hypotheses": {
        k: v["verdict"] for k, v in report["hypotheses"].items()
    }}, indent=2))


if __name__ == "__main__":
    main()
