"""FC-01/FC-02 hardening regressions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from global_os.evals.research.artifact_lock import assert_artifact_path_writable
from global_os.evals.research.y22_evidence_ab import _dir_sha256

ROOT = Path(__file__).resolve().parents[1]


def test_y22_process_log_sha_is_public_dir_merkle():
    pub = ROOT / "artifacts" / "y22" / "public"
    expected = _dir_sha256(pub)
    pl = json.loads((ROOT / "artifacts" / "y22" / "arms" / "A" / "process_log.json").read_text())
    assert pl["public_pack_sha256"] == expected
    file_sha = hashlib.sha256((pub / "public_pack.json").read_bytes()).hexdigest()
    assert pl["public_pack_sha256"] != file_sha


def test_historical_artifact_rewrite_refused():
    target = ROOT / "artifacts" / "y19" / "Y19-H1-transient-early-warning" / "mission.json"
    with pytest.raises(PermissionError):
        assert_artifact_path_writable(target)
