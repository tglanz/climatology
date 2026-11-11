"""Validation-window objectives with equally weighted training-simulation means."""

import torch
from torch.utils.data import DataLoader

from ml.training.loss import LossFn


def _score(
    val_loader: DataLoader, loss_fn: LossFn, prediction, target_index: int | None
) -> float:
    total, count = 0.0, 0
    with torch.no_grad():
        for _, y in val_loader:
            if target_index is not None:
                y = y[:, target_index : target_index + 1]
            if y.shape[1] != 1:
                raise ValueError("score physical baseline targets separately")
            total += loss_fn(prediction(y), y).item() * len(y)
            count += len(y)
    if count == 0:
        raise ValueError("baseline evaluation has no samples")
    return total / count


def score_zero(
    val_loader: DataLoader, loss_fn: LossFn, target_index: int | None = None
) -> float:
    return _score(val_loader, loss_fn, torch.zeros_like, target_index)


def score_mean(
    simulation_targets: torch.Tensor,
    val_loader: DataLoader,
    loss_fn: LossFn,
    target_index: int | None = None,
) -> float:
    if simulation_targets.ndim != 3 or len(simulation_targets) == 0:
        raise ValueError("training baseline needs one target per simulation")
    if not torch.isfinite(simulation_targets).all():
        raise ValueError("training baseline targets must be finite")
    if target_index is not None:
        simulation_targets = simulation_targets[:, target_index : target_index + 1]
    mean = simulation_targets.mean(dim=0, keepdim=True)
    return _score(val_loader, loss_fn, lambda y: mean.expand_as(y), target_index)
