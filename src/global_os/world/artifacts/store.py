"""Content-addressed artifact store (SHA-256)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ArtifactRef:
    digest: str
    media_type: str
    size_bytes: int
    path: str


class ArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def put_bytes(
        self, data: bytes, *, media_type: str = "application/octet-stream"
    ) -> ArtifactRef:
        digest = f"sha256:{hashlib.sha256(data).hexdigest()}"
        rel = digest.replace(":", "/")
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(data)
        return ArtifactRef(
            digest=digest, media_type=media_type, size_bytes=len(data), path=str(path)
        )

    def put_json(self, obj: Any) -> ArtifactRef:
        payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
        return self.put_bytes(payload, media_type="application/json")

    def get_bytes(self, digest: str) -> bytes:
        path = self.root / digest.replace(":", "/")
        return path.read_bytes()
