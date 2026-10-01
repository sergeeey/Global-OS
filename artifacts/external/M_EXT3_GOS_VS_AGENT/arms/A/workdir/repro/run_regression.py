"""Standalone regression for httpx#3614 — no upstream pytest.ini."""
from __future__ import annotations

import sys
from pathlib import Path

WT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/httpx-mext3-armA")
sys.path.insert(0, str(WT))

import httpx  # noqa: E402


def test_base_url_with_query_does_not_corrupt_query_when_enforcing_slash() -> None:
    client = httpx.Client(base_url="https://example.org/get?data=1")
    assert client.base_url.query == b"data=1", client.base_url.query
    assert str(client.base_url) == "https://example.org/get/?data=1"
    req = client.build_request("GET", "")
    assert req.url.query == b"data=1"
    assert req.url.params["data"] == "1"


def test_base_url_path_still_gets_trailing_slash() -> None:
    client = httpx.Client(base_url="https://example.org/path")
    assert str(client.base_url) == "https://example.org/path/"


def main() -> int:
    tests = [
        test_base_url_with_query_does_not_corrupt_query_when_enforcing_slash,
        test_base_url_path_still_gets_trailing_slash,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASSED {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAILED {t.__name__}: {e}")
    print(f"{len(tests) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
