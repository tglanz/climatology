"""Stable per-channel population moments and one reversible normalization contract."""

from dataclasses import dataclass

import torch
from torch import nn

from ml.data.metadata import DataMetadata


@dataclass
class RunningMoments:
    count: int = 0
    mean: torch.Tensor | None = None
    squared_deviation: torch.Tensor | None = None
    ndim: int | None = None

    def update(self, values: torch.Tensor) -> None:
        if values.ndim not in (3, 4) or values.shape[0] == 0:
            raise ValueError(
                "normalization needs nonempty (batch, channel, spatial...) arrays"
            )
        if not torch.isfinite(values).all():
            raise ValueError("normalization input contains nonfinite values")
        batch = (
            values.detach()
            .to(device="cpu", dtype=torch.float64)
            .movedim(1, 0)
            .flatten(1)
        )
        n = batch.shape[1]
        mean = batch.mean(dim=1)
        m2 = ((batch - mean[:, None]) ** 2).sum(dim=1)
        if self.count == 0:
            self.mean, self.squared_deviation = mean, m2
            self.ndim = values.ndim
        else:
            if self.ndim != values.ndim or self.mean.shape != mean.shape:
                raise ValueError("normalization channel shape changed")
            delta = mean - self.mean
            total = self.count + n
            self.squared_deviation += m2 + delta.square() * self.count * n / total
            self.mean += delta * n / total
        self.count += n

    def normalizer(self, epsilon: float = 1e-7) -> "ChannelNormalizer":
        if self.count == 0:
            raise ValueError("cannot fit normalization without training samples")
        shape = (1, -1, *([1] * (self.ndim - 2)))
        return ChannelNormalizer(
            self.mean.reshape(shape).float(),
            (self.squared_deviation / self.count)
            .clamp_min(0)
            .sqrt()
            .reshape(shape)
            .float(),
            epsilon,
        )


class ChannelNormalizer(nn.Module):
    def __init__(self, mean: torch.Tensor, std: torch.Tensor, epsilon: float):
        super().__init__()
        if mean.shape != std.shape or mean.ndim not in (3, 4):
            raise ValueError("invalid normalization statistic shapes")
        if (
            not torch.isfinite(mean).all()
            or not torch.isfinite(std).all()
            or (std < 0).any()
        ):
            raise ValueError(
                "normalization statistics must be finite with nonnegative std"
            )
        if not isinstance(epsilon, (float, int)) or not 0 < epsilon < float("inf"):
            raise ValueError("normalization epsilon must be finite and positive")
        self.register_buffer("mean", mean.detach().clone())
        self.register_buffer("std", std.detach().clone())
        self.epsilon = float(epsilon)

    def transform(self, values: torch.Tensor) -> torch.Tensor:
        return (values - self.mean) / (self.std + self.epsilon)

    def inverse_transform(self, values: torch.Tensor) -> torch.Tensor:
        return values * (self.std + self.epsilon) + self.mean


@dataclass
class Normalization:
    x: ChannelNormalizer
    y: ChannelNormalizer
    metadata: DataMetadata

    def to(self, device: torch.device) -> "Normalization":
        self.x.to(device)
        self.y.to(device)
        return self

    def to_dict(self) -> dict:
        return {
            "x_mean": self.x.mean.detach().cpu(),
            "x_std": self.x.std.detach().cpu(),
            "y_mean": self.y.mean.detach().cpu(),
            "y_std": self.y.std.detach().cpu(),
            "x_epsilon": self.x.epsilon,
            "y_epsilon": self.y.epsilon,
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, values: dict) -> "Normalization":
        if (
            "metadata" not in values
            or "x_epsilon" not in values
            or "y_epsilon" not in values
        ):
            raise ValueError(
                "unversioned normalization; regenerate and retrain with correctness preprocessing"
            )
        metadata = DataMetadata.from_dict(values["metadata"])
        result = cls(
            ChannelNormalizer(values["x_mean"], values["x_std"], values["x_epsilon"]),
            ChannelNormalizer(values["y_mean"], values["y_std"], values["y_epsilon"]),
            metadata,
        )
        if result.x.mean.shape != (1, metadata.input_channels, 1, 1):
            raise ValueError("input normalization shape differs from metadata")
        if result.y.mean.shape != (1, len(metadata.y_vars), 1):
            raise ValueError("target normalization shape differs from metadata")
        return result
