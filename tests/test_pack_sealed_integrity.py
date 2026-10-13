"""Sealed PACK-v2/v3 drift guards — five integrity checks each."""

from __future__ import annotations

from pathlib import Path

from global_os.evals.trust.pack_v2 import PACK_V2_ID, assert_pack_v2_integrity
from global_os.evals.trust.pack_v3 import PACK_V3_ID, assert_pack_v3_integrity

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "safe_autonomy_t1"


def test_pack_v2_five_integrity_checks() -> None:
    m = assert_pack_v2_integrity(root=ARTIFACT)
    assert m["pack_id"] == PACK_V2_ID
    assert m.get("sealed_pack_sha256")
    assert m.get("sealed_dir_sha256")


def test_pack_v3_five_integrity_checks() -> None:
    m = assert_pack_v3_integrity(root=ARTIFACT)
    assert m["pack_id"] == PACK_V3_ID
    assert m.get("sealed_pack_sha256")
    assert m.get("sealed_dir_sha256")
