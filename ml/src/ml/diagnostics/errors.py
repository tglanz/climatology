"""
See
- https://en.wikipedia.org/wiki/Approximation_error
"""
from typing import Union
import numpy as np
import torch

from ml.diagnostics.spatial import cosine_latitude_weights

def signed_error(pred: Union[np.ndarray, torch.Tensor], truth: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
    return pred - truth


def absolute_error(pred: Union[np.ndarray, torch.Tensor], truth: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
    return abs(pred - truth)


def relative_error(
    pred: np.ndarray, truth: np.ndarray, eps: float = 1e-12
) -> np.ndarray:
    # +eps to avoid division issues
    return np.abs(pred - truth) / (np.abs(truth) + eps)


def rms_error(pred: np.ndarray, truth: np.ndarray) -> float:
    """ https://en.wikipedia.org/wiki/Root_mean_square """
    return float(np.sqrt(np.mean((pred - truth) ** 2)))

def relative_l2(pred: np.ndarray, truth: np.ndarray, eps: float = 1e-12) -> float:
    num = np.linalg.norm(pred - truth)
    den = np.linalg.norm(truth)
    return float(num / (den + eps))


def lat_weighted_relative_l2(
    pred: np.ndarray,
    truth: np.ndarray,
    latitudes_deg: np.ndarray,
    eps: float = 1e-12,
) -> float:
    w = cosine_latitude_weights(latitudes_deg)
    err2 = ((pred - truth) ** 2) * w[:, None]
    sig2 = (truth**2) * w[:, None]
    num = float(np.sqrt(err2.sum()))
    den = float(np.sqrt(sig2.sum()))
    return num / (den + eps)
