"""
NOTE: this is shitty file. no need for re-exports. With time ill remove usages of those re-exports and remove this.

Diagnostics: the single home for semantic computations on physical fields.

This module collects the named, well-defined quantities used elsewhere
in the codebase: cos-lat area weights, area-weighted spatial reductions,
pointwise and reduced error metrics, zonal power spectra, and physical
invariants such as enstrophy. It also hosts the persistence-prediction
baseline.
"""

from __future__ import annotations

from typing import Union

import numpy as np
import torch

def lat_weighted_relative_l2_torch(
    pred: torch.Tensor,
    truth: torch.Tensor,
    lat_weights: torch.Tensor,
) -> torch.Tensor:
    if pred.ndim == 4:
        wb = lat_weights.view(1, 1, -1, 1)
        num = ((pred - truth).pow(2) * wb).sum(dim=(-2, -1)).sqrt()
        den = (truth.pow(2) * wb).sum(dim=(-2, -1)).sqrt()
    else:
        wb = lat_weights.view(1, 1, -1)
        num = ((pred - truth).pow(2) * wb).sum(dim=-1).sqrt()
        den = (truth.pow(2) * wb).sum(dim=-1).sqrt()
    return (num / den).mean()

def persistence_prediction(x: Union[np.ndarray, torch.Tensor], vor_t_channel: int) -> Union[np.ndarray, torch.Tensor]:
    """
    Persistence baseline: predict next-step vorticity to be equal to the
    current vorticity. Returns the slice
    `x[:, vor_t_channel : vor_t_channel + 1, :, :]`.

    For a lag-stacked input layout (channels are
    [vor_{t-K+1}, stirring_{t-K+1}, ..., vor_t, stirring_t]), the caller
    supplies the index of the most-recent vor channel, typically
    `(K - 1) * len(x_vars) + x_vars.index("vor")`.

    Why it is meaningful: any model that fails to beat persistence is
    not learning useful dynamics. It is the simplest reference baseline
    in time-series forecasting.

    Backend-agnostic via array slicing, which behaves identically on
    numpy and torch.

    See https://en.wikipedia.org/wiki/Persistence_forecasting.
    """
    return x[:, vor_t_channel : vor_t_channel + 1, :, :]

from ml.diagnostics.spatial import (
    zonal_mean,
)

from ml.diagnostics.convergence import (
    compute_time_mean_zonal_mean,
    find_zonal_mean_convergence_time,
    zonal_mean_convergence_errors,
)

from ml.diagnostics.spinup import (
    find_spinup_time,
)

from ml.diagnostics.enstrophy import (
    enstrophy_density,
    mean_enstrophy,
)

from ml.diagnostics.spectra import (
    zonal_power_spectrum,
    zonal_power_spectrum_torch,
    lat_weighted_zonal_power_spectrum,
)

from ml.diagnostics.errors import (
    absolute_error,
    relative_error,
    rms_error,
    signed_error,
)