from __future__ import annotations

import sys

from global_os.world.sandbox import Sandbox, SandboxLimits


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
