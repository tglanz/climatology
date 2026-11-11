"""Retrospective adjacent-block stability heuristic; not a significance test."""

import math
import numpy as np
from numpy.typing import NDArray


def find_spinup_time(
    diagnostic: NDArray[np.floating],
    window_size: int = 10,
    stable_time: int = 10,
    z_threshold: float = 2.0,
) -> int | None:
    if (
        window_size < 2
        or stable_time < 1
        or not np.isfinite(z_threshold)
        or z_threshold <= 0
    ):
        raise ValueError("invalid spinup settings")
    x = np.asarray(diagnostic, dtype=np.float64)
    if x.ndim != 1 or not np.isfinite(x).all():
        raise ValueError("spinup diagnostic must be a finite 1D series")
    required = max(1, math.ceil(stable_time / window_size))
    n_windows = len(x) // window_size
    if n_windows < required + 1:
        return None
    scale = np.max(np.abs(x))
    if scale > 0:
        x = x / scale
    windows = x[: n_windows * window_size].reshape(n_windows, window_size)
    means = windows.mean(axis=1)
    variances = windows.var(axis=1, ddof=1)
    # Floors apply after nondimensionalization, so changing physical units is harmless.
    floor = 1e-12
    std_err = np.sqrt(variances / window_size) + floor
    mean_change = np.abs(np.diff(means)) / (std_err[1:] + std_err[:-1])
    variance_change = np.abs(np.diff(np.log(variances + floor)))
    stable = (mean_change < z_threshold) & (variance_change < z_threshold)
    for i in range(len(stable) - required + 1):
        if stable[i : i + required].all():
            return (i + 1) * window_size
    return None
