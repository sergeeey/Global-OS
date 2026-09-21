from __future__ import annotations

from pathlib import Path

from global_os.cognition.workers import WorkerRuntime, WorkerSpec
from global_os.runtime.events import EventLedger
from global_os.world.artifacts import ArtifactStore


def test_ephemeral_worker_writes_artifact(tmp_path: Path):
    ledger = EventLedger()
    store = ArtifactStore(tmp_path / "artifacts")
    rt = WorkerRuntime(ledger=ledger, artifacts=store)
    wid = rt.spawn(
        WorkerSpec(
            mission="architecture",
            capabilities=frozenset({"filesystem.read"}),
            parent_capabilities=frozenset({"filesystem.read", "web.read"}),
            fn=lambda a: {"finding": "ok", "input": a},
        ),
        tenant_id="t",
        workspace_id="w",
        goal_id="goal_x",
    )
    result = rt.run(
        wid,
        {"task": "scan"},
        tenant_id="t",
        workspace_id="w",
        goal_id="goal_x",
    )
    assert result.destroyed is True
    assert result.artifact_digest and result.artifact_digest.startswith("sha256:")
    assert worker_gone(rt, wid)
    raw = store.get_bytes(result.artifact_digest)
    assert b"architecture" in raw


def worker_gone(rt: WorkerRuntime, wid: str) -> bool:
    return wid not in rt._active  # intentional private-state check
