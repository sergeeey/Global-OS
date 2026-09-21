"""Supported organization topologies — contracts P0; superiority P1 (GOS-I30)."""

from __future__ import annotations

from enum import Enum


class OrganizationTopology(str, Enum):
    SINGLE_SOLVER = "single_solver"
    PIPELINE = "pipeline"
    MANAGER_WORKERS = "manager_workers"
    PARALLEL_WORKERS = "parallel_workers"
    RECURSIVE_HIERARCHY = "recursive_hierarchy"
    INDEPENDENT_ENSEMBLE = "independent_ensemble"
    SPECIALIST_CELLS = "specialist_cells"
    COMMITTEE = "committee"
    VERIFICATION_BRANCH = "verification_branch"
    HYBRID = "hybrid"


# Compilable today without claiming optimality.
IMPLEMENTED_TOPOLOGIES: frozenset[OrganizationTopology] = frozenset(
    {
        OrganizationTopology.SINGLE_SOLVER,
        OrganizationTopology.MANAGER_WORKERS,
        OrganizationTopology.PARALLEL_WORKERS,
    }
)

# Named but not yet full compilers — still valid enum members for contracts.
CONTRACTED_TOPOLOGIES: frozenset[OrganizationTopology] = frozenset(
    set(OrganizationTopology) - set(IMPLEMENTED_TOPOLOGIES)
)


def assert_not_default_truth(topology: OrganizationTopology) -> None:
    """Recursive hierarchy (or any topology) is never an architectural axiom."""
    if topology == OrganizationTopology.RECURSIVE_HIERARCHY:
        # Allowed as an experimental choice, never as silent default.
        return
