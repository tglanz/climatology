from typing import Union
import numpy as np
import torch

def zonal_power_spectrum(field: np.ndarray) -> np.ndarray:
    """
    - FFT along each latitude
    - Compute the power (magnitude squared)

    Given a 2d signal (lats, lons); The output is (lat, harmonics_amplitude_squared)
    where len(harmonics_amplitude_squared) is about len(lons) // 2

    See https://en.wikipedia.org/wiki/Spectral_density.
    """
    return np.abs(np.fft.rfft(field, axis=-1)) ** 2


def zonal_power_spectrum_torch(field: torch.Tensor) -> torch.Tensor:
    """
    Torch counterpart of `zonal_power_spectrum`
    Args:    field of shape (..., H, W).
    Returns: tensor of shape (..., H, W//2 + 1).
    """
    return torch.fft.rfft(field, dim=-1).abs().pow(2)


def lat_weighted_zonal_power_spectrum(
    field: np.ndarray, latitudes_deg: np.ndarray
) -> np.ndarray:
    """
    Cos-lat-weighted average of the zonal power spectrum over latitude:
    `(|rfft(field, axis=-1)|**2 * w[:, None]).sum(axis=-2) / w.sum()`,
    where `w = cos(lat)`. Collapses the latitude axis with proper area
    weighting so polar rows do not overcount.

    Why it is meaningful: a single 1D spectrum E(k) of how energy
    distributes across zonal wavenumbers, averaged over the sphere.
    The natural input to a k^-3 (enstrophy cascade) reference comparison.

    See https://en.wikipedia.org/wiki/Spectral_density.

    Args:
        field:         (..., H, W) array.
        latitudes_deg: 1D array of length H.

    Returns: array of shape (..., W//2 + 1).
    """
    w = cosine_latitude_weights(latitudes_deg, normalize="none")
    power = zonal_power_spectrum(field) * w[:, None]
    return power.sum(axis=-2) / w.sum()


def error_power_spectrum(pred: np.ndarray, truth: np.ndarray) -> np.ndarray:
    """
    Zonal power spectrum of the residual `pred - truth`. Reveals which
    spatial scales the model is missing.

    See https://en.wikipedia.org/wiki/Spectral_density.
    """
    return zonal_power_spectrum(pred - truth)


def signal_power_spectrum(truth: np.ndarray) -> np.ndarray:
    """
    Zonal power spectrum of the target field. Used as a reference to
    judge whether the prediction's energy distribution matches the
    truth's at each scale.

    See https://en.wikipedia.org/wiki/Spectral_density.
    """
    return zonal_power_spectrum(truth)


def spectrum_residual(pred: np.ndarray, truth: np.ndarray) -> np.ndarray:
    """
    Difference between the power spectra of the prediction and the truth:
    `signal_power_spectrum(pred) - signal_power_spectrum(truth)`.

    Distinct from `error_power_spectrum`: that one is the power spectrum
    of the residual (sensitive to phase). This one compares the two
    spectra directly, so it answers "does the model produce the right
    amount of energy at each scale, regardless of where in space".

    See https://en.wikipedia.org/wiki/Spectral_density.
    """
    return signal_power_spectrum(pred) - signal_power_spectrum(truth)

