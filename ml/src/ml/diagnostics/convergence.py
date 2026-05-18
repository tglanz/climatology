"""
Convergence diagnostics for forced-dissipative barotropic simulations:
spinup-time detection on the global enstrophy series, and time-mean
zonal-mean profiles used to compare within and across simulations.
"""

from __future__ import annotations

import numpy as np

from ml.diagnostics import mean_enstrophy, zonal_mean


def compute_enstrophy(snapshots: np.ndarray, latitudes_deg: np.ndarray) -> np.ndarray:
    return mean_enstrophy(snapshots, latitudes_deg)


def find_spinup_time(
    enstrophy_series: np.ndarray,
    window: int = 8,
    tol: float = 0.05,
    hold: int = 3,
) -> int:
    series = np.asarray(enstrophy_series, dtype=np.float64)
    T = series.shape[0]
    if T < window + hold:
        raise ValueError(
            f"series length {T} too short for window={window}, hold={hold}"
        )

    kernel = np.ones(window) / window
    rolling = np.convolve(series, kernel, mode="valid")
    target = float(rolling[-window:].mean())
    if target == 0.0:
        raise ValueError("long-run mean is zero; cannot compute relative deviation")

    within = np.abs(rolling - target) / abs(target) < tol
    for start in range(len(within) - hold + 1):
        if within[start : start + hold].all():
            return start + window - 1

    raise ValueError(
        f"no plateau found (tol={tol}, window={window}, hold={hold}); "
        f"series may not have reached statistical equilibrium"
    )


def compute_time_mean_zonal_mean(snapshots: np.ndarray, a: int, b: int) -> np.ndarray:
    assert (
        0 <= a < b <= snapshots.shape[0]
    ), f"need 0 <= {a} < {b} <= {snapshots.shape[0]}"
    return zonal_mean(snapshots[a:b]).mean(axis=0)
