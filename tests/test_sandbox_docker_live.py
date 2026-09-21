"""Live Docker sandbox — Reality Contact (requires usable Docker daemon)."""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest

from global_os.world.sandbox import (
    ContainerLimits,
    StrongSandboxUnavailable,
    probe_docker,
    run_sandboxed_task,
)


def _docker_can_run_containers() -> bool:
    try:
        probe_docker()
    except StrongSandboxUnavailable:
        return False
    docker = shutil.which("docker")
    if not docker:
        return False
    proc = subprocess.run(
        [docker, "run", "--rm", "--network=none", "python:3.13-slim", "python", "-c", "print(1)"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    return proc.returncode == 0 and "1" in proc.stdout


def _require_usable_docker() -> None:
    if _docker_can_run_containers():
        return
    if os.environ.get("GOS_REQUIRE_DOCKER") == "1":
        pytest.fail(
            "GOS_REQUIRE_DOCKER=1 but docker cannot run containers "
            "(daemon missing or nested overlay unsupported)"
        )
    pytest.skip("docker cannot run containers in this environment")


def test_live_sandboxed_task_network_limits_destroy():
    _require_usable_docker()
    out = run_sandboxed_task(
        goal_id="goal_reality_docker",
        task_id="task_container_1",
        argv=["python", "-c", "print('gos-docker-task-ok')"],
        limits=ContainerLimits(
            walltime_seconds=30.0,
            memory_mb=256,
            cpus=0.5,
            network="none",
            image="python:3.13-slim",
        ),
        verify_network_isolation=True,
    )
    assert out.exit_code == 0
    assert "gos-docker-task-ok" in out.stdout
    assert out.destroyed is True
    assert out.network_isolated is True
    assert out.inspect.get("network_mode") == "none"
    assert out.inspect.get("memory") == 256 * 1024 * 1024
    assert out.container_id
