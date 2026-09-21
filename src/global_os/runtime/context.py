"""Minimal in-process runtime context for CLI and local use."""

from __future__ import annotations

from global_os.epistemic import EpistemicStore
from global_os.kernel.action_gateway import ToolGateway
from global_os.kernel.authority import AuthorityKernel
from global_os.kernel.authority.kernel import AuthorityBackend
from global_os.memory import NullResultStore
from global_os.runtime.events import EventLedger
from global_os.runtime.goals import GoalStore
from global_os.runtime.profile import (
    RuntimeProfile,
    apply_production_guards,
    resolve_authority_backend,
    resolve_profile,
)


class RuntimeContext:
    def __init__(
        self,
        *,
        profile: RuntimeProfile | None = None,
        authority_backend: AuthorityBackend | None = None,
    ) -> None:
        self.profile: RuntimeProfile = profile if profile is not None else resolve_profile()
        backend = resolve_authority_backend(profile=self.profile, explicit=authority_backend)
        apply_production_guards(profile=self.profile, backend=backend)
        self.authority_backend = backend
        self.ledger = EventLedger()
        self.goals = GoalStore(self.ledger)
        self.authority = AuthorityKernel(self.ledger, backend=backend)
        self.gateway = ToolGateway(self.ledger)
        self.epistemic = EpistemicStore(self.ledger)
        self.null_results = NullResultStore(self.ledger)
