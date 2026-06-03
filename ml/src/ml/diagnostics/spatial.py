from typing import Union
import numpy as np
import torch

def cosine_latitude_weights(
    latitudes: np.ndarray,
    angle_units: str = "degree",
    normalize: str = "mean1"
) -> np.ndarray:
    if angle_units == "degree":
        rad = np.deg2rad(np.asarray(latitudes, dtype=np.float64))
    elif angle_units == "radian":
        rad = latitudes
    else:
        raise ValueError(f"unknown angle_units {angle_units}")

    w = np.cos(rad)
    w = np.clip(w, 0.0, None)
    if normalize == "mean1":
        return w / w.mean()
    if normalize == "sum1":
        return w / w.sum()
    if normalize == "none":
        return w
    raise ValueError(f"unknown normalize: {normalize!r}")

def area_mean(field: np.ndarray, latitudes_deg: np.ndarray) -> np.ndarray:
    """
    Area-weighted spatial mean of a field on a regular lat-lon grid.

    Why it is meaningful: this is the natural global spatial average for
    a quantity defined on the sphere. Equivalent to the integral over
    the sphere divided by the surface area when latitudes_deg samples a
    Gaussian or uniform grid.

    See https://en.wikipedia.org/wiki/Spherical_coordinate_system
    (the area element).

    Args:
        field:         (..., H, W) array. Trailing dims are (lat, lon).
        latitudes_deg: 1D array of length H.

    Returns: array of shape (...,), the spatial mean per leading slice.
    """
    w = cosine_latitude_weights(latitudes_deg)
    return (field * w[:, None]).mean(axis=(-2, -1))


def area_l2_norm(field: np.ndarray, latitudes_deg: np.ndarray) -> np.ndarray:
    """
    Area-weighted L2 norm: `sqrt(area_mean(field**2))`. Useful as the
    denominator of a relative-L2 error on a sphere.

    See https://en.wikipedia.org/wiki/Lp_space.
    """
    return np.sqrt(area_mean(field**2, latitudes_deg))


def zonal_mean(field: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
    """
    Average over the longitude (last) axis
    See https://en.wikipedia.org/wiki/Zonal_and_meridional_flow.
    """
    return field.mean(-1)


def zonal_anomaly(field: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
    """
    Field minus its zonal mean: the "eddy" part with the latitudinal band structure removed
    See https://en.wikipedia.org/wiki/Zonal_and_meridional_flow.
    """
    return field - zonal_mean(field)[..., None]