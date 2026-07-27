import logging
import time
from datetime import datetime, timezone

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from neuralop.data.transforms.normalizers import UnitGaussianNormalizer

from ml.config import Config, SchedulerConfig
from ml.common.training_metrics import TrainingMetrics
from ml.training.early_stopping import CompositeEarlyStopper, EarlyStoppingInfo
from ml.training.loss import LossFn, create_loss_fn
from ml.training.info import TrainingInfo


def build_scheduler(
    optimizer: torch.optim.Optimizer, cfg: SchedulerConfig, total_epochs: int
):
    if cfg.kind == "none":
        return None, "none"
    if cfg.kind == "step":
        sch = torch.optim.lr_scheduler.StepLR(
            optimizer, step_size=cfg.step.step_size, gamma=cfg.step.gamma
        )
        return sch, "epoch"
    if cfg.kind == "cosine":
        t_max = cfg.cosine.t_max if cfg.cosine.t_max is not None else total_epochs
        sch = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=t_max, eta_min=cfg.cosine.eta_min
        )
        return sch, "epoch"
    if cfg.kind == "plateau":
        sch = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode="min",
            factor=cfg.plateau.factor,
            patience=cfg.plateau.patience,
            threshold=cfg.plateau.threshold,
            min_lr=cfg.plateau.eta_min,
        )
        return sch, "plateau"
    raise ValueError(f"unknown scheduler kind: {cfg.kind}")


class Trainer:
    def __init__(self, model: nn.Module, cfg: Config, lat_weights: torch.Tensor | None = None):
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
        self.loss_fn = create_loss_fn(cfg.training.loss, lat_weights=lat_weights)
        self.log.info("loss: %s", cfg.training.loss)

        wd = cfg.training.regularization.weight_decay
        if cfg.training.optimizer == "adam":
            if wd is not None and wd != 0.0:
                self.log.warning(
                    "regularization.weight_decay=%s is ignored when optimizer='adam'; "
                    "switch optimizer to 'adamw' to apply it",
                    wd,
                )
            self.optimizer = torch.optim.Adam(
                model.parameters(), lr=cfg.training.learning_rate
            )
        elif cfg.training.optimizer == "adamw":
            self.optimizer = torch.optim.AdamW(
                model.parameters(),
                lr=cfg.training.learning_rate,
                weight_decay=wd if wd is not None else 0.0,
            )
        else:
            raise ValueError(f"unknown optimizer: {cfg.training.optimizer}")

        self.scheduler, self.scheduler_mode = build_scheduler(
            self.optimizer, cfg.training.scheduler, cfg.training.epochs
        )
        self.log.info(
            "scheduler: %s (mode=%s)", cfg.training.scheduler.kind, self.scheduler_mode
        )

        self.early_stopper = CompositeEarlyStopper.from_config(
            cfg.training.early_stopping
        )
        if len(self.early_stopper) > 0:
            self.log.info(
                "early stopping: %s",
                ", ".join(type(s).__name__ for s in self.early_stopper),
            )
        else:
            self.log.info("early stopping: none")

        self.grad_clip = cfg.training.grad_clip

        self.info = TrainingInfo.collect(cfg, self.run_id, self.model, self.device)

    def _fit_normalizers(self, train_loader: DataLoader):
        normalizer_x = UnitGaussianNormalizer(dim=[0, 2, 3])
        normalizer_y = None

        batch_size = train_loader.batch_size
        for x, y in train_loader:
            if normalizer_y is None:
                normalizer_y = UnitGaussianNormalizer(dim=[0, 2])

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
        torch.save(
            {
                "x_mean": normalizer_x.mean.cpu(),
                "x_std": normalizer_x.std.cpu(),
                "y_mean": normalizer_y.mean.cpu(),
                "y_std": normalizer_y.std.cpu(),
            },
            self.cfg.paths.checkpoint_dir / "normalization.pt",
        )
        self.log.info(
            "saved normalization stats to %s",
            self.cfg.paths.checkpoint_dir / "normalization.pt",
        )

    def _step_scheduler(self, val_loss: float | None) -> None:
        if self.scheduler is None:
            return
        if self.scheduler_mode == "plateau":
            assert val_loss is not None, "plateau scheduler requires a validation loader"
            self.scheduler.step(val_loss)
        else:
            self.scheduler.step()

    def _current_lr(self) -> float:
        return self.optimizer.param_groups[0]["lr"]

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader | None,
        track_metrics: bool = False,
    ):
        self._fit_normalizers(train_loader)
        training_metrics = (
            TrainingMetrics(
                self.cfg.paths, self.normalizer_x, self.normalizer_y, self.device
            )
            if track_metrics
            else None
        )

        best_val = float("inf")
        best_val_epoch = -1
        stopped_early = False

        self.info.save(self.cfg.paths.training_info_file)
        self.log.info("wrote run metadata to %s", self.cfg.paths.training_info_file)

        for epoch in tqdm(range(1, self.cfg.training.epochs + 1), desc="epochs"):
            t0 = time.monotonic()
            train_loss = self.train_epoch(train_loader)

            if val_loader is not None:
                val_loss = self.evaluate(val_loader)
                self.log.info(
                    "epoch %d  train=%.6f  val=%.6f", epoch, train_loss, val_loss
                )
                if val_loss < best_val:
                    best_val = val_loss
                    best_val_epoch = epoch
                    torch.save(
                        self.model.state_dict(),
                        self.cfg.paths.checkpoint_dir / "parameters.pt",
                    )
                monitored = val_loss
                if training_metrics is not None:
                    training_metrics.update(self.model, val_loader)
            else:
                val_loss = None
                self.log.info("epoch %d  train=%.6f", epoch, train_loss)
                torch.save(
                    self.model.state_dict(),
                    self.cfg.paths.checkpoint_dir / "parameters.pt",
                )
                monitored = train_loss

            self._step_scheduler(monitored)
            lr = self._current_lr()

            if training_metrics is not None:
                training_metrics.log_epoch(
                    self.run_id,
                    epoch,
                    datetime.now(timezone.utc).isoformat(),
                    time.monotonic() - t0,
                    lr,
                    train_loss,
                    val_loss,
                )

            es_info = EarlyStoppingInfo(
                epoch=epoch,
                train_loss=train_loss,
                val_loss=val_loss,
                best_val_loss=best_val,
                best_val_epoch=best_val_epoch,
                learning_rate=lr,
            )
            if self.early_stopper.should_early_stop(es_info):
                self.log.info(
                    "early stop at epoch %d: %s", epoch, self.early_stopper.reason()
                )
                stopped_early = True
                break

        self.info.finalize(
            total_epochs=epoch,
            best_val_loss=best_val,
            best_val_epoch=best_val_epoch,
            stopped_early=stopped_early,
        )
        self.info.save(self.cfg.paths.training_info_file)

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
            if self.grad_clip is not None:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(), self.grad_clip
                )
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
