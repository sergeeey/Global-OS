"""GE-STUDY runner — v1 seal immutable; v1.1 post-audit appendix writable."""

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
from global_os.evals.goal_engineering.stats import (
    Interval,
    bootstrap_mean_ci,
    bootstrap_paired_diff_ci,
    fnv1a32,
)
from global_os.evals.goal_engineering.strategies import STRATEGY_IDS
from global_os.evals.goal_engineering.tasks import DOMAIN_IDS, all_task_specs, build_world

APPENDIX_PROTOCOL = "GE-STUDY-v1.1-POST-AUDIT"


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
    autonomy: float
    cost_tokens: int
    latency_ms: int
    steps: int
    details: dict[str, Any] = field(default_factory=dict)


def _autonomy(episode: EpisodeResult, budget: int) -> float:
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


def _aligned_metric_vectors(
    rows: list[TrialRow],
    strategy_a: str,
    strategy_b: str,
    metric: str,
    domain: str | None = None,
) -> tuple[list[float], list[float]]:
    """Align on (seed, task_id) for paired bootstrap."""
    index: dict[tuple[int, str], dict[str, TrialRow]] = {}
    for r in rows:
        if domain is not None and r.domain != domain:
            continue
        key = (r.seed, r.task_id)
        index.setdefault(key, {})[r.strategy_id] = r
    aa: list[float] = []
    bb: list[float] = []
    for key in sorted(index):
        cell = index[key]
        if strategy_a in cell and strategy_b in cell:
            aa.append(float(getattr(cell[strategy_a], metric)))
            bb.append(float(getattr(cell[strategy_b], metric)))
    return aa, bb


def _ci_dict(ci: Interval) -> dict[str, Any]:
    return {
        "estimate": ci.estimate,
        "ci90_low": ci.low,
        "ci90_high": ci.high,
        "n": ci.n,
        "level": ci.level,
        "method": ci.method,
    }


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
            ci = bootstrap_mean_ci(xs, seed=fnv1a32(f"{sid}|{m}|mean"))
            cell["overall"][m] = _ci_dict(ci)
        for dom in DOMAIN_IDS:
            cell["by_domain"][dom] = {}
            for m in metrics:
                xs = _metric_vectors(rows, sid, m, domain=dom)
                ci = bootstrap_mean_ci(xs, seed=fnv1a32(f"{sid}|{dom}|{m}|mean"))
                cell["by_domain"][dom][m] = _ci_dict(ci)
        by_strategy[sid] = cell

    contrasts: dict[str, Any] = {}
    for base in ("S_TRAD", "S_DETAIL", "S_DETAIL_VERIFIED"):
        for m in (
            "oracle_success",
            "false_claim",
            "evidence_fidelity",
            "cost_tokens",
            "latency_ms",
        ):
            a, b = _aligned_metric_vectors(rows, "S_GE", base, m)
            ci = bootstrap_paired_diff_ci(
                a, b, seed=fnv1a32(f"GE-{base}-{m}|paired")
            )
            contrasts[f"S_GE_minus_{base}__{m}"] = _ci_dict(ci)

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
        "protocol_version": APPENDIX_PROTOCOL,
        "parent_protocol": PROTOCOL_VERSION,
        "n_trials": len(rows),
        "n_tasks": len(all_task_specs()),
        "n_strategies": len(STRATEGY_IDS),
        "by_strategy": by_strategy,
        "contrasts_GE_minus_baseline": contrasts,
        "conditional_winners_oracle_success": winners,
        "fidelity": "deterministic_behavioral_agents_post_audit",
        "live_llm": "NOT_EXECUTED",
        "ci_scope": (
            "Within-suite seed variability on fixed 3 tasks; "
            "NOT generalization uncertainty over new tasks"
        ),
        "contrast_method": "paired_bootstrap_on_seed_task_cells",
    }


def hypothesis_verdicts(summary: dict[str, Any]) -> dict[str, Any]:
    """Post-audit verdicts: mechanism labels, never causal CONFIRMED."""
    c = summary["contrasts_GE_minus_baseline"]

    def _dir(key: str, *, want_positive: bool) -> str:
        d = c[key]
        if want_positive:
            if d["ci90_low"] > 0:
                return "MECHANISM_SUPPORTED"
            if d["ci90_high"] < 0:
                return "MECHANISM_CONTRADICTED"
            return "INCONCLUSIVE"
        if d["ci90_high"] < 0:
            return "MECHANISM_SUPPORTED"
        if d["ci90_low"] > 0:
            return "MECHANISM_CONTRADICTED"
        return "INCONCLUSIVE"

    return {
        "H1_GE_oracle_gt_TRAD": {
            "statement": "S_GE oracle_success > S_TRAD (paired, this suite)",
            "verdict": _dir("S_GE_minus_S_TRAD__oracle_success", want_positive=True),
            "estimate": c["S_GE_minus_S_TRAD__oracle_success"],
            "causal_status": "NOT_CAUSAL",
        },
        "H2_GE_oracle_gt_DETAIL_brittle": {
            "statement": "S_GE oracle_success > brittle S_DETAIL (paired)",
            "verdict": _dir("S_GE_minus_S_DETAIL__oracle_success", want_positive=True),
            "estimate": c["S_GE_minus_S_DETAIL__oracle_success"],
            "causal_status": "NOT_CAUSAL",
            "note": "S_DETAIL intentionally incomplete — expect GE advantage",
        },
        "H2b_GE_oracle_gt_DETAIL_VERIFIED": {
            "statement": (
                "S_GE oracle_success > S_DETAIL_VERIFIED complete runbook (paired)"
            ),
            "verdict": _dir(
                "S_GE_minus_S_DETAIL_VERIFIED__oracle_success", want_positive=True
            ),
            "estimate": c["S_GE_minus_S_DETAIL_VERIFIED__oracle_success"],
            "causal_status": "NOT_CAUSAL",
            "note": "Fair procedural control — primary post-audit contrast",
        },
        "H3_GE_false_claim_lt_TRAD": {
            "statement": "S_GE false_claim < S_TRAD (paired)",
            "verdict": _dir("S_GE_minus_S_TRAD__false_claim", want_positive=False),
            "estimate": c["S_GE_minus_S_TRAD__false_claim"],
            "causal_status": "NOT_CAUSAL",
        },
        "H4_GE_evidence_gt_DETAIL_VERIFIED": {
            "statement": "S_GE evidence_fidelity > S_DETAIL_VERIFIED (paired)",
            "verdict": _dir(
                "S_GE_minus_S_DETAIL_VERIFIED__evidence_fidelity", want_positive=True
            ),
            "estimate": c["S_GE_minus_S_DETAIL_VERIFIED__evidence_fidelity"],
            "causal_status": "NOT_CAUSAL",
        },
        "H5_GE_not_free_vs_TRAD": {
            "statement": "S_GE cost or latency > S_TRAD (paired)",
            "verdict": (
                "MECHANISM_SUPPORTED"
                if (
                    _dir("S_GE_minus_S_TRAD__cost_tokens", want_positive=True)
                    == "MECHANISM_SUPPORTED"
                    or _dir("S_GE_minus_S_TRAD__latency_ms", want_positive=True)
                    == "MECHANISM_SUPPORTED"
                )
                else "INCONCLUSIVE"
            ),
            "estimate_cost": c["S_GE_minus_S_TRAD__cost_tokens"],
            "estimate_latency": c["S_GE_minus_S_TRAD__latency_ms"],
            "causal_status": "NOT_CAUSAL",
        },
        "meta": {
            "v1_seal_labels": "SUPERSEDED_SEE_POST_HOC_AUDIT",
            "forbidden_label": "CONFIRMED_as_causal_GE_advantage",
            "live_llm": "NOT_EXECUTED",
        },
    }


def run_and_seal(
    out_dir: Path,
    *,
    n_seeds: int = 20,
    master_seed: int = MASTER_SEED,
) -> dict[str, Any]:
    """Write appendix seal. Refuses to overwrite v1_immutable/."""
    resolved = out_dir.resolve()
    if resolved.name == "v1_immutable" or "v1_immutable" in resolved.parts:
        raise RuntimeError("refusing to write into immutable v1 seal directory")
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = run_suite(n_seeds=n_seeds, master_seed=master_seed)
    summary = summarize(rows)
    hyps = hypothesis_verdicts(summary)
    report = {
        "protocol_version": APPENDIX_PROTOCOL,
        "parent_protocol": PROTOCOL_VERSION,
        "master_seed": master_seed,
        "n_seeds": n_seeds,
        "recorded_at": datetime.now(UTC).isoformat(),
        "execution_class": "EXECUTED_DETERMINISTIC_POST_AUDIT",
        "live_llm_class": "PROTOCOL_ONLY_NOT_EXECUTED",
        "summary": summary,
        "hypotheses": hyps,
        "limitations": [
            "Agents are deterministic behavioral models, not live LLMs",
            "Only 3 task types — CIs are within-suite seed noise, not task generalization",
            "S_DETAIL remains brittle by design; fair control is S_DETAIL_VERIFIED",
            "Cost/latency are simulated counters",
            "Oracle isolated via AgentView; evaluator alone scores against oracle",
            "See POST_HOC_AUDIT.md — v1 CONFIRMED labels demoted",
        ],
        "rows": [asdict(r) for r in rows],
    }
    (out_dir / "results.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# GE-STUDY-v1.1 post-audit appendix",
        "",
        f"- protocol: `{APPENDIX_PROTOCOL}`",
        f"- parent_immutable: `{PROTOCOL_VERSION}` → `results/v1_immutable/`",
        f"- master_seed: `{master_seed}`",
        f"- n_seeds: `{n_seeds}`",
        f"- n_trials: `{len(rows)}` (4 strategies × 3 tasks × {n_seeds} seeds)",
        "- execution_class: **EXECUTED_DETERMINISTIC_POST_AUDIT**",
        "- live_llm: **NOT_EXECUTED**",
        "- causal_status: **NOT_CAUSAL** (mechanism demo only)",
        "",
        "## Aggregate oracle_success (mean, 90% CI; within-suite)",
        "",
    ]
    for sid in STRATEGY_IDS:
        m = summary["by_strategy"][sid]["overall"]["oracle_success"]
        lines.append(
            f"- `{sid}`: {m['estimate']:.3f} "
            f"[{m['ci90_low']:.3f}, {m['ci90_high']:.3f}]"
        )
    lines.extend(["", "## Hypotheses (post-audit labels)", ""])
    for hid, body in hyps.items():
        if hid == "meta":
            continue
        lines.append(f"- `{hid}`: **{body['verdict']}** — {body['statement']}")
    lines.extend(["", "## Conditional winners (oracle_success)", ""])
    for dom, sid in summary["conditional_winners_oracle_success"].items():
        lines.append(f"- `{dom}`: `{sid}`")
    lines.extend(
        [
            "",
            "## Fair contrast note",
            "",
            "Primary GE-vs-procedure contrast is `S_GE` vs `S_DETAIL_VERIFIED`.",
            "Advantage vs brittle `S_DETAIL` is expected by construction.",
            "",
        ]
    )
    (out_dir / "RESULTS_SEAL.md").write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> None:
    root = Path(__file__).resolve().parents[4]
    # Never overwrite immutable v1 seal; write appendix only
    out = root / "artifacts" / "goal_engineering" / "results" / "v1_1_post_audit"
    report = run_and_seal(out)
    print(
        json.dumps(
            {
                "n_trials": report["summary"]["n_trials"],
                "hypotheses": {
                    k: v["verdict"]
                    for k, v in report["hypotheses"].items()
                    if k != "meta"
                },
                "out": str(out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
