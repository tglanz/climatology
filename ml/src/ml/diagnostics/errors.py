"""Error metrics with explicit shapes and undefined relative-error handling."""

from dataclasses import dataclass
from typing import Union
import numpy as np
import torch

from ml.diagnostics.grid import gaussian_latitude_weights


@dataclass(frozen=True)
class ScoreSummary:
    mean: float | None
    count: int
    undefined: int

    @classmethod
    def from_values(cls, values) -> "ScoreSummary":
        values = np.asarray(values, dtype=np.float64)
        if np.isinf(values).any():
            raise ValueError("scores contain infinite values")
        valid = np.isfinite(values)
        return cls(
            float(values[valid].mean()) if valid.any() else None,
            int(valid.sum()),
            int((~valid).sum()),
        )


def signed_error(
    pred: Union[np.ndarray, torch.Tensor], truth: Union[np.ndarray, torch.Tensor]
) -> Union[np.ndarray, torch.Tensor]:
    return pred - truth


def absolute_error(
    pred: Union[np.ndarray, torch.Tensor], truth: Union[np.ndarray, torch.Tensor]
) -> Union[np.ndarray, torch.Tensor]:
    return abs(pred - truth)


def relative_error(
    pred: np.ndarray, truth: np.ndarray, eps: float = 1e-12
) -> np.ndarray:
    return np.abs(pred - truth) / (np.abs(truth) + eps)


def _matching_arrays(pred, truth) -> tuple[np.ndarray, np.ndarray]:
    p, y = np.asarray(pred, dtype=np.float64), np.asarray(truth, dtype=np.float64)
    if p.shape != y.shape or p.ndim < 1:
        raise ValueError("prediction and truth must have the same non-scalar shape")
    if not np.isfinite(p).all() or not np.isfinite(y).all():
        raise ValueError("prediction and truth must be finite")
    return p, y


def rms_error(pred: np.ndarray, truth: np.ndarray) -> float:
    pred, truth = _matching_arrays(pred, truth)
    return float(np.sqrt(np.mean((pred - truth) ** 2)))


def relative_l2(pred: np.ndarray, truth: np.ndarray) -> float:
    pred, truth = _matching_arrays(pred, truth)
    den = np.linalg.norm(truth)
    return float(np.linalg.norm(pred - truth) / den) if den > 0 else float("nan")


def profile_relative_l2_values(
    pred: np.ndarray, truth: np.ndarray, latitudes: np.ndarray
) -> np.ndarray:
    """Return one ratio per leading index of matching (..., latitude) arrays."""
    pred, truth = _matching_arrays(pred, truth)
    weights = gaussian_latitude_weights(latitudes)
    if pred.shape[-1] != len(weights):
        raise ValueError("profile shape must end in latitude")
    num = np.sqrt(np.sum(weights * (pred - truth) ** 2, axis=-1))
    den = np.sqrt(np.sum(weights * truth**2, axis=-1))
    return np.divide(num, den, out=np.full_like(num, np.nan), where=den > 0)


def lat_weighted_relative_l2(
    pred: np.ndarray, truth: np.ndarray, latitudes_deg: np.ndarray
) -> float:
    values = profile_relative_l2_values(pred, truth, latitudes_deg)
    summary = ScoreSummary.from_values(values)
    return float("nan") if summary.mean is None else summary.mean


def lat_weighted_relative_l2_torch(
    pred: torch.Tensor, truth: torch.Tensor, lat_weights: torch.Tensor
) -> torch.Tensor:
    """Mean of per-sample, per-target ratios for profiles or spatial fields."""
    if pred.shape != truth.shape or pred.ndim not in (3, 4):
        raise ValueError(
            "loss shapes must match (batch, target, latitude[, longitude])"
        )
    if lat_weights.ndim != 1 or len(lat_weights) != pred.shape[2]:
        raise ValueError("latitude weights do not match the loss shape")
    if not torch.isfinite(pred).all() or not torch.isfinite(truth).all():
        raise ValueError("relative loss requires finite predictions and targets")
    if not torch.isfinite(lat_weights).all() or (lat_weights <= 0).any():
        raise ValueError("latitude weights must be finite and positive")
    weights = lat_weights.to(device=pred.device, dtype=pred.dtype)
    weights = weights / weights.sum()
    shape = (1, 1, -1, 1) if pred.ndim == 4 else (1, 1, -1)
    root_weight = weights.view(shape).sqrt()
    dims = (-2, -1) if pred.ndim == 4 else (-1,)
    # vector_norm defines a zero subgradient at zero error; sqrt(sum(e**2)) does not.
    num = ((pred - truth) * root_weight).norm(dim=dims)
    den = (truth * root_weight).norm(dim=dims)
    if (den == 0).any():
        raise ValueError(
            "relative loss has a zero target norm; use MSE or change the targets"
        )
    return (num / den).mean()


def profile_rel_l2(pred: np.ndarray, truth: np.ndarray, lat: np.ndarray) -> float:
    if np.ndim(pred) != 1 or np.ndim(truth) != 1:
        raise ValueError("profile shapes must both be (latitude,)")
    return float(profile_relative_l2_values(pred, truth, lat))


def profile_rmse(pred: np.ndarray, truth: np.ndarray, lat: np.ndarray) -> float:
    pred, truth = _matching_arrays(pred, truth)
    weights = gaussian_latitude_weights(lat)
    if pred.ndim != 1 or pred.shape != weights.shape:
        raise ValueError("profile shapes must both be (latitude,)")
    return float(np.sqrt(np.sum(weights * (pred - truth) ** 2)))


def notebook_profile_rel_l2(
    pred: np.ndarray, truth: np.ndarray, lat: np.ndarray
) -> float:
    """Retained notebook API using the shared metric contract."""
    return profile_rel_l2(pred, truth, lat)
