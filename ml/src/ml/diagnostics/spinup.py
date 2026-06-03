import numpy as np
from numpy.typing import NDArray

def find_spinup_time(
    diagnostic: NDArray[np.floating],
    window_size: int = 10,
    stable_time: int = 10,
    z_threshold: float = 2.0,
) -> int:
    x = np.asarray(diagnostic, dtype=np.float64)

    n_windows = len(x) // window_size
    if n_windows < 2:
        raise ValueError("Not enough data")

    x = x[: n_windows * window_size]
    windows = x.reshape(n_windows, window_size)

    means = windows.mean(axis=1)
    vars_ = windows.var(axis=1, ddof=1)

    std_err = np.sqrt(vars_ / window_size) + 1e-12

    z_mean = np.abs(means[1:] - means[:-1]) / (std_err[1:] + std_err[:-1])
    z_var = np.abs(np.log(vars_[1:] + 1e-12) - np.log(vars_[:-1] + 1e-12))

    stable = (z_mean < z_threshold) & (z_var < z_threshold)

    required = max(1, stable_time // window_size)

    for i in range(len(stable) - required + 1):
        if stable[i:i + required].all():
            return (i + 1) * window_size

    return None