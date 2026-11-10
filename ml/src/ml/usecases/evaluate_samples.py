"""Prepared-test-set evaluation, retaining the original notebook conventions."""

from pathlib import Path
import h5py
import numpy as np
import torch
from ml import patches
from ml.config import load
from ml.inference import load_model, select_device, prepare_device, predict_windows
from ml.diagnostics.errors import notebook_profile_rel_l2, profile_rmse


def run(training_dir: Path, batch_size: int = 64, limit: int | None = None):
    training_dir = training_dir.resolve()
    cfg = load(training_dir / "config.toml")
    data_dir = training_dir.parent / "data"
    model = load_model(cfg, training_dir, dropout=cfg.training.regularization.dropout)
    norm = torch.load(
        training_dir / "normalization.pt", map_location="cpu", weights_only=True
    )
    with h5py.File(data_dir / "test.h5", "r") as f:
        x = f["x"][:limit]
        truth = f["y"][:limit].squeeze(1)
    device = select_device()
    patches.apply()
    prepare_device(model, x.shape[1:], device)
    predictions = predict_windows(model, norm, x, device, batch_size)
    # This notebook historically uses synthetic equiangular plotting coordinates.
    # Actual-grid reconciliation belongs to action item 02.
    lat = np.linspace(-90, 90, truth.shape[1])
    rmses = np.array([profile_rmse(p, t, lat) for p, t in zip(predictions, truth)])
    rels = np.array(
        [notebook_profile_rel_l2(p, t, lat) for p, t in zip(predictions, truth)]
    )
    return predictions, truth, lat, rmses, rels


def print_metrics(rmses, rels):
    print(
        f"{'metric':<10} {'mean':>10} {'median':>10} {'p75':>10} {'p95':>10} {'max':>10}"
    )
    print("-" * 60)
    for name, vals in [("rmse", rmses), ("relL2", rels)]:
        print(
            f"{name:<10} {vals.mean():>10.4f} {np.median(vals):>10.4f}"
            f" {np.percentile(vals, 75):>10.4f} {np.percentile(vals, 95):>10.4f} {vals.max():>10.4f}"
        )
