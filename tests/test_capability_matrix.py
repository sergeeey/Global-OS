from __future__ import annotations

import json
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_PATH_TOKEN = re.compile(r"(?:tests|artifacts|src|docs)/[A-Za-z0-9_./:+-]+")


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


def test_capability_evidence_paths_exist():
    """R1 regression: RUNTIME_* rows must cite at least one existing evidence path."""
    matrix = json.loads((_ROOT / "docs/capability_matrix.json").read_text(encoding="utf-8"))
    runtime_states = {
        "RUNTIME_VERIFIED_LOCAL",
        "RUNTIME_VERIFIED_HARNESS",
        "PRODUCTION_PROVEN",
    }
    failures: list[str] = []
    for item in matrix["capabilities"]:
        if item["state"] not in runtime_states:
            continue
        evidence = item.get("evidence") or ""
        tokens = _PATH_TOKEN.findall(evidence)
        if not tokens:
            failures.append(f"{item['id']}: no parseable evidence path")
            continue
        ok_any = False
        for token in tokens:
            rel = token.split("::", 1)[0].rstrip(".,);/")
            if (_ROOT / rel).exists():
                ok_any = True
                break
        if not ok_any:
            failures.append(f"{item['id']}: cited paths missing: {tokens}")
    assert not failures, "\n".join(failures)
