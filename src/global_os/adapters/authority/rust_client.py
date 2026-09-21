"""Process-boundary Authority client — shells out to gos-authority (never imports models)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


class RustAuthorityError(Exception):
    pass


def find_gos_authority_bin() -> Path | None:
    which = shutil.which("gos-authority")
    if which:
        return Path(which)
    # workspace target/debug from repo root
    root = Path(__file__).resolve()
    for parent in root.parents:
        candidate = parent / "target" / "debug" / "gos-authority"
        if candidate.exists():
            return candidate
        candidate = parent / "crates" / "authority_kernel" / "target" / "debug" / "gos-authority"
        if candidate.exists():
            return candidate
    return None


def decide_via_rust(request: dict[str, Any], proposal: dict[str, Any] | None = None) -> dict[str, Any]:
    """Call Rust Authority binary. Fail closed if binary missing — never silent Python allow."""
    binary = find_gos_authority_bin()
    if binary is None:
        raise RustAuthorityError(
            "gos-authority binary not found; refusing silent Python Authority fallback"
        )
    payload = {"request": request, "proposal": proposal or {}}
    proc = subprocess.run(
        [str(binary)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    if not proc.stdout.strip():
        raise RustAuthorityError(f"empty response from gos-authority: {proc.stderr}")
    try:
        parsed: dict[str, Any] = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RustAuthorityError(f"invalid JSON from gos-authority: {proc.stdout}") from exc
    return parsed
