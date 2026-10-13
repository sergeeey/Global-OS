"""Fast structural copies for JSON-shaped data (dicts/lists/scalars).

Faster than ``copy.deepcopy`` for event/payload trees that contain only
JSON-serializable types. Preserves isolation for callers that mutate results.
"""

from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")


def jsonable_copy(obj: T) -> T:
    """Deep-copy JSON-shaped structures without deepcopy overhead."""
    if isinstance(obj, dict):
        return {k: jsonable_copy(v) for k, v in obj.items()}  # type: ignore[return-value]
    if isinstance(obj, list):
        return [jsonable_copy(v) for v in obj]  # type: ignore[return-value]
    if isinstance(obj, tuple):
        return tuple(jsonable_copy(v) for v in obj)  # type: ignore[return-value]
    return obj
