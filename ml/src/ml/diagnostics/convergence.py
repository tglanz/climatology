"""
Convergence diagnostics for forced-dissipative barotropic simulations:
spinup-time detection on the global enstrophy series, time-mean
zonal-mean profiles, and convergence-time detection on a running
time-mean diagnostic.
"""

from __future__ import annotations

import numpy as np

from ml.diagnostics.spatial import cosine_latitude_weights, zonal_mean

def compute_time_mean_zonal_mean(snapshots: np.ndarray, a: int, b: int) -> np.ndarray:
    assert (
        0 <= a < b <= snapshots.shape[0]
    ), f"need 0 <= {a} < {b} <= {snapshots.shape[0]}"
    return zonal_mean(snapshots[a:b]).mean(axis=0)


def zonal_mean_convergence_errors(
    field: np.ndarray,
    latitudes_deg: np.ndarray,
    t_s: int,
) -> np.ndarray:
    M = field.shape[0]
    assert 0 <= t_s < M, f"need 0 <= t_s={t_s} < M={M}"

    reference = compute_time_mean_zonal_mean(field, t_s, M)
    w = cosine_latitude_weights(latitudes_deg)
    ref_norm2 = float(np.sum(w * reference**2))
    if ref_norm2 == 0.0:
        raise ValueError("reference norm is zero; cannot compute relative error")

    n_i = M - t_s - 1
    errors = np.empty(n_i, dtype=np.float64)
    for k in range(n_i):
        i = k + 1
        running = compute_time_mean_zonal_mean(field, t_s, t_s + i)
        errors[k] = float(
            np.sqrt(np.sum(w * (running - reference) ** 2) / ref_norm2)
        )
    return errors


def find_zonal_mean_convergence_time(
    field: np.ndarray,
    latitudes_deg: np.ndarray,
    t_s: int,
    threshold: float = 0.05,
    hold: int = 3,
) -> int:
    """
    Smallest absolute snapshot index at which the running time-mean
    zonal-mean of `field` has settled onto the long-run reference.
    Returns t_s + i, where i is the smallest window length such that
    the convergence-error curve stays below `threshold` for `hold`
    consecutive entries.

    Pass t_s = 0 when no spin-up has been detected.

    Raises ValueError when the convergence criterion is not met
    anywhere within the trajectory.
    """
    errors = zonal_mean_convergence_errors(field, latitudes_deg, t_s)
    if len(errors) < hold:
        raise ValueError(
            f"convergence series length {len(errors)} too short for hold={hold}"
        )

    below = errors < threshold
    for start in range(len(below) - hold + 1):
        if below[start : start + hold].all():
            return t_s + (start + 1)

    return None