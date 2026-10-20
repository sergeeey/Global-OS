"""Cross-platform regression for directory hash ordering.

The frozen hashes were produced with POSIX (case-sensitive) path ordering.  Sorting
``pathlib.Path`` objects is platform-dependent: WindowsPath compares case-insensitively,
PosixPath compares case-sensitively.  The directory hashers must therefore sort by the
canonical POSIX string, not by Path objects.

These tests fail on Windows before the fix and pass on both Windows and Linux after it.
They do not modify any sealed pack or manifest.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from global_os.evals.research.y22_evidence_ab import _dir_sha256 as y22_dir_sha256
from global_os.evals.trust.pack_v2 import _dir_sha256 as pack_v2_dir_sha256
from global_os.evals.trust.pack_v3 import _dir_sha256 as pack_v3_dir_sha256

ROOT = Path(__file__).resolve().parents[1]

FROZEN = [
    (
        "y22_public",
        y22_dir_sha256,
        ROOT / "artifacts" / "y22" / "public",
        "6cf5ed7880cadfe39fc07e3603473c71dca0fadef0e7061689cc17c1787db6bb",
    ),
    (
        "pack_v2_sealed",
        pack_v2_dir_sha256,
        ROOT / "artifacts" / "safe_autonomy_t1" / "PACK_V2" / "sealed",
        "ab9f4998acd0fcc0b613beba7661c0dbef77c559897dc6de5df95ce65acd1768",
    ),
    (
        "pack_v3_sealed",
        pack_v3_dir_sha256,
        ROOT / "artifacts" / "safe_autonomy_t1" / "PACK_V3" / "sealed",
        "e77e8813026e07d154fd6bc235cec9c2f20943c308d48e41282c789f526a8c6e",
    ),
]

HASHERS = [y22_dir_sha256, pack_v2_dir_sha256, pack_v3_dir_sha256]


@pytest.mark.parametrize("name,hasher,directory,expected", FROZEN, ids=[f[0] for f in FROZEN])
def test_frozen_directory_hash_is_unchanged(
    name: str, hasher, directory: Path, expected: str
) -> None:
    """Historical sealed hashes must stay exactly as frozen; no re-freeze."""
    del name
    assert directory.is_dir(), directory
    assert hasher(directory) == expected


@pytest.mark.parametrize("hasher", HASHERS, ids=["y22", "pack_v2", "pack_v3"])
def test_mixed_case_names_use_case_sensitive_posix_order(hasher, tmp_path: Path) -> None:
    """README.md sorts before public_pack.json case-sensitively, opposite of WindowsPath."""
    (tmp_path / "README.md").write_text("readme\n", encoding="utf-8")
    (tmp_path / "public_pack.json").write_text("pack\n", encoding="utf-8")

    expected = hashlib.sha256()
    for name in ("README.md", "public_pack.json"):  # case-sensitive POSIX order
        expected.update(name.encode())
        expected.update((tmp_path / name).read_bytes())

    assert hasher(tmp_path) == expected.hexdigest()
