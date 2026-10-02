"""M-EXT5 experiment configuration (serializable)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Config:
    # Data (synthetic — no torchvision dependency)
    n_features: int = 64
    n_classes: int = 10
    n_train: int = 4000
    n_test: int = 1000
    data_seed: int = 0

    # Model
    hidden_dim: int = 64

    # Optimization (identical for hot/cold)
    lr: float = 0.05
    batch_size: int = 64
    max_steps: int = 1500
    momentum: float = 0.0  # vanilla SGD for identical dynamics

    # Init construction (fixed-LR Mpemba construction)
    sigma_hot_factor: float = 2.0
    sigma_cold_factor: float = 0.3
    # H_e = default kaiming-uniform scale proxy = sqrt(6 / fan_in)

    # Targets (both locked before confirmatory; see PREREG.md)
    # LATE = nearer "final regime"; EARLY = mid-training threshold (secondary)
    loss_target_late: float = 0.35
    loss_target_early: float = 1.0
    # Validity: require D_L2(hot, θ_ref) > D_L2(cold, θ_ref) at t=0
    # Back-compat alias used only in older gate snippets
    loss_target: float = 0.35

    # Reference θ*
    ref_train_steps: int = 4000
    ref_seed: int = 12345

    # Monitoring
    monitor_every: int = 5

    protocol_id: str = "M-EXT5-INIT-MPEMBA-v1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def he_scale(fan_in: int) -> float:
    """Kaiming-uniform half-range proxy used as H_e."""
    import math

    return math.sqrt(6.0 / float(fan_in))
