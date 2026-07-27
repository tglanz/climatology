import csv
from pathlib import Path

import h5py
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from neuralop.data.transforms.normalizers import UnitGaussianNormalizer

from ml.config import PathsConfig

from ml.diagnostics import absolute_error


_EPOCH_HEADER = ["run_id", "epoch", "timestamp", "elapsed_seconds", "learning_rate", "train_loss", "val_loss"]


def _append_csv(path: Path, header: list, row: list) -> None:
    write_header = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        w.writerow(row)


class TrainingMetrics:
    def __init__(
        self,
        paths: PathsConfig,
        normalizer_x: UnitGaussianNormalizer,
        normalizer_y: UnitGaussianNormalizer,
        device: torch.device,
    ):
        paths.training_dir.mkdir(parents=True, exist_ok=True)
        self._epoch_metrics_path = paths.epoch_metrics_file
        self._metrics_path = paths.metrics_file
        self._normalizer_x = normalizer_x
        self._normalizer_y = normalizer_y
        self._device = device

    def log_epoch(
        self,
        run_id: str,
        epoch: int,
        timestamp: str,
        elapsed: float,
        lr: float,
        train_loss: float,
        val_loss: float | None,
    ) -> None:
        _append_csv(self._epoch_metrics_path, _EPOCH_HEADER, [
            run_id, epoch, timestamp, f"{elapsed:.3f}", f"{lr:.2e}",
            f"{train_loss:.6f}", f"{val_loss:.6f}" if val_loss is not None else "",
        ])

    def update(self, model: nn.Module, val_loader: DataLoader) -> None:
        """
        Run the model on the val loader and write per-epoch diagnostic
        artifacts to metrics.h5:
          - spatial_error:    mean absolute error per latitude     (H,)
          - profile_pred:     mean predicted u(lat) profile        (H,)
          - profile_pred_std: std of predicted profile             (H,)
          - profile_truth:    mean true u(lat) profile             (H,)
        """
        model.eval()
        spatial_acc: torch.Tensor | None = None
        pred_acc: torch.Tensor | None = None
        pred_sq_acc: torch.Tensor | None = None
        truth_acc: torch.Tensor | None = None
        n_samples = 0

        with torch.no_grad():
            for x, y in val_loader:
                x = x.to(self._device)
                y = y.to(self._device)
                pred = self._normalizer_y.inverse_transform(
                    model(self._normalizer_x.transform(x))
                )

                pred_b = pred.squeeze(1)
                truth_b = y.squeeze(1)

                err_abs = absolute_error(pred_b, truth_b).sum(0)
                spatial_acc = err_abs if spatial_acc is None else spatial_acc + err_abs
                pred_acc    = pred_b.sum(0)        if pred_acc    is None else pred_acc    + pred_b.sum(0)
                pred_sq_acc = pred_b.pow(2).sum(0) if pred_sq_acc is None else pred_sq_acc + pred_b.pow(2).sum(0)
                truth_acc   = truth_b.sum(0)       if truth_acc   is None else truth_acc   + truth_b.sum(0)
                n_samples += x.shape[0]

        assert spatial_acc is not None and n_samples > 0

        spatial_error = (spatial_acc / n_samples).cpu().numpy().astype(np.float32)
        pred_mean = pred_acc / n_samples
        pred_std = (pred_sq_acc / n_samples - pred_mean.pow(2)).clamp(min=0).sqrt()

        tmp = self._metrics_path.with_suffix(".tmp.h5")
        with h5py.File(tmp, "w") as f:
            f.create_dataset("spatial_error",    data=spatial_error)
            f.create_dataset("profile_pred",     data=pred_mean.cpu().numpy().astype(np.float32))
            f.create_dataset("profile_pred_std", data=pred_std.cpu().numpy().astype(np.float32))
            f.create_dataset("profile_truth",    data=(truth_acc / n_samples).cpu().numpy().astype(np.float32))
        # atomic rename so the monitor never reads a partially-written file
        tmp.replace(self._metrics_path)
