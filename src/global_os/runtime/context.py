"""Minimal in-process runtime context for CLI and local use."""

from __future__ import annotations

from global_os.epistemic import EpistemicStore
from global_os.kernel.action_gateway import ToolGateway
from global_os.kernel.authority import AuthorityKernel
from global_os.memory import NullResultStore
from global_os.runtime.events import EventLedger
from global_os.runtime.goals import GoalStore


class RuntimeContext:
    def __init__(self) -> None:
        self.ledger = EventLedger()
        self.goals = GoalStore(self.ledger)
        self.authority = AuthorityKernel(self.ledger)
        self.gateway = ToolGateway(self.ledger)
        self.epistemic = EpistemicStore(self.ledger)
        self.null_results = NullResultStore(self.ledger)
