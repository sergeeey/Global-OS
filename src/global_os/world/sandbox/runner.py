"""Sandbox interface — untrusted code only (GOS sandbox MVP contract)."""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SandboxLimits:
    walltime_seconds: float = 5.0
    max_output_bytes: int = 64_000


@dataclass(frozen=True)
class SandboxResult:
    sandbox_id: str
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool


class Sandbox:
    """Local process sandbox (container/gVisor later). No network by default policy."""

    def __init__(self, limits: SandboxLimits | None = None) -> None:
        self.limits = limits or SandboxLimits()
        self._root: Path | None = None
        self.sandbox_id = ""

    def create(self) -> str:
        self._root = Path(tempfile.mkdtemp(prefix="gos_sbx_"))
        self.sandbox_id = self._root.name
        return self.sandbox_id

    def execute(self, argv: list[str], *, cwd: Path | None = None) -> SandboxResult:
        if self._root is None:
            raise RuntimeError("Sandbox.create() required")
        try:
            proc = subprocess.run(
                argv,
                cwd=str(cwd or self._root),
                capture_output=True,
                text=True,
                timeout=self.limits.walltime_seconds,
                check=False,
            )
            stdout = proc.stdout[: self.limits.max_output_bytes]
            stderr = proc.stderr[: self.limits.max_output_bytes]
            return SandboxResult(
                sandbox_id=self.sandbox_id,
                exit_code=proc.returncode,
                stdout=stdout,
                stderr=stderr,
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
        if self._root is None:
            return {}
        files = [p.name for p in self._root.iterdir()]
        return {"sandbox_id": self.sandbox_id, "files": files}

    def destroy(self) -> None:
        if self._root and self._root.exists():
            for p in sorted(self._root.rglob("*"), reverse=True):
                if p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    p.rmdir()
            self._root.rmdir()
        self._root = None
