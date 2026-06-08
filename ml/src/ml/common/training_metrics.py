import csv
from pathlib import Path

import h5py
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from neuralop.data.transforms.normalizers import UnitGaussianNormalizer

from ml.config import PathsConfig

from ml.diagnostics import (
    absolute_error,
    zonal_mean,
    zonal_power_spectrum_torch,
)


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
        artifacts to metrics.h5.

        Step mode (y ndim=4):
          - spatial_error:    mean absolute error map              (H, W)
          - zonal_mean_error: spatial_error averaged over lon      (H,)
          - error_power:      mean residual zonal power spectrum   (W//2+1,)
          - signal_power:     mean target  zonal power spectrum    (W//2+1,)

        Climatology mode (y ndim=3):
          - spatial_error:    mean absolute error per latitude     (H,)
          - profile_pred:     mean predicted u(lat) profile        (H,)
          - profile_truth:    mean true      u(lat) profile        (H,)
        """
        model.eval()
        spatial_acc: torch.Tensor | None = None
        power_acc: torch.Tensor | None = None
        target_power_acc: torch.Tensor | None = None
        pred_acc: torch.Tensor | None = None
        truth_acc: torch.Tensor | None = None
        is_clim: bool | None = None
        n_samples = 0

        with torch.no_grad():
            for x, y in val_loader:
                x = x.to(self._device)
                y = y.to(self._device)
                pred = self._normalizer_y.inverse_transform(
                    model(self._normalizer_x.transform(x))
                )

                # Drop the channel dim; downstream reductions assume (B, H) or (B, H, W).
                pred_b = pred.squeeze(1)
                truth_b = y.squeeze(1)

                is_clim = y.ndim == 3

                err_abs = absolute_error(pred_b, truth_b).sum(0)
                spatial_acc = err_abs if spatial_acc is None else spatial_acc + err_abs

                if is_clim:
                    pred_acc  = pred_b.sum(0)  if pred_acc  is None else pred_acc  + pred_b.sum(0)
                    truth_acc = truth_b.sum(0) if truth_acc is None else truth_acc + truth_b.sum(0)
                else:
                    error_power  = zonal_power_spectrum_torch(pred_b - truth_b).sum(dim=(0, 1))
                    target_power = zonal_power_spectrum_torch(truth_b).sum(dim=(0, 1))
                    power_acc        = error_power  if power_acc        is None else power_acc        + error_power
                    target_power_acc = target_power if target_power_acc is None else target_power_acc + target_power

                n_samples += x.shape[0]

        assert spatial_acc is not None and n_samples > 0
        H = spatial_acc.shape[0]

        spatial_error = (spatial_acc / n_samples).cpu().numpy().astype(np.float32)
        tmp = self._metrics_path.with_suffix(".tmp.h5")
        with h5py.File(tmp, "w") as f:
            f.create_dataset("spatial_error", data=spatial_error)
            if is_clim:
                f.create_dataset("profile_pred",  data=(pred_acc  / n_samples).cpu().numpy().astype(np.float32))
                f.create_dataset("profile_truth", data=(truth_acc / n_samples).cpu().numpy().astype(np.float32))
            else:
                f.create_dataset("zonal_mean_error", data=zonal_mean(spatial_error).astype(np.float32))
                f.create_dataset("error_power",      data=(power_acc        / (n_samples * H)).cpu().numpy().astype(np.float32))
                f.create_dataset("signal_power",     data=(target_power_acc / (n_samples * H)).cpu().numpy().astype(np.float32))
        # atomic rename so the monitor never reads a partially-written file
        tmp.replace(self._metrics_path)
