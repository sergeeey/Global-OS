"""Portability regression — survival slow_dependency must not require Unix sleep."""

from __future__ import annotations

import sys

from global_os.evals.survival.harness import cross_platform_sleep_argv, run_injection
from global_os.evals.survival.scenarios import Injection
from global_os.world.sandbox import Sandbox, SandboxLimits


def test_cross_platform_sleep_argv_uses_python_not_unix_sleep():
    argv = cross_platform_sleep_argv(2.0)
    assert argv[0] == sys.executable
    assert argv[1] == "-c"
    assert "time.sleep" in argv[2]
    assert argv[0] != "sleep"
    assert "sleep" not in argv[0]


def test_sandbox_timeout_with_cross_platform_sleep_no_unix_binary():
    """Same timeout semantics as slow_dependency sandbox leg — OS-independent."""
    sb = Sandbox(SandboxLimits(walltime_seconds=0.05))
    sb.create()
    try:
        result = sb.execute(cross_platform_sleep_argv(2.0))
    finally:
        sb.destroy()
    assert result.timed_out is True
    assert result.exit_code == 124


def test_slow_dependency_injection_passes_without_unix_sleep():
    scenario = run_injection(Injection.SLOW_DEPENDENCY)
    assert scenario.passed is True
    assert scenario.name == "slow_dependency"
