"""Raw zonal Fourier power; FFT coefficients use NumPy's default normalization."""

import numpy as np
from ml.diagnostics.grid import gaussian_latitude_weights


def zonal_power_spectrum(field: np.ndarray) -> np.ndarray:
    """Return |rfft(field)|**2 along longitude, without one-sided rescaling."""
    return np.abs(np.fft.rfft(field, axis=-1)) ** 2


def lat_weighted_zonal_power_spectrum(
    field: np.ndarray, latitudes_deg: np.ndarray
) -> np.ndarray:
    """Gaussian latitude average of raw zonal Fourier power."""
    weights = gaussian_latitude_weights(latitudes_deg)
    if np.ndim(field) < 2 or np.shape(field)[-2] != len(weights):
        raise ValueError("spectrum field shape must end in (latitude, longitude)")
    if not np.isfinite(field).all():
        raise ValueError("spectrum field contains nonfinite values")
    return np.sum(zonal_power_spectrum(field) * weights[:, None], axis=-2)
