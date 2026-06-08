from typing import Callable

import torch
import torch.nn as nn

from ml.config import LossKind
from ml.diagnostics import lat_weighted_relative_l2_torch


LossFn = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


def create_loss_fn(kind: str, lat_weights: torch.Tensor | None = None) -> LossFn:
    if kind == LossKind.MSE:
        return nn.MSELoss()

    if kind == LossKind.RELATIVE_L2:
        def relative_l2(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
            return torch.mean(
                torch.norm(pred - target, dim=(-2, -1))
                / torch.norm(target, dim=(-2, -1))
            )
        return relative_l2

    if kind == LossKind.LAT_WEIGHTED_RELATIVE_L2:
        assert lat_weights is not None, "lat_weighted_relative_l2 requires lat_weights"
        # lat_weights lives on CPU at construction time; move lazily to match pred device
        weights_holder = {"w": lat_weights}

        def lat_weighted_relative_l2_loss(
            pred: torch.Tensor, target: torch.Tensor
        ) -> torch.Tensor:
            w = weights_holder["w"]
            if w.device != pred.device:
                w = w.to(pred.device)
                weights_holder["w"] = w
            return lat_weighted_relative_l2_torch(pred, target, w)

        return lat_weighted_relative_l2_loss

    raise ValueError(f"unknown loss: {kind}")
