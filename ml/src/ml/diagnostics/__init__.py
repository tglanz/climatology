"""
Diagnostics: the single home for semantic computations on physical fields.

This module collects the named, well-defined quantities used elsewhere
in the codebase: cos-lat area weights, area-weighted spatial reductions,
pointwise and reduced error metrics, zonal power spectra, and physical
invariants such as enstrophy. It also hosts the persistence-prediction
baseline.

Invariants this module guarantees:

- All functions are pure: outputs depend only on arguments. No reading
  from disk, no global state, no caching, no side effects.
- All functions are stateless. No classes with internal state. No
  closures over module-level mutables.
- Naming convention. The default (unsuffixed) implementation is numpy.
  A `_torch` suffix indicates a torch-tensor variant added because a
  torch-side consumer (typically the training loss path or the
  per-epoch metrics writer) needs it. A function whose body works
  identically on numpy and torch through Python operators or method
  duck typing has no suffix and a `Union[np.ndarray, torch.Tensor]`
  type hint. Torch variants are introduced only when actually required;
  there is no automatic mirroring.
- Per-function docstrings explain what each function computes and why
  it is meaningful, not how. Implementation comments live next to the
  relevant code lines only if a reader would otherwise be lost.
"""

from __future__ import annotations

from typing import Union

import numpy as np
import torch

# Type alias for functions whose body is identical on numpy and torch
# through operator overloading or method duck typing. Use it only for
# functions that genuinely work on either type without dispatch.
ArrayLike = Union[np.ndarray, torch.Tensor]


# ----- weights ---------------------------------------------------------


def cosine_latitude_weights(
    latitudes_deg: np.ndarray, normalize: str = "mean1"
) -> np.ndarray:
    """
    Cosine-of-latitude area weights for fields on a regular lat-lon grid.

    Why it is meaningful: the area element on the unit sphere is
    `cos(lat) dlat dlon`, so cos(lat) is the per-row weight that turns a
    raw sum over a lat-lon grid into a true area-weighted spatial
    integral. Without it, polar cells (which cover little physical area)
    are over-counted relative to equatorial ones.

    See https://en.wikipedia.org/wiki/Spherical_coordinate_system
    (surface element on the unit sphere).

    Args:
        latitudes_deg: 1D array of latitudes in degrees.
        normalize:
            "mean1" - divide by the mean so the weights have mean 1.
                      Useful when the consumer takes a spatial mean and
                      wants the result to stay on the same scale as an
                      unweighted mean.
            "sum1"  - divide by the sum so the weights are a proper
                      probability measure over latitude.
            "none"  - raw cos(lat), clipped at 0 to guard against tiny
                      negative values from floating-point representation
                      of latitudes slightly outside [-90, 90].

    Returns: 1D float64 numpy array of length len(latitudes_deg).
    """
    rad = np.deg2rad(np.asarray(latitudes_deg, dtype=np.float64))
    w = np.cos(rad)
    w = np.clip(w, 0.0, None)
    if normalize == "mean1":
        return w / w.mean()
    if normalize == "sum1":
        return w / w.sum()
    if normalize == "none":
        return w
    raise ValueError(f"unknown normalize: {normalize!r}")


def cosine_latitude_weights_torch(
    latitudes_deg: np.ndarray,
    normalize: str = "mean1",
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """
    Torch-tensor version of `cosine_latitude_weights`. Used by the
    training loss path. Numerical semantics are identical; only the
    return type differs.

    Returns a CPU tensor of the requested dtype. The caller is
    responsible for moving it to a target device with `.to(device)`.
    """
    w_np = cosine_latitude_weights(latitudes_deg, normalize=normalize)
    np_dtype = np.float32 if dtype == torch.float32 else np.float64
    return torch.from_numpy(w_np.astype(np_dtype)).to(dtype)


# ----- spatial reductions ----------------------------------------------


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


def zonal_mean(field: ArrayLike) -> ArrayLike:
    """
    Average over the longitude (last) axis. Backend-agnostic: works on
    numpy arrays and torch tensors via the positional-axis form of
    `.mean(-1)`, which both libraries support.

    Why it is meaningful: the zonal mean of an atmospheric field reveals
    its latitudinally banded structure (jets, baroclinic regions) free
    of the eddies that vary with longitude. Standard reference line in
    atmospheric dynamics.

    See https://en.wikipedia.org/wiki/Zonal_and_meridional_flow.
    """
    return field.mean(-1)


def zonal_anomaly(field: ArrayLike) -> ArrayLike:
    """
    Field minus its zonal mean: the "eddy" part with the latitudinal
    band structure removed. Backend-agnostic via `zonal_mean` and
    broadcasting.

    See https://en.wikipedia.org/wiki/Zonal_and_meridional_flow.
    """
    return field - zonal_mean(field)[..., None]


# ----- errors ----------------------------------------------------------
# Pointwise errors operate on aligned (pred, truth) and broadcast over
# leading batch / channel dims.


def signed_error(pred: ArrayLike, truth: ArrayLike) -> ArrayLike:
    """
    Pointwise signed prediction error, `pred - truth`. Positive where the
    model overshoots, negative where it undershoots. Its mean over the
    domain is the prediction bias.

    Backend-agnostic via the subtraction operator.

    See https://en.wikipedia.org/wiki/Approximation_error.
    """
    return pred - truth


def absolute_error(pred: ArrayLike, truth: ArrayLike) -> ArrayLike:
    """
    Pointwise absolute prediction error, `|pred - truth|`. Drops the sign
    so reductions reflect magnitude only.

    Backend-agnostic via Python's `abs()` builtin, which delegates to
    `__abs__` on either numpy arrays or torch tensors.

    See https://en.wikipedia.org/wiki/Approximation_error.
    """
    return abs(pred - truth)


def relative_error(
    pred: np.ndarray, truth: np.ndarray, eps: float = 1e-12
) -> np.ndarray:
    """
    Pointwise relative error, `|pred - truth| / (|truth| + eps)`.

    Distinct from relative L2: this is per-pixel, not per-sample. It
    answers "by what fraction does the prediction miss the truth at
    each grid point". Sensitive to small truth values; eps avoids
    division blowup.

    See https://en.wikipedia.org/wiki/Approximation_error.
    """
    return np.abs(pred - truth) / (np.abs(truth) + eps)


def rms_error(pred: np.ndarray, truth: np.ndarray) -> float:
    """
    Root-mean-square error: `sqrt(mean((pred - truth)**2))` over every
    element. Standard scalar summary of prediction error magnitude.

    See https://en.wikipedia.org/wiki/Root_mean_square.
    """
    return float(np.sqrt(np.mean((pred - truth) ** 2)))


def relative_l2(pred: np.ndarray, truth: np.ndarray, eps: float = 1e-12) -> float:
    """
    Relative L2 error per sample:
    `||pred - truth||_2 / (||truth||_2 + eps)`, treating the input as a
    single flattened vector.

    Scale-invariant version of L2. Compared to RMS, it normalizes by the
    truth magnitude, which makes it comparable across simulations with
    different vorticity amplitudes.

    See https://en.wikipedia.org/wiki/Lp_space.
    """
    num = np.linalg.norm(pred - truth)
    den = np.linalg.norm(truth)
    return float(num / (den + eps))


def lat_weighted_relative_l2(
    pred: np.ndarray,
    truth: np.ndarray,
    latitudes_deg: np.ndarray,
    eps: float = 1e-12,
) -> float:
    """
    Cos-lat-weighted relative L2 error (single sample, scalar): same as
    `relative_l2`, but each spatial squared term is multiplied by
    `cos(lat)` area weights. Removes the polar over-weighting bias of
    unweighted L2 on a lat-lon grid.

    Args:
        pred, truth:   (..., H, W) arrays.
        latitudes_deg: 1D array of length H.

    See https://en.wikipedia.org/wiki/Lp_space.
    """
    w = cosine_latitude_weights(latitudes_deg)
    err2 = ((pred - truth) ** 2) * w[:, None]
    sig2 = (truth**2) * w[:, None]
    num = float(np.sqrt(err2.sum()))
    den = float(np.sqrt(sig2.sum()))
    return num / (den + eps)


def lat_weighted_relative_l2_torch(
    pred: torch.Tensor,
    truth: torch.Tensor,
    lat_weights: torch.Tensor,
) -> torch.Tensor:
    """
    Cos-lat-weighted relative L2 error in batched torch form, used as a
    training loss. Computes per-(batch, channel) relative L2 with
    cos-lat area weights, then averages over the batch and channel dims
    so the output is a single scalar.

    Distinct from `lat_weighted_relative_l2` (numpy, single-sample): the
    torch version is batched and reduces to a scalar suitable for
    backpropagation.

    Args:
        pred, truth: (B, C, H, W) tensors.
        lat_weights: (H,) tensor on the same device as pred / truth, with
                     mean 1 normalization (use
                     `cosine_latitude_weights_torch(..., "mean1")`).

    Returns: scalar tensor.

    See https://en.wikipedia.org/wiki/Lp_space.
    """
    wb = lat_weights.view(1, 1, -1, 1)
    num = ((pred - truth).pow(2) * wb).sum(dim=(-2, -1)).sqrt()
    den = (truth.pow(2) * wb).sum(dim=(-2, -1)).sqrt()
    return (num / den).mean()


# ----- spectra ---------------------------------------------------------


def zonal_power_spectrum(field: np.ndarray) -> np.ndarray:
    """
    Power spectrum along the longitude (last) axis: `|rfft(field)|**2`.

    Why it is meaningful: it shows how the field's energy distributes
    across zonal wavenumbers (large-scale features at low k, fine-scale
    eddies at high k). The shape of this spectrum is a defining
    statistical property of geophysical turbulence.

    See https://en.wikipedia.org/wiki/Spectral_density.

    Args:    field of shape (..., H, W).
    Returns: array of shape (..., H, W//2 + 1).
    """
    return np.abs(np.fft.rfft(field, axis=-1)) ** 2


def zonal_power_spectrum_torch(field: torch.Tensor) -> torch.Tensor:
    """
    Torch counterpart of `zonal_power_spectrum`, used by the per-epoch
    metrics writer. Numerical semantics identical.

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


# ----- physical invariants ---------------------------------------------


def enstrophy_density(vor: ArrayLike) -> ArrayLike:
    """
    Pointwise enstrophy density, `0.5 * vor**2`. No spatial reduction.

    Why it is meaningful: enstrophy is a quadratic conserved quantity in
    inviscid 2D flow and a key budget term in barotropic dynamics. The
    map of `0.5 * vor**2` shows where small-scale vorticity is
    concentrated.

    Backend-agnostic via the `**` operator and scalar multiplication.

    See https://en.wikipedia.org/wiki/Enstrophy.
    """
    return 0.5 * vor**2


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


# ----- baselines -------------------------------------------------------


def persistence_prediction(x: ArrayLike, vor_t_channel: int) -> ArrayLike:
    """
    Persistence baseline: predict next-step vorticity to be equal to the
    current vorticity. Returns the slice
    `x[:, vor_t_channel : vor_t_channel + 1, :, :]`.

    For a lag-stacked input layout (channels are
    [vor_{t-K+1}, stirring_{t-K+1}, ..., vor_t, stirring_t]), the caller
    supplies the index of the most-recent vor channel, typically
    `(K - 1) * len(x_vars) + x_vars.index("vor")`.

    Why it is meaningful: any model that fails to beat persistence is
    not learning useful dynamics. It is the simplest reference baseline
    in time-series forecasting.

    Backend-agnostic via array slicing, which behaves identically on
    numpy and torch.

    See https://en.wikipedia.org/wiki/Persistence_forecasting.
    """
    return x[:, vor_t_channel : vor_t_channel + 1, :, :]


# Re-export convergence diagnostics. Imported at the bottom of the file
# because ml.diagnostics.convergence depends on names defined above
# (mean_enstrophy, zonal_mean).
from ml.diagnostics.convergence import (  # noqa: E402
    compute_enstrophy,
    compute_time_mean_zonal_mean,
    find_spinup_time,
)
