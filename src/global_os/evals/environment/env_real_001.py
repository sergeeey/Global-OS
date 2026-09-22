"""ENV-REAL-001 — observed Environment Compiler routing failure.

Cloud Agent selected a remote VM that had a git clone but lacked
machine-local secrets / filesystem locality. Not a scientific claim;
empirical failure case for H-ENV / EnvironmentCompiler design.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

CASE_ID = "ENV-REAL-001"


@dataclass(frozen=True)
class EnvReal001Report:
    case_id: str = CASE_ID
    hypothesis_link: str = "H-ENV-001"
    fidelity: str = "OBSERVED_OPERATOR_FAILURE"
    scientific_claim_accepted: bool = False
    failure: str = "Agent selected execution environment without required machine-local resources"
    observed: tuple[str, ...] = (
        "Cloud Agent VM had repository clone",
        "Local secret path (Windows E:\\…\\secret\\.env) absent from VM filesystem",
        "live_keys_present() all False in cloud workspace",
        ".env gitignored — secrets never sync via git clone",
    )
    required_capabilities: tuple[str, ...] = (
        "resource_locality",
        "secret_locality",
        "filesystem_locality",
        "tool_availability",
        "privacy",
        "execution_authority",
    )
    expected_correction: str = (
        "Route task to self-hosted / My Machines worker when secrets+Docker+local "
        "checkout are required; refuse silent continue on cloud-only clone"
    )
    verdict: str = "FAILURE_CASE_RECORDED_NOT_FIXED"
    recorded_at: str = ""

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


def summarize_env_real_001() -> EnvReal001Report:
    """Record the Cloud-vs-local secret locality failure. Claim stays false."""
    return EnvReal001Report(recorded_at=datetime.now(UTC).isoformat())
