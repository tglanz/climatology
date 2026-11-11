"""Finite-reference running-mean diagnostics with Gaussian area quadrature."""

import numpy as np
from ml.diagnostics.grid import gaussian_latitude_weights
from ml.diagnostics.spatial import zonal_mean


def compute_time_mean_zonal_mean(snapshots: np.ndarray, a: int, b: int) -> np.ndarray:
    values = np.asarray(snapshots)
    if values.ndim != 3 or not 0 <= a < b <= len(values):
        raise ValueError(f"invalid climatology interval [{a}, {b}) or field shape")
    if not np.isfinite(values[a:b]).all():
        raise ValueError("climatology contains nonfinite values")
    return values[a:b].mean(axis=(0, 2), dtype=np.float64)


def zonal_mean_convergence_errors(
    field: np.ndarray, latitudes_deg: np.ndarray, t_s: int
) -> np.ndarray:
    values = np.asarray(field)
    if values.ndim != 3 or not 0 <= t_s < len(values):
        raise ValueError("invalid convergence field or reference start")
    if not np.isfinite(values).all():
        raise ValueError("convergence field contains nonfinite values")
    weights = gaussian_latitude_weights(latitudes_deg)
    profiles = values[t_s:].mean(axis=-1, dtype=np.float64)
    if profiles.shape[-1] != len(weights):
        raise ValueError("convergence field and latitude shapes differ")
    reference = profiles.mean(axis=0)
    ref_norm = np.sqrt(np.sum(weights * reference**2))
    if ref_norm == 0:
        raise ValueError("reference norm is zero; relative convergence is undefined")
    running = np.cumsum(profiles, axis=0)[:-1] / np.arange(1, len(profiles))[:, None]
    return np.sqrt(np.sum(weights * (running - reference) ** 2, axis=-1)) / ref_norm


def find_zonal_mean_convergence_time(
    field: np.ndarray,
    latitudes_deg: np.ndarray,
    t_s: int,
    threshold: float = 0.05,
    hold: int = 3,
) -> int | None:
    """Exclusive prefix endpoint of the first qualifying retrospective hold."""
    if not np.isfinite(threshold) or threshold <= 0 or hold < 1:
        raise ValueError("invalid convergence settings")
    errors = zonal_mean_convergence_errors(field, latitudes_deg, t_s)
    below = errors < threshold
    for start in range(len(below) - hold + 1):
        if below[start : start + hold].all():
            return t_s + start + 1
    return None
