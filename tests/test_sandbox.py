from __future__ import annotations

import sys

import pytest

from global_os.world.sandbox import (
    Sandbox,
    SandboxLimits,
    StrongSandboxUnavailable,
    open_sandbox,
    probe_docker,
)


def test_sandbox_create_execute_destroy():
    sb = Sandbox(SandboxLimits(walltime_seconds=3))
    sid = sb.create()
    assert sid
    result = sb.execute([sys.executable, "-c", "print('gos-ok')"])
    assert result.timed_out is False
    assert result.exit_code == 0
    assert "gos-ok" in result.stdout
    snap = sb.snapshot()
    assert snap["sandbox_id"] == sid
    sb.destroy()
    assert sb.snapshot() == {}


def test_open_sandbox_process_local():
    sb = open_sandbox("process_local", limits=SandboxLimits(walltime_seconds=2))
    sb.create()
    out = sb.execute([sys.executable, "-c", "print(1)"])
    assert out.exit_code == 0
    sb.destroy()


def test_container_profile_fails_closed_without_docker(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("global_os.world.sandbox.port.shutil.which", lambda _name: None)
    with pytest.raises(StrongSandboxUnavailable, match="refusing silent process_local"):
        open_sandbox("container")


def test_gvisor_and_microvm_fail_closed():
    with pytest.raises(StrongSandboxUnavailable, match="not implemented"):
        open_sandbox("gvisor")
    with pytest.raises(StrongSandboxUnavailable, match="not implemented"):
        open_sandbox("microvm")


def test_probe_docker_fails_closed(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("global_os.world.sandbox.port.shutil.which", lambda _name: None)
    with pytest.raises(StrongSandboxUnavailable, match="docker binary not found"):
        probe_docker()


def test_container_sandbox_live_when_docker_available():
    try:
        probe_docker()
    except StrongSandboxUnavailable:
        pytest.skip("docker unavailable — fail-closed path covered elsewhere")
    sb = open_sandbox("container")
    try:
        try:
            sid = sb.create()
        except StrongSandboxUnavailable as exc:
            pytest.skip(f"docker cannot create containers here: {exc}")
        assert sid
        result = sb.execute(["python", "-c", "print('gos-container-ok')"])
        assert result.exit_code == 0
        assert "gos-container-ok" in result.stdout
        snap = sb.snapshot()
        assert snap.get("profile") == "container"
    finally:
        sb.destroy()
