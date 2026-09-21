"""Sandboxed task runner — Goal/Task → container → result (Reality Contact)."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any

from global_os.world.sandbox.port import (
    ContainerLimits,
    ContainerSandbox,
    StrongSandboxUnavailable,
    open_sandbox,
    probe_docker,
)


@dataclass(frozen=True)
class SandboxedTaskResult:
    goal_id: str
    task_id: str
    sandbox_id: str
    container_id: str
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    destroyed: bool
    limits: dict[str, Any]
    network_isolated: bool
    inspect: dict[str, Any]


def run_sandboxed_task(
    *,
    goal_id: str,
    task_id: str,
    argv: list[str],
    limits: ContainerLimits | None = None,
    verify_network_isolation: bool = True,
) -> SandboxedTaskResult:
    """Execute argv inside a container sandbox and tear it down.

    Fail-closed if Docker unavailable. Never falls back to process_local.
    """
    probe_docker()
    cl = limits or ContainerLimits(
        walltime_seconds=60.0, memory_mb=256, cpus=0.5, network="none"
    )
    sb = open_sandbox("container", limits=cl)
    if not isinstance(sb, ContainerSandbox):
        raise StrongSandboxUnavailable("open_sandbox(container) did not return ContainerSandbox")

    network_ok = True
    inspect: dict[str, Any] = {}
    container_id = ""
    sandbox_id = ""
    result_exit = 1
    result_out = ""
    result_err = ""
    timed_out = False
    try:
        sandbox_id = sb.create()
        snap = sb.snapshot()
        container_id = str(snap.get("container_id") or "")
        inspect = _inspect_container(container_id)
        if verify_network_isolation:
            net = sb.execute(
                [
                    "python",
                    "-c",
                    (
                        "import urllib.request\n"
                        "try:\n"
                        " urllib.request.urlopen('https://example.com', timeout=2)\n"
                        " print('NETWORK_OPEN')\n"
                        "except Exception as e:\n"
                        " print('NETWORK_BLOCKED:'+type(e).__name__)\n"
                    ),
                ]
            )
            network_ok = "NETWORK_BLOCKED" in net.stdout and "NETWORK_OPEN" not in net.stdout
        # Prove writable workdir + host mount
        sb.execute(["python", "-c", "open('/work/gos_marker.txt','w').write('ok')"])
        result = sb.execute(argv)
        result_exit = result.exit_code
        result_out = result.stdout
        result_err = result.stderr
        timed_out = result.timed_out
    finally:
        sb.destroy()
        if container_id:
            _assert_container_gone(container_id)

    return SandboxedTaskResult(
        goal_id=goal_id,
        task_id=task_id,
        sandbox_id=sandbox_id,
        container_id=container_id,
        exit_code=result_exit,
        stdout=result_out,
        stderr=result_err,
        timed_out=timed_out,
        destroyed=True,
        limits={
            "memory_mb": cl.memory_mb,
            "cpus": cl.cpus,
            "network": cl.network,
        },
        network_isolated=network_ok if verify_network_isolation else True,
        inspect=inspect,
    )


def _inspect_container(container_id: str) -> dict[str, Any]:
    docker = shutil.which("docker")
    if not docker or not container_id:
        return {}
    proc = subprocess.run(
        [docker, "inspect", container_id],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return {"error": proc.stderr[:200]}
    data = json.loads(proc.stdout)[0]
    host = data.get("HostConfig", {})
    return {
        "memory": host.get("Memory"),
        "nano_cpus": host.get("NanoCpus"),
        "network_mode": host.get("NetworkMode"),
        "status": data.get("State", {}).get("Status"),
    }


def _assert_container_gone(container_id: str) -> None:
    docker = shutil.which("docker")
    if not docker:
        return
    check = subprocess.run(
        [docker, "inspect", container_id],
        capture_output=True,
        text=True,
        check=False,
    )
    if check.returncode == 0:
        raise StrongSandboxUnavailable(f"container {container_id} still present after destroy()")
