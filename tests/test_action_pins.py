from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.validate_action_pins import USES_RE, _is_full_sha, _resolves, _workflow_files


def test_workflow_pins_are_full_shas():
    files = _workflow_files()
    assert files
    for path in files:
        text = path.read_text(encoding="utf-8")
        matches = list(USES_RE.finditer(text))
        assert matches, f"no uses: in {path}"
        for match in matches:
            ref = match.group("ref")
            assert _is_full_sha(ref), f"{path}: {ref} not full sha"


def test_setup_python_pin_matches_known_v560():
    """Guard against truncated/corrupted immutable pins (CI run #7 class of bug)."""
    text = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    expected = "a26af69be951a213d495a4c3e4e4022e16d87065"
    assert expected in text
    assert "a26af69be951a213d495a4bdc1e42aa18c1bdc04" not in text
    assert re.search(rf"actions/setup-python@{expected}", text)


def test_resolves_retries_transient_403(monkeypatch: pytest.MonkeyPatch):
    import urllib.error
    import urllib.request

    calls = {"n": 0}

    class FakeResp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(req, timeout=30):
        calls["n"] += 1
        if calls["n"] < 3:
            raise urllib.error.HTTPError(
                req.full_url, 403, "rate", hdrs=None, fp=None
            )  # type: ignore[arg-type]
        return FakeResp()
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    with patch("tools.validate_action_pins.time.sleep", return_value=None):
        ok, detail = _resolves("actions", "checkout", "0" * 40, attempts=5)
    assert ok is True
    assert detail == "ok"
    assert calls["n"] == 3
