"""T2 SOP skill packs (MetaGPT-inspired, ADR-0013).

Not a fixed swarm architecture. OrgCompiler still chooses topology (GOS-I30).
Packs provide typed artifact handoff schemas only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HandoffSchema:
    name: str
    required_fields: tuple[str, ...]
    producer_role: str
    consumer_role: str


@dataclass(frozen=True)
class SopPack:
    pack_id: str
    title: str
    handoffs: tuple[HandoffSchema, ...]
    suggested_topology: str  # hint only — never forced axiom
    trust_zone: str = "T2"

    def to_dict(self) -> dict[str, Any]:
        return {
            "pack_id": self.pack_id,
            "title": self.title,
            "trust_zone": self.trust_zone,
            "suggested_topology": self.suggested_topology,
            "handoffs": [
                {
                    "name": h.name,
                    "required_fields": list(h.required_fields),
                    "producer_role": h.producer_role,
                    "consumer_role": h.consumer_role,
                }
                for h in self.handoffs
            ],
        }


SOFTWARE_SOP_V1 = SopPack(
    pack_id="sop.software.v1",
    title="Artifact-first software handoff pack",
    suggested_topology="pipeline",  # hint; OrgCompiler may pick single_solver
    handoffs=(
        HandoffSchema(
            "prd",
            ("user_stories", "acceptance_criteria"),
            "analyst",
            "architect",
        ),
        HandoffSchema(
            "design",
            ("components", "interfaces"),
            "architect",
            "implementer",
        ),
        HandoffSchema(
            "implementation",
            ("files_touched", "tests"),
            "implementer",
            "reviewer",
        ),
        HandoffSchema(
            "review",
            ("findings", "decision"),
            "reviewer",
            "integrator",
        ),
    ),
)

_REGISTRY: dict[str, SopPack] = {SOFTWARE_SOP_V1.pack_id: SOFTWARE_SOP_V1}


def load_sop_pack(pack_id: str) -> SopPack:
    if pack_id not in _REGISTRY:
        raise KeyError(f"unknown SOP pack: {pack_id}")
    return _REGISTRY[pack_id]


def validate_handoff(pack: SopPack, handoff_name: str, artifact: dict[str, Any]) -> list[str]:
    """Return list of missing required fields (empty = ok)."""
    target = next((h for h in pack.handoffs if h.name == handoff_name), None)
    if target is None:
        return [f"unknown_handoff:{handoff_name}"]
    return [f for f in target.required_fields if f not in artifact or artifact[f] in (None, "")]


def hierarchy_not_default_axiom(pack: SopPack) -> bool:
    """GOS-I30: pack must not claim recursive_hierarchy as proven optimal."""
    return pack.suggested_topology != "recursive_hierarchy" or pack.trust_zone == "T3"
