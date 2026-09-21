from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from global_os.adapters.authority import RustAuthorityError, decide_via_rust, find_gos_authority_bin


def _ensure_built() -> Path:
    root = Path(__file__).resolve().parents[1]
    binary = find_gos_authority_bin()
    if binary and binary.exists():
        return binary
    cargo = shutil.which("cargo")
    if not cargo:
        pytest.skip("cargo not available")
    proc = subprocess.run(
        [cargo, "build", "-p", "authority_kernel"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        pytest.fail(f"cargo build failed: {proc.stderr}")
    binary = find_gos_authority_bin()
    assert binary is not None
    return binary


def test_rust_authority_default_deny_and_allow():
    _ensure_built()
    denied = decide_via_rust(
        {
            "principal": "w1",
            "action": "web.read",
            "capability": "web.read",
            "resource": "https://x",
            "granted_capabilities": [],
        },
        {"capability": "web.read"},
    )
    assert denied["decision"] == "DENY"

    allowed = decide_via_rust(
        {
            "principal": "w1",
            "action": "web.read",
            "capability": "web.read",
            "resource": "https://x",
            "granted_capabilities": ["web.read"],
            "parent_capabilities": ["web.read"],
        },
        {"capability": "web.read"},
    )
    assert allowed["decision"] == "ALLOW"
    assert allowed["execution_token"]


def test_rust_authority_gos_i04_parent_subset():
    _ensure_built()
    out = decide_via_rust(
        {
            "principal": "child",
            "action": "email.send",
            "capability": "email.send",
            "resource": "a@b.c",
            "granted_capabilities": ["email.send"],
            "parent_capabilities": ["email.draft"],
            "approval_id": "apr_1",
        },
        {},
    )
    assert out["decision"] == "DENY"
    assert "GOS-I04" in out["reason"]


def test_rust_authority_fails_closed_without_binary(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "global_os.adapters.authority.rust_client.find_gos_authority_bin",
        lambda: None,
    )
    with pytest.raises(RustAuthorityError, match="refusing silent Python"):
        decide_via_rust(
            {
                "principal": "w1",
                "action": "web.read",
                "capability": "web.read",
                "resource": "x",
                "granted_capabilities": ["web.read"],
            }
        )
