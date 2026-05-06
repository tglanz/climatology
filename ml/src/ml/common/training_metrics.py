import csv
from datetime import datetime
from pathlib import Path

import h5py
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from neuralop.data.transforms.normalizers import UnitGaussianNormalizer

from ml.config import PathsConfig


_EPOCH_HEADER = ["run_id", "epoch", "timestamp", "elapsed_seconds", "learning_rate", "train_loss", "val_loss"]
_RUNS_HEADER  = ["run_id", "start_time", "end_time", "total_epochs", "best_val_loss", "best_val_epoch", "stopped_early"]


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
        self._runs_path = paths.runs_file
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

    def log_run(
        self,
        run_id: str,
        start_time: datetime,
        end_time: datetime,
        total_epochs: int,
        best_val_loss: float,
        best_val_epoch: int,
        stopped_early: bool,
    ) -> None:
        _append_csv(self._runs_path, _RUNS_HEADER, [
            run_id,
            start_time.isoformat(),
            end_time.isoformat(),
            total_epochs,
            f"{best_val_loss:.6f}" if best_val_loss < float("inf") else "",
            best_val_epoch if best_val_epoch > 0 else "",
            stopped_early,
        ])

    def update(self, model: nn.Module, val_loader: DataLoader) -> None:
        model.eval()
        spatial_acc: torch.Tensor | None = None
        power_acc: torch.Tensor | None = None
        n_samples = 0

        target_power_acc: torch.Tensor | None = None

        with torch.no_grad():
            for x, y in val_loader:
                x = x.to(self._device)
                y = y.to(self._device)
                pred = self._normalizer_y.inverse_transform(
                    model(self._normalizer_x.transform(x))
                )
                error  = (pred - y).squeeze(1)          # (B, H, W)
                target = y.squeeze(1)                   # (B, H, W)

                spatial_acc = error.abs().sum(0) if spatial_acc is None else spatial_acc + error.abs().sum(0)

                error_power  = torch.fft.rfft(error,  dim=-1).abs().pow(2).sum(dim=(0, 1))  # (W//2+1,)
                target_power = torch.fft.rfft(target, dim=-1).abs().pow(2).sum(dim=(0, 1))

                power_acc        = error_power  if power_acc        is None else power_acc        + error_power
                target_power_acc = target_power if target_power_acc is None else target_power_acc + target_power

                n_samples += x.shape[0]

        assert spatial_acc is not None and n_samples > 0
        H = spatial_acc.shape[0]
        denom = n_samples * H

        spatial_error = (spatial_acc / n_samples).cpu().numpy().astype(np.float32)
        tmp = self._metrics_path.with_suffix(".tmp.h5")
        with h5py.File(tmp, "w") as f:
            f.create_dataset("spatial_error",      data=spatial_error)
            f.create_dataset("zonal_mean_error",   data=spatial_error.mean(axis=1))
            f.create_dataset("error_power",        data=(power_acc        / (n_samples * H)).cpu().numpy().astype(np.float32))
            f.create_dataset("signal_power",       data=(target_power_acc / (n_samples * H)).cpu().numpy().astype(np.float32))
        # atomic rename so the monitor never reads a partially-written file
        tmp.replace(self._metrics_path)
