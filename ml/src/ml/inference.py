"""Versioned checkpoint loading and physical-unit predictions for all targets."""

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import torch

from ml.training.model import build_model
from ml.training.normalization import Normalization


@dataclass
class Checkpoint:
    model: torch.nn.Module
    normalization: Normalization


def load_checkpoint(cfg, training_dir: Path, dropout=None) -> Checkpoint:
    norm = Normalization.from_dict(
        torch.load(
            training_dir / "normalization.pt", map_location="cpu", weights_only=True
        )
    )
    norm.metadata.validate_config(cfg.data)
    dropout = cfg.training.regularization.dropout if dropout is None else dropout
    model = build_model(cfg.model, norm.metadata.grid, dropout=dropout)
    state = torch.load(
        training_dir / "parameters.pt", map_location="cpu", weights_only=True
    )
    state.pop("_metadata", None)
    model.load_state_dict(state)
    model.eval()
    return Checkpoint(model, norm)


def load_model(cfg, training_dir: Path, dropout=None):
    return load_checkpoint(cfg, training_dir, dropout).model


def select_device(requested: str = "auto") -> torch.device:
    if requested not in ("auto", "cpu", "cuda", "mps"):
        raise ValueError(f"unknown device: {requested}")
    if requested != "auto":
        if requested == "cuda" and not torch.cuda.is_available():
            raise ValueError("CUDA is unavailable")
        if requested == "mps" and not torch.backends.mps.is_available():
            raise ValueError("MPS is unavailable")
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def prepare_device(model, x_shape: tuple, device: torch.device):
    if tuple(x_shape[-2:]) != model.grid.shape:
        raise ValueError("prediction grid differs from the checkpoint")
    if device.type != "cpu":
        model.cpu()
        with torch.no_grad():
            model(torch.zeros(1, *x_shape))
    return model.to(device)


def predict_windows(
    model,
    norm: Normalization | dict,
    x_windows: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> np.ndarray:
    if batch_size < 1:
        raise ValueError("prediction batch size must be positive")
    normalization = Normalization.from_dict(norm) if isinstance(norm, dict) else norm
    metadata = normalization.metadata
    values = np.asarray(x_windows)
    if values.ndim != 4 or values.shape[1:] != (
        metadata.input_channels,
        *metadata.grid.shape,
    ):
        raise ValueError("prediction input shape differs from saved metadata")
    if not np.isfinite(values).all():
        raise ValueError("prediction input contains nonfinite values")
    if not model.grid.matches(metadata.grid):
        raise ValueError("prediction coordinates differ from the checkpoint")
    if len(values) == 0:
        return np.empty(
            (0, len(metadata.y_vars), metadata.grid.shape[0]), dtype=np.float32
        )
    normalization.to(device)
    model.eval()
    preds = []
    with torch.no_grad():
        for start in range(0, len(values), batch_size):
            xb = torch.as_tensor(
                values[start : start + batch_size], dtype=torch.float32, device=device
            )
            pred = normalization.y.inverse_transform(
                model(normalization.x.transform(xb))
            )
            if not torch.isfinite(pred).all():
                raise ValueError("model produced nonfinite predictions")
            preds.append(pred.cpu().numpy())
    return np.concatenate(preds, axis=0)
