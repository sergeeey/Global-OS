"""Arm B regression harness for httpx#3614."""
from __future__ import annotations
import sys
from pathlib import Path

WT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/httpx-mext3-armB")
sys.path.insert(0, str(WT))
import httpx


def test_query_preserved() -> None:
    client = httpx.Client(base_url="https://example.org/get?data=1")
    assert client.base_url.query == b"data=1"
    assert client.base_url.params["data"] == "1"
    req = client.build_request("GET", "")
    assert req.url.query == b"data=1"


def test_path_slash_preserved() -> None:
    client = httpx.Client(base_url="https://example.org/api")
    assert str(client.base_url) == "https://example.org/api/"


def main() -> int:
    failed = 0
    for t in (test_query_preserved, test_path_slash_preserved):
        try:
            t(); print(f"PASSED {t.__name__}")
        except Exception as e:
            failed += 1; print(f"FAILED {t.__name__}: {e}")
    print(f"{2 - failed} passed, {failed} failed")
    return bool(failed)

if __name__ == "__main__":
    raise SystemExit(main())
