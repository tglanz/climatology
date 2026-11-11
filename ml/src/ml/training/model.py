"""Neural operators with explicit physical coordinates and Gaussian SHTs."""

from dataclasses import asdict, dataclass

import numpy as np
import torch
import torch.nn as nn
from neuralop.layers.embeddings import GridEmbedding2D
from neuralop.layers.spherical_convolution import SphericalConv
from neuralop.models import FNO

from ml import patches
from ml.config import ModelConfig
from ml.diagnostics.grid import GaussianGrid


class CoordinateEmbedding(GridEmbedding2D):
    def __init__(self, in_channels: int, grid: GaussianGrid):
        super().__init__(in_channels)
        self.spatial_shape = grid.shape
        lat, lon = np.meshgrid(
            grid.latitudes / 90, grid.longitudes / 360, indexing="ij"
        )
        self.register_buffer(
            "coordinates",
            torch.tensor(np.stack((lat, lon)), dtype=torch.float32)[None],
            persistent=False,
        )

    def forward(self, data, batched=True):
        if not batched:
            data = data.unsqueeze(0)
        if data.ndim != 4 or tuple(data.shape[-2:]) != self.spatial_shape:
            raise ValueError("input shape differs from saved physical coordinates")
        coordinates = self.coordinates.to(dtype=data.dtype).expand(
            data.shape[0], -1, -1, -1
        )
        result = torch.cat((data, coordinates), dim=1)
        return result if batched else result.squeeze(0)


class GaussianSphericalConv(SphericalConv):
    """The transform expects north-to-south rows; callers retain Isca row order."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, sht_grids="legendre-gauss", **kwargs)

    def forward(self, x, output_shape=None):
        return super().forward(x.flip(-2), output_shape=output_shape).flip(-2)


class ZonalMeanWrapper(nn.Module):
    def __init__(self, model: nn.Module, grid: GaussianGrid):
        super().__init__()
        self.model = model
        self.grid = grid

    def state_dict(self, *args, **kwargs):
        state = super().state_dict(*args, **kwargs)
        # Neuraloperator adds constructor objects; our metadata owns reconstruction.
        state.pop("_metadata", None)
        return state

    def forward(self, x):
        return self.model(x).mean(dim=-1)


def build_model(cfg: ModelConfig, grid: GaussianGrid, dropout: float | None = None):
    sub = cfg.active_sub_config()
    height, width = grid.shape
    if sub.n_modes[0] > height or sub.n_modes[1] > width:
        raise ValueError("model mode counts exceed the data grid")
    if cfg.architecture == "sfno":
        if not grid.south_to_north:
            raise ValueError("SFNO currently requires south-to-north Isca coordinates")
        if (
            sub.n_modes[1] < 2
            or sub.n_modes[1] % 2
            or sub.n_modes[1] // 2 > sub.n_modes[0]
        ):
            raise ValueError(
                "SFNO longitude modes must be even and compatible with harmonic degree"
            )
    model = _build_operator(cfg, CoordinateEmbedding(sub.in_channels, grid), dropout)
    return ZonalMeanWrapper(model, grid)


def _build_operator(
    cfg: ModelConfig, embedding: GridEmbedding2D | str, dropout: float | None
):
    sub = cfg.active_sub_config()
    kwargs = asdict(sub)
    kwargs["n_modes"] = tuple(sub.n_modes)
    kwargs["positional_embedding"] = embedding
    if dropout is not None:
        kwargs["channel_mlp_dropout"] = dropout
    if cfg.architecture == "sfno":
        patches.apply()
        kwargs["conv_module"] = GaussianSphericalConv
    return FNO(**kwargs)


@dataclass(frozen=True)
class ParameterCounts:
    total: int
    trainable: int


def model_parameter_counts(
    cfg: ModelConfig, dropout: float | None = None
) -> ParameterCounts:
    """Inspect learned dimensions without constructing or assuming a physical grid."""
    model = _build_operator(cfg, "grid", dropout)
    return ParameterCounts(
        sum(p.numel() for p in model.parameters()),
        sum(p.numel() for p in model.parameters() if p.requires_grad),
    )
