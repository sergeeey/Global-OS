"""Strong sandbox port — container isolation with fail-closed policy (ADR-0006).

Never silently downgrade ``container`` / ``gvisor`` / ``microvm`` to process_local.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from global_os.world.sandbox.runner import Sandbox, SandboxLimits, SandboxResult


class SandboxUnavailable(Exception):
    """Requested sandbox profile cannot be provided."""


class StrongSandboxUnavailable(SandboxUnavailable):
    """Container/gVisor/microvm requested but runtime unavailable or unimplemented."""


class SandboxBackend(Protocol):
    sandbox_id: str

    def create(self) -> str: ...

    def execute(self, argv: list[str], *, cwd: Path | None = None) -> SandboxResult: ...

    def snapshot(self) -> dict[str, Any]: ...

    def destroy(self) -> None: ...


@dataclass(frozen=True)
class ContainerLimits(SandboxLimits):
    memory_mb: int = 512
    cpus: float = 1.0
    network: str = "none"
    image: str = "python:3.13-slim"


def probe_docker(*, timeout_seconds: float = 5.0) -> dict[str, Any]:
    """Return docker server info or raise StrongSandboxUnavailable."""
    docker = shutil.which("docker")
    if docker is None:
        raise StrongSandboxUnavailable(
            "docker binary not found; refusing silent process_local fallback"
        )
    try:
        proc = subprocess.run(
            [docker, "info", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise StrongSandboxUnavailable(
            f"docker probe failed ({exc}); refusing silent process_local fallback"
        ) from exc
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "unknown").strip()[:300]
        raise StrongSandboxUnavailable(
            f"docker daemon unavailable ({err}); refusing silent process_local fallback"
        )
    try:
        info = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        info = {"raw": proc.stdout[:200]}
    return {"binary": docker, "info": info}


class ContainerSandbox:
    """Docker-backed sandbox: --network=none, memory/cpu caps, ephemeral container."""

    def __init__(self, limits: ContainerLimits | None = None) -> None:
        self.limits = limits or ContainerLimits()
        self.sandbox_id = ""
        self._container_id: str | None = None
        self._work: Path | None = None
        self._docker = ""

    def create(self) -> str:
        probe = probe_docker()
        self._docker = str(probe["binary"])
        self._work = Path(tempfile.mkdtemp(prefix="gos_csbx_"))
        name = f"gos-sbx-{uuid.uuid4().hex[:12]}"
        cmd = [
            self._docker,
            "run",
            "-d",
            "--rm",
            "--name",
            name,
            "--network",
            self.limits.network,
            "--memory",
            f"{self.limits.memory_mb}m",
            "--cpus",
            str(self.limits.cpus),
            "-v",
            f"{self._work}:/work:rw",
            "-w",
            "/work",
            self.limits.image,
            "sleep",
            "3600",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=120)
        if proc.returncode != 0:
            self.destroy()
            raise StrongSandboxUnavailable(
                f"docker run failed: {(proc.stderr or proc.stdout)[:300]}"
            )
        self._container_id = proc.stdout.strip()
        self.sandbox_id = name
        return self.sandbox_id

    def execute(self, argv: list[str], *, cwd: Path | None = None) -> SandboxResult:
        if not self._container_id or not self._docker:
            raise RuntimeError("ContainerSandbox.create() required")
        workdir = "/work"
        if cwd is not None and self._work is not None:
            try:
                rel = cwd.resolve().relative_to(self._work.resolve())
                workdir = f"/work/{rel.as_posix()}" if str(rel) != "." else "/work"
            except ValueError as exc:
                raise StrongSandboxUnavailable("cwd escapes sandbox workdir") from exc
        cmd = [
            self._docker,
            "exec",
            "-w",
            workdir,
            self._container_id,
            *argv,
        ]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.limits.walltime_seconds,
                check=False,
            )
            return SandboxResult(
                sandbox_id=self.sandbox_id,
                exit_code=proc.returncode,
                stdout=proc.stdout[: self.limits.max_output_bytes],
                stderr=proc.stderr[: self.limits.max_output_bytes],
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
            err = (exc.stderr or "") if isinstance(exc.stderr, str) else "timeout"
            return SandboxResult(
                self.sandbox_id,
                exit_code=124,
                stdout=out[: self.limits.max_output_bytes],
                stderr=err[: self.limits.max_output_bytes],
                timed_out=True,
            )

    def snapshot(self) -> dict[str, Any]:
        if self._work is None:
            return {}
        files = [p.name for p in self._work.iterdir()]
        return {
            "sandbox_id": self.sandbox_id,
            "container_id": self._container_id,
            "profile": "container",
            "files": files,
        }

    def destroy(self) -> None:
        if self._container_id and self._docker:
            subprocess.run(
                [self._docker, "rm", "-f", self._container_id],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
        self._container_id = None
        if self._work and self._work.exists():
            for p in sorted(self._work.rglob("*"), reverse=True):
                if p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    p.rmdir()
            self._work.rmdir()
        self._work = None


def open_sandbox(
    profile: str,
    *,
    limits: SandboxLimits | ContainerLimits | None = None,
) -> SandboxBackend:
    """Factory: strong profiles fail closed; never silent downgrade."""
    if profile in {"none", "process_local"}:
        return Sandbox(limits if isinstance(limits, SandboxLimits) else SandboxLimits())
    if profile == "container":
        cl = limits if isinstance(limits, ContainerLimits) else ContainerLimits()
        # Probe before returning — fail closed at open time.
        probe_docker()
        return ContainerSandbox(cl)
    if profile in {"gvisor", "microvm"}:
        raise StrongSandboxUnavailable(
            f"sandbox profile {profile!r} not implemented; "
            "refusing silent process_local fallback"
        )
    raise StrongSandboxUnavailable(f"unknown sandbox profile: {profile!r}")
