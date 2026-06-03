"""
https://en.wikipedia.org/wiki/Enstrophy
"""
from typing import Union

from ml.diagnostics.spatial import area_mean

import numpy as np
import torch

def enstrophy_density(vorticity: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
    return 0.5 * vorticity**2


def mean_enstrophy(vor: np.ndarray, latitudes_deg: np.ndarray) -> np.ndarray:
    """
    Global mean enstrophy: the area-weighted spatial average of
    `0.5 * vor**2`. Treats the (lat, lon) axes as the trailing two dims.

    Why it is meaningful: scalar summary of the flow's vorticity
    magnitude. Decays under hyperdiffusion and is sourced by stochastic
    stirring; comparing it across simulations is a quick health check
    for spinup and statistical equilibrium.

    See https://en.wikipedia.org/wiki/Enstrophy.

    Args:
        vor:           (..., H, W) array of vorticity.
        latitudes_deg: 1D array of length H.

    Returns: array of shape (...,).
    """
    return area_mean(enstrophy_density(vor), latitudes_deg)