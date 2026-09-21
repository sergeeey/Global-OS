"""H-ENV-001 synthetic harness — environment vs prompt marginal gain.

Fidelity: synthetic_deterministic. Does NOT accept or reject the scientific hypothesis.
Results are for harness correctness only until real-model runs are recorded.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class EnvConfig:
    name: str
    tools: bool
    browser: bool
    sandbox: bool
    evidence: bool
    full_gos: bool


ENVIRONMENTS: tuple[EnvConfig, ...] = (
    EnvConfig("A_no_tools", False, False, False, False, False),
    EnvConfig("B_browser", True, True, False, False, False),
    EnvConfig("C_browser_sandbox", True, True, True, False, False),
    EnvConfig("D_browser_sandbox_evidence", True, True, True, True, False),
    EnvConfig("E_full_global_os", True, True, True, True, True),
)


def _env_capability_score(env: EnvConfig) -> float:
    score = 0.15
    if env.tools:
        score += 0.1
    if env.browser:
        score += 0.15
    if env.sandbox:
        score += 0.15
    if env.evidence:
        score += 0.2
    if env.full_gos:
        score += 0.2
    return min(score, 1.0)


def _prompt_score(prompt_tokens: int) -> float:
    """Diminishing returns after minimally sufficient instruction (~120 tokens)."""
    if prompt_tokens <= 0:
        return 0.0
    # saturates near 1.0; marginal gain after 120 is small
    return min(1.0, prompt_tokens / 120.0) * (1.0 - 0.35 * max(0, prompt_tokens - 120) / 500.0)


def simulate_success(*, env: EnvConfig, prompt_tokens: int) -> float:
    """Synthetic success in [0,1]. Environment weight > prompt after min sufficiency."""
    env_s = _env_capability_score(env)
    prompt_s = max(0.0, _prompt_score(prompt_tokens))
    # After min prompt (~80), environment dominates residual variance
    env_w = 0.7 if prompt_tokens >= 80 else 0.4
    prompt_w = 1.0 - env_w
    return round(env_w * env_s + prompt_w * prompt_s, 4)


@dataclass(frozen=True)
class EnvSweepRow:
    environment: str
    prompt_tokens: int
    success: float


def run_environment_sweep(prompt_tokens: int = 100) -> list[EnvSweepRow]:
    return [
        EnvSweepRow(env.name, prompt_tokens, simulate_success(env=env, prompt_tokens=prompt_tokens))
        for env in ENVIRONMENTS
    ]


def run_prompt_sweep(env: EnvConfig | None = None) -> list[EnvSweepRow]:
    target = env or ENVIRONMENTS[2]  # C fixed
    return [
        EnvSweepRow(target.name, tokens, simulate_success(env=target, prompt_tokens=tokens))
        for tokens in (40, 80, 120, 200, 400)
    ]


def summarize_h_env_001() -> dict[str, Any]:
    """Preregistered-style experiment record. Verdict is never CONFIRMED from synthetic data."""
    env_rows = run_environment_sweep(100)
    prompt_rows = run_prompt_sweep()
    env_gain = env_rows[-1].success - env_rows[0].success
    prompt_gain = prompt_rows[-1].success - prompt_rows[1].success  # after min sufficient
    return {
        "id": "H-ENV-001",
        "hypothesis": (
            "After minimally sufficient instructions, improving task environment yields "
            "larger marginal gain than further prompt elongation."
        ),
        "fidelity": "synthetic_deterministic",
        "preregistered_at": "2026-09-21",
        "ran_at": datetime.now(UTC).isoformat(),
        "environment_sweep": [asdict(r) for r in env_rows],
        "prompt_sweep": [asdict(r) for r in prompt_rows],
        "metrics": {
            "env_marginal_A_to_E": round(env_gain, 4),
            "prompt_marginal_after_min": round(prompt_gain, 4),
        },
        "synthetic_hint_env_gt_prompt": env_gain > prompt_gain,
        "verdict": "INCONCLUSIVE_NEEDS_REAL_MODEL",
        "note": "80/20 rhetoric is NOT accepted as fact; harness only validates measurement plumbing.",
    }
