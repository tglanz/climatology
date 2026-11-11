"""Spatial reductions with the actual Gaussian latitude quadrature."""

from typing import Union
import numpy as np
import torch

from ml.diagnostics.grid import gaussian_latitude_weights


def cosine_latitude_weights(
    latitudes: np.ndarray, angle_units: str = "degree", normalize: str = "mean1"
) -> np.ndarray:
    """Cosine approximation for uniform latitude spacing; not Gaussian quadrature."""
    if angle_units == "degree":
        rad = np.deg2rad(np.asarray(latitudes, dtype=np.float64))
    elif angle_units == "radian":
        rad = np.asarray(latitudes, dtype=np.float64)
    else:
        raise ValueError(f"unknown angle_units {angle_units}")
    w = np.clip(np.cos(rad), 0.0, None)
    if normalize == "mean1":
        return w / w.mean()
    if normalize == "sum1":
        return w / w.sum()
    if normalize == "none":
        return w
    raise ValueError(f"unknown normalize: {normalize!r}")


def area_mean(field: np.ndarray, latitudes_deg: np.ndarray) -> np.ndarray:
    """Area mean of (..., latitude, longitude) on a full Gaussian grid."""
    values = np.asarray(field)
    weights = gaussian_latitude_weights(latitudes_deg)
    if values.ndim < 2 or values.shape[-2] != len(weights):
        raise ValueError("field shape must end in (latitude, longitude)")
    if not np.isfinite(values).all():
        raise ValueError("field contains nonfinite values")
    return np.sum(values.mean(axis=-1) * weights, axis=-1)


def area_l2_norm(field: np.ndarray, latitudes_deg: np.ndarray) -> np.ndarray:
    return np.sqrt(area_mean(np.asarray(field, dtype=np.float64) ** 2, latitudes_deg))


def zonal_mean(
    field: Union[np.ndarray, torch.Tensor],
) -> Union[np.ndarray, torch.Tensor]:
    return field.mean(-1)


def zonal_anomaly(
    field: Union[np.ndarray, torch.Tensor],
) -> Union[np.ndarray, torch.Tensor]:
    return field - zonal_mean(field)[..., None]
