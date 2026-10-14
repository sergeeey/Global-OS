"""Oracle-isolating view of World for executing agents.

CONSTITUTION / experimental integrity: agents must not read World.oracle.
Only the independent evaluator may access oracle fields.
"""

from __future__ import annotations

from typing import Any

from global_os.evals.goal_engineering.tasks import World


class OracleLeakError(RuntimeError):
    """Raised when an executing agent attempts to read the hidden oracle."""


class AgentView:
    """Read/write facade over World.state; oracle access is forbidden."""

    __slots__ = ("_world",)

    def __init__(self, world: World) -> None:
        self._world = world

    @property
    def task_id(self) -> str:
        return self._world.task_id

    @property
    def domain(self) -> str:
        return self._world.domain

    @property
    def state(self) -> dict[str, Any]:
        return self._world.state

    @property
    def log(self) -> list[dict[str, Any]]:
        return self._world.log

    def record(self, kind: str, **payload: Any) -> None:
        self._world.record(kind, **payload)

    @property
    def oracle(self) -> Any:
        raise OracleLeakError(
            "agents must not read World.oracle; only independent_evaluator may"
        )

    def __getattr__(self, name: str) -> Any:
        if name == "oracle":
            raise OracleLeakError(
                "agents must not read World.oracle; only independent_evaluator may"
            )
        raise AttributeError(name)
