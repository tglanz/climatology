"""Checkpoint loading and batched climatology prediction.

Loaded-model normalization intentionally retains the pre-compaction arithmetic.
Training's normalization epsilon is reconciled in action item 02.
"""

from pathlib import Path
import numpy as np
import torch
from ml.training.model import build_model


def load_model(cfg, training_dir: Path, dropout=None):
    model = build_model(cfg.model, dropout=dropout)
    params_path = training_dir / "parameters.pt"
    assert params_path.exists(), f"model parameters not found: {params_path}"
    state = torch.load(params_path, map_location="cpu", weights_only=False)
    state.pop("_metadata", None)
    model.load_state_dict(state)
    model.eval()
    return model


def select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def prepare_device(model, x_shape: tuple, device: torch.device):
    if device.type != "cpu":
        model.cpu()
        with torch.no_grad():
            model(torch.zeros(1, *x_shape))
        for m in model.modules():
            if hasattr(m, "_grid"):
                m._grid = None
    model.to(device)
    return model


def predict_windows(
    model,
    norm: dict,
    x_windows: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> np.ndarray:
    x_mean = norm["x_mean"].to(device)
    x_std = norm["x_std"].to(device)
    y_mean = norm["y_mean"].to(device)
    y_std = norm["y_std"].to(device)

    x_tensor = torch.from_numpy(x_windows)
    preds = []
    with torch.no_grad():
        for i in range(0, len(x_tensor), batch_size):
            xb = x_tensor[i : i + batch_size].to(device)
            xb_norm = (xb - x_mean) / x_std
            yb_norm = model(xb_norm)
            yb = yb_norm * y_std + y_mean
            preds.append(yb.squeeze(1).cpu().numpy())
    preds_all = np.concatenate(preds, axis=0)
    return preds_all
