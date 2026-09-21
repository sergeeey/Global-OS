"""Ensure GitHub Actions are pinned to full SHAs that resolve remotely."""

from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

USES_RE = re.compile(
    r"^\s*-\s*uses:\s*(?P<owner>[^/\s]+)/(?P<repo>[^@\s]+)@(?P<ref>[^\s#]+)",
    re.MULTILINE,
)


def _workflow_files() -> list[Path]:
    root = Path(__file__).resolve().parents[1]
    return sorted((root / ".github" / "workflows").glob("*.yml"))


def _is_full_sha(ref: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{40}", ref))


def _resolves(owner: str, repo: str, sha: str) -> tuple[bool, str]:
    url = f"https://api.github.com/repos/{owner}/{repo}/git/commits/{sha}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "global-os-action-pin-validator",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 200:
                return True, "ok"
            return False, f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return False, str(exc.reason)


def main() -> int:
    errors = 0
    found = 0
    for path in _workflow_files():
        text = path.read_text(encoding="utf-8")
        for match in USES_RE.finditer(text):
            found += 1
            owner = match.group("owner")
            repo = match.group("repo")
            ref = match.group("ref")
            label = f"{owner}/{repo}@{ref}"
            if not _is_full_sha(ref):
                print(f"FAIL {path.name}: {label} is not a full 40-char SHA", file=sys.stderr)
                errors += 1
                continue
            ok, detail = _resolves(owner, repo, ref)
            if not ok:
                print(f"FAIL {path.name}: {label} does not resolve ({detail})", file=sys.stderr)
                errors += 1
            else:
                print(f"OK   {path.name}: {label}")
    if found == 0:
        print("FAIL: no uses: pins found", file=sys.stderr)
        return 1
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
