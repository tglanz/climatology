import logging
import time
from datetime import datetime, timezone
from typing import Callable

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from neuralop.data.transforms.normalizers import UnitGaussianNormalizer

from ml.config import Config
from ml.common.training_metrics import TrainingMetrics


def create_loss_fn(kind: str) -> Callable[[torch.Tensor, torch.Tensor], torch.Tensor]:
    if kind == "mse":
        return nn.MSELoss()
    if kind == "relative_l2":

        def relative_l2(pred, target):
            return torch.mean(
                torch.norm(pred - target, dim=(-2, -1))
                / torch.norm(target, dim=(-2, -1))
            )

        return relative_l2
    raise ValueError(f"unknown loss: {kind}")


class Trainer:
    def __init__(self, model: nn.Module, cfg: Config):
        self.cfg = cfg
        self.log = logging.getLogger(__name__)
        self.run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        cfg.paths.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
        self.log.info("device: %s", self.device)

        self.model = model.to(self.device)
        self.loss_fn = create_loss_fn(cfg.training.loss)

        if cfg.training.optimizer == "adam":
            self.optimizer = torch.optim.Adam(model.parameters(), lr=cfg.training.learning_rate)
        elif cfg.training.optimizer == "adamw":
            self.optimizer = torch.optim.AdamW(
                model.parameters(),
                lr=cfg.training.learning_rate,
                weight_decay=cfg.training.weight_decay,
            )
        else:
            raise ValueError(f"unknown optimizer: {cfg.training.optimizer}")

        self.scheduler = torch.optim.lr_scheduler.StepLR(
            self.optimizer,
            step_size=cfg.training.lr_decay_every,
            gamma=cfg.training.lr_decay_factor,
        )

    def _fit_normalizers(self, train_loader: DataLoader):
        normalizer_x = UnitGaussianNormalizer(dim=[0, 2, 3])
        normalizer_y = UnitGaussianNormalizer(dim=[0, 2, 3])
        batch_size = train_loader.batch_size
        for x, y in tqdm(train_loader, desc="fit normalizers", leave=False):
            normalizer_x.partial_fit(x, batch_size=batch_size)
            normalizer_y.partial_fit(y, batch_size=batch_size)
        self.normalizer_x = normalizer_x.to(self.device)
        self.normalizer_y = normalizer_y.to(self.device)
        self.log.info(
            "normalizer_x mean=%s std=%s",
            normalizer_x.mean.squeeze().tolist(),
            normalizer_x.std.squeeze().tolist(),
        )
        self.log.info(
            "normalizer_y mean=%s std=%s",
            normalizer_y.mean.squeeze().tolist(),
            normalizer_y.std.squeeze().tolist(),
        )

    def fit(self, train_loader: DataLoader, val_loader: DataLoader | None, track_metrics: bool = False):
        self._fit_normalizers(train_loader)
        training_metrics = (
            TrainingMetrics(self.cfg.paths, self.normalizer_x, self.normalizer_y, self.device)
            if track_metrics
            else None
        )

        best_val = float("inf")
        best_val_epoch = -1
        target_loss = self.cfg.training.target_loss
        stopped_early = False
        start_time = datetime.now(timezone.utc)

        for epoch in tqdm(range(1, self.cfg.training.epochs + 1), desc="epochs"):
            t0 = time.monotonic()
            train_loss = self.train_epoch(train_loader)
            self.scheduler.step()
            lr = self.scheduler.get_last_lr()[0]

            if val_loader is not None:
                val_loss = self.evaluate(val_loader)
                self.log.info("epoch %d  train=%.6f  val=%.6f", epoch, train_loss, val_loss)
                if val_loss < best_val:
                    best_val = val_loss
                    best_val_epoch = epoch
                    torch.save(self.model.state_dict(), self.cfg.paths.checkpoint_dir / "best.pt")
                monitored = val_loss
                if training_metrics is not None:
                    training_metrics.update(self.model, val_loader)
            else:
                val_loss = None
                self.log.info("epoch %d  train=%.6f", epoch, train_loss)
                torch.save(self.model.state_dict(), self.cfg.paths.checkpoint_dir / "best.pt")
                monitored = train_loss

            if training_metrics is not None:
                training_metrics.log_epoch(
                    self.run_id, epoch,
                    datetime.now(timezone.utc).isoformat(),
                    time.monotonic() - t0, lr, train_loss, val_loss,
                )

            if target_loss is not None and monitored <= target_loss:
                self.log.info("target loss %.6f reached at epoch %d, stopping", target_loss, epoch)
                stopped_early = True
                break

        if training_metrics is not None:
            training_metrics.log_run(
                self.run_id, start_time, datetime.now(timezone.utc),
                epoch, best_val, best_val_epoch, stopped_early,
            )

    def train_epoch(self, loader: DataLoader) -> float:
        self.model.train()
        total = 0.0
        for x, y in tqdm(loader, desc="train", leave=False):
            x, y = x.to(self.device), y.to(self.device)
            x = self.normalizer_x.transform(x)
            y = self.normalizer_y.transform(y)
            loss = self.loss_fn(self.model(x), y)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            total += loss.item()
        return total / len(loader)

    def evaluate(self, loader: DataLoader) -> float:
        self.model.eval()
        total = 0.0
        with torch.no_grad():
            for x, y in tqdm(loader, desc="val", leave=False):
                x, y = x.to(self.device), y.to(self.device)
                x = self.normalizer_x.transform(x)
                y = self.normalizer_y.transform(y)
                total += self.loss_fn(self.model(x), y).item()
        return total / len(loader)
