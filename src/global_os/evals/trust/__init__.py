"""Safe-autonomy / H_TRUST eval harness (metrics freeze; not Trust Kernel)."""

from global_os.evals.trust.safe_autonomy_metrics import (
    MATERIAL_FAILURE_TAXONOMY,
    MCID_SET,
    MCID_UNSET,
    ArmMetrics,
    KeepRejectDecision,
    McidConfig,
    SafeAutonomyScore,
    compute_mier,
    compute_ssr,
    decide_keep_reject,
    load_benchmark_freeze,
)
from global_os.evals.trust.t1_diagnostics import build_diagnostics, write_diagnostics
from global_os.evals.trust.t1_runner import run_t1
from global_os.evals.trust.t2_runner import run_t2
from global_os.evals.trust.t3_runner import run_t3
from global_os.evals.trust.variance_pilot import (
    derive_mcid,
    run_variance_pilot,
    write_pilot_artifacts,
)

__all__ = [
    "MATERIAL_FAILURE_TAXONOMY",
    "MCID_SET",
    "MCID_UNSET",
    "ArmMetrics",
    "KeepRejectDecision",
    "McidConfig",
    "SafeAutonomyScore",
    "build_diagnostics",
    "compute_mier",
    "compute_ssr",
    "decide_keep_reject",
    "derive_mcid",
    "load_benchmark_freeze",
    "run_t1",
    "run_t2",
    "run_t3",
    "run_variance_pilot",
    "write_diagnostics",
    "write_pilot_artifacts",
]
