"""PREPROD_V0_1 supervised Operator Edition — composition of existing kernels.

No new Authority / Verification / scheduler surfaces (ADR-0009).
Profile label: PREPROD_SUPERVISED (mission metadata; not a GOS_PROFILE enum).
"""

from global_os.runtime.preprod.supervised_mission import (
    SupervisedMissionError,
    cancel_mission,
    deliver_mission,
    pause_mission,
    resume_mission,
    start_mission,
    status_mission,
    verify_repo_audit_report,
)

__all__ = [
    "SupervisedMissionError",
    "cancel_mission",
    "deliver_mission",
    "pause_mission",
    "resume_mission",
    "start_mission",
    "status_mission",
    "verify_repo_audit_report",
]
