"""M-EXT5 initialization-induced Mpemba experiment core."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

from config import Config, he_scale


class MLP(nn.Module):
    def __init__(self, n_features: int, hidden: int, n_classes: int) -> None:
        super().__init__()
        self.fc1 = nn.Linear(n_features, hidden)
        self.fc2 = nn.Linear(hidden, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(F.relu(self.fc1(x)))


def make_synthetic_data(cfg: Config) -> tuple[TensorDataset, TensorDataset]:
    rng = np.random.default_rng(cfg.data_seed)
    w = rng.normal(0, 1, size=(cfg.n_features, cfg.n_classes))
    x_train = rng.normal(0, 1, size=(cfg.n_train, cfg.n_features))
    x_test = rng.normal(0, 1, size=(cfg.n_test, cfg.n_features))
    y_train = (x_train @ w).argmax(axis=1)
    y_test = (x_test @ w).argmax(axis=1)
    train = TensorDataset(
        torch.tensor(x_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.long),
    )
    test = TensorDataset(
        torch.tensor(x_test, dtype=torch.float32),
        torch.tensor(y_test, dtype=torch.long),
    )
    return train, test


def param_l2(a: nn.Module, b: nn.Module) -> float:
    total = 0.0
    for p, q in zip(a.parameters(), b.parameters(), strict=True):
        total += float(torch.sum((p.detach() - q.detach()) ** 2))
    return float(np.sqrt(total))


def init_scaled(model: nn.Module, factor: float, seed: int) -> None:
    g = torch.Generator()
    g.manual_seed(seed)
    with torch.no_grad():
        for p in model.parameters():
            if p.ndim >= 2:
                fan_in = p.shape[1]
                scale = he_scale(fan_in) * factor
                p.copy_(torch.empty_like(p).uniform_(-scale, scale, generator=g))
            else:
                p.zero_()


def train_reference(cfg: Config, train_ds: TensorDataset, device: str) -> dict[str, torch.Tensor]:
    torch.manual_seed(cfg.ref_seed)
    model = MLP(cfg.n_features, cfg.hidden_dim, cfg.n_classes).to(device)
    opt = torch.optim.SGD(model.parameters(), lr=cfg.lr, momentum=cfg.momentum)
    loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True)
    it = iter(loader)
    model.train()
    for _ in range(cfg.ref_train_steps):
        try:
            xb, yb = next(it)
        except StopIteration:
            it = iter(loader)
            xb, yb = next(it)
        xb, yb = xb.to(device), yb.to(device)
        opt.zero_grad(set_to_none=True)
        loss = F.cross_entropy(model(xb), yb)
        loss.backward()
        opt.step()
    return {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}


def load_state(model: nn.Module, state: dict[str, torch.Tensor], device: str) -> None:
    model.load_state_dict({k: v.to(device) for k, v in state.items()})


def batch_stream(
    train_ds: TensorDataset, batch_size: int, steps: int, seed: int
) -> list[tuple[torch.Tensor, torch.Tensor]]:
    """Precompute identical batch sequence for paired hot/cold."""
    g = torch.Generator()
    g.manual_seed(seed)
    loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, generator=g)
    batches: list[tuple[torch.Tensor, torch.Tensor]] = []
    it = iter(loader)
    for _ in range(steps):
        try:
            xb, yb = next(it)
        except StopIteration:
            it = iter(loader)
            xb, yb = next(it)
        batches.append((xb.clone(), yb.clone()))
    return batches


def _win(tau_h: int | None, tau_c: int | None) -> bool | None:
    if tau_h is None and tau_c is None:
        return None
    if tau_h is None:
        return False
    if tau_c is None:
        return True
    return tau_h < tau_c


@dataclass
class PairResult:
    seed_pair: int
    seed_batch: int
    d_hot0: float
    d_cold0: float
    valid_ordering: bool
    tau_hot_late: int | None
    tau_cold_late: int | None
    hot_wins_late: bool | None
    tau_hot_early: int | None
    tau_cold_early: int | None
    hot_wins_early: bool | None
    # aliases for gate/pilot compatibility (late = primary)
    tau_hot: int | None
    tau_cold: int | None
    hot_wins: bool | None
    final_loss_hot: float
    final_loss_cold: float
    early_gradnorm_hot: float
    early_gradnorm_cold: float
    n_updates_hot: int
    n_updates_cold: int


def run_arm(
    cfg: Config,
    train_ds: TensorDataset,
    ref_state: dict[str, torch.Tensor],
    init_factor: float,
    init_seed: int,
    batches: list[tuple[torch.Tensor, torch.Tensor]],
    device: str,
) -> tuple[int | None, int | None, float, float, float, int]:
    """Returns tau_late, tau_early, final_loss, d0, early_gradnorm, n_updates."""
    model = MLP(cfg.n_features, cfg.hidden_dim, cfg.n_classes).to(device)
    init_scaled(model, init_factor, init_seed)
    ref = MLP(cfg.n_features, cfg.hidden_dim, cfg.n_classes).to(device)
    load_state(ref, ref_state, device)
    d0 = param_l2(model, ref)
    opt = torch.optim.SGD(model.parameters(), lr=cfg.lr, momentum=cfg.momentum)
    tau_late: int | None = None
    tau_early: int | None = None
    grad_norms: list[float] = []
    n_updates = 0
    lv = float("nan")
    model.train()
    for step, (xb, yb) in enumerate(batches):
        xb, yb = xb.to(device), yb.to(device)
        opt.zero_grad(set_to_none=True)
        logits = model(xb)
        loss = F.cross_entropy(logits, yb)
        loss.backward()
        if step < 20:
            gn = 0.0
            for p in model.parameters():
                if p.grad is not None:
                    gn += float(torch.sum(p.grad.detach() ** 2))
            grad_norms.append(np.sqrt(gn))
        opt.step()
        n_updates += 1
        lv = float(loss.detach().cpu())
        if step % cfg.monitor_every == 0:
            if tau_early is None and lv <= cfg.loss_target_early:
                tau_early = step + 1
            if tau_late is None and lv <= cfg.loss_target_late:
                tau_late = step + 1
        if step + 1 >= cfg.max_steps:
            break
    early_gn = float(np.mean(grad_norms)) if grad_norms else 0.0
    return tau_late, tau_early, lv, d0, early_gn, n_updates


def run_pair(
    cfg: Config,
    train_ds: TensorDataset,
    ref_state: dict[str, torch.Tensor],
    seed_pair: int,
    seed_batch: int,
    device: str = "cpu",
) -> PairResult:
    batches = batch_stream(train_ds, cfg.batch_size, cfg.max_steps, seed_batch)
    seed_hot = seed_pair * 10 + 1
    seed_cold = seed_pair * 10 + 2
    tau_hl, tau_he, loss_h, d_h, gn_h, n_h = run_arm(
        cfg, train_ds, ref_state, cfg.sigma_hot_factor, seed_hot, batches, device
    )
    tau_cl, tau_ce, loss_c, d_c, gn_c, n_c = run_arm(
        cfg, train_ds, ref_state, cfg.sigma_cold_factor, seed_cold, batches, device
    )
    valid = d_h > d_c
    win_late = _win(tau_hl, tau_cl) if valid else None
    win_early = _win(tau_he, tau_ce) if valid else None
    return PairResult(
        seed_pair=seed_pair,
        seed_batch=seed_batch,
        d_hot0=d_h,
        d_cold0=d_c,
        valid_ordering=valid,
        tau_hot_late=tau_hl,
        tau_cold_late=tau_cl,
        hot_wins_late=win_late,
        tau_hot_early=tau_he,
        tau_cold_early=tau_ce,
        hot_wins_early=win_early,
        tau_hot=tau_hl,
        tau_cold=tau_cl,
        hot_wins=win_late,
        final_loss_hot=loss_h,
        final_loss_cold=loss_c,
        early_gradnorm_hot=gn_h,
        early_gradnorm_cold=gn_c,
        n_updates_hot=n_h,
        n_updates_cold=n_c,
    )


def result_to_dict(r: PairResult) -> dict[str, Any]:
    return {
        "seed_pair": r.seed_pair,
        "seed_batch": r.seed_batch,
        "d_hot0": r.d_hot0,
        "d_cold0": r.d_cold0,
        "valid_ordering": r.valid_ordering,
        "tau_hot_late": r.tau_hot_late,
        "tau_cold_late": r.tau_cold_late,
        "hot_wins_late": r.hot_wins_late,
        "tau_hot_early": r.tau_hot_early,
        "tau_cold_early": r.tau_cold_early,
        "hot_wins_early": r.hot_wins_early,
        "tau_hot": r.tau_hot,
        "tau_cold": r.tau_cold,
        "hot_wins": r.hot_wins,
        "final_loss_hot": r.final_loss_hot,
        "final_loss_cold": r.final_loss_cold,
        "early_gradnorm_hot": r.early_gradnorm_hot,
        "early_gradnorm_cold": r.early_gradnorm_cold,
        "n_updates_hot": r.n_updates_hot,
        "n_updates_cold": r.n_updates_cold,
    }


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
