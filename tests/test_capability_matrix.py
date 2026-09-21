from __future__ import annotations

import json
from pathlib import Path


def test_capability_matrix_states_are_known():
    matrix = json.loads(Path("docs/capability_matrix.json").read_text(encoding="utf-8"))
    allowed = set(matrix["states"])
    assert "CONTRACTED" in allowed
    for item in matrix["capabilities"]:
        assert item["state"] in allowed, item
    # Honesty anchors
    by_id = {c["id"]: c for c in matrix["capabilities"]}
    assert by_id["temporal_durability"]["state"] == "RUNTIME_VERIFIED_HARNESS"
    assert by_id["rust_authority_boundary"]["state"] == "RUNTIME_VERIFIED_HARNESS"
    assert by_id["durable_runner_process_kill"]["state"] == "RUNTIME_VERIFIED_HARNESS"
    assert by_id["survival_other_injections"]["state"] == "RUNTIME_VERIFIED_HARNESS"
    assert by_id["environment_compiler"]["state"] == "RUNTIME_VERIFIED_LOCAL"
    assert by_id["environment_compiler_dynamic"]["state"] == "RUNTIME_VERIFIED_LOCAL"
    assert by_id["full_epistemic_graph"]["state"] == "RUNTIME_VERIFIED_LOCAL"
    assert by_id["event_replay_engine"]["state"] == "RUNTIME_VERIFIED_LOCAL"
    assert by_id["otel_distributed_temporal"]["state"] == "RUNTIME_VERIFIED_LOCAL"
    assert by_id["otel_traces"]["state"] == "RUNTIME_VERIFIED_LOCAL"
    assert by_id["h_env_001_benchmark"]["state"] == "RUNTIME_VERIFIED_LOCAL"
    assert by_id["postgres_durable_state"]["state"] == "RUNTIME_VERIFIED_HARNESS"
    assert by_id["temporal_durability"]["state"] == "RUNTIME_VERIFIED_HARNESS"
