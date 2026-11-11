"""Training objectives reduce each target channel before averaging samples."""

from typing import Callable
import torch
import torch.nn as nn

from ml.config import LossKind
from ml.diagnostics.errors import lat_weighted_relative_l2_torch

LossFn = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


def create_loss_fn(kind: str, lat_weights: torch.Tensor | None = None) -> LossFn:
    if kind == LossKind.MSE:
        return nn.MSELoss()
    if kind not in (LossKind.RELATIVE_L2, LossKind.LAT_WEIGHTED_RELATIVE_L2):
        raise ValueError(f"unknown loss: {kind}")
    if kind == LossKind.LAT_WEIGHTED_RELATIVE_L2 and lat_weights is None:
        raise ValueError("latitude-weighted loss requires grid weights")

    def loss(pred: torch.Tensor, truth: torch.Tensor) -> torch.Tensor:
        weights = lat_weights if kind == LossKind.LAT_WEIGHTED_RELATIVE_L2 else None
        if weights is None:
            weights = torch.ones(pred.shape[2], dtype=pred.dtype, device=pred.device)
        return lat_weighted_relative_l2_torch(pred, truth, weights)

    return loss
