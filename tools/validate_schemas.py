"""Validate all JSON Schema files under contracts/schemas."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    schemas = sorted((root / "contracts" / "schemas").glob("*.schema.json"))
    if not schemas:
        print("ERROR: no schemas found", file=sys.stderr)
        return 1
    errors = 0
    for path in schemas:
        with path.open(encoding="utf-8") as fh:
            schema = json.load(fh)
        try:
            Draft202012Validator.check_schema(schema)
            print(f"OK  {path.name}")
        except Exception as exc:  # noqa: BLE001 — report all schema errors
            errors += 1
            print(f"FAIL {path.name}: {exc}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
