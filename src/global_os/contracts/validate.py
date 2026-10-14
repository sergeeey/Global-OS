"""JSON Schema loading and validation against contracts/."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator


def _find_schemas_dir() -> Path:
    """Resolve schemas for editable/repo checkout and installed wheels."""
    here = Path(__file__).resolve().parent
    packaged = here / "schemas"
    if packaged.is_dir() and any(packaged.glob("*.schema.json")):
        return packaged
    for parent in (here, *here.parents):
        candidate = parent / "contracts" / "schemas"
        if candidate.is_dir() and any(candidate.glob("*.schema.json")):
            return candidate
    raise FileNotFoundError(
        "contracts/schemas not found (packaged under global_os/contracts/schemas "
        "or repo contracts/schemas)"
    )


def _find_repo_root() -> Path:
    """Best-effort root above contracts/schemas (checkout) or package parent (wheel)."""
    return _find_schemas_dir().parent.parent


SCHEMAS_DIR = _find_schemas_dir()
REPO_ROOT = _find_repo_root()


@lru_cache(maxsize=32)
def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMAS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {path}")
    with path.open(encoding="utf-8") as fh:
        return cast(dict[str, Any], json.load(fh))


def validate(instance: dict[str, Any], schema_name: str) -> None:
    schema = load_schema(schema_name)
    Draft202012Validator(schema).validate(instance)


def list_schema_files() -> list[Path]:
    return sorted(SCHEMAS_DIR.glob("*.schema.json"))
