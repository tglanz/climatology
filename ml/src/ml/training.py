import csv
import logging
import time
from datetime import datetime, timezone
from typing import Callable

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from ml.config import Config


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


EPOCH_METRICS_FILE = "epoch-metrics.csv"
RUNS_FILE = "runs.csv"
EPOCH_METRICS_HEADER = ["run_id", "epoch", "timestamp", "elapsed_seconds", "learning_rate", "train_loss", "val_loss"]
RUNS_HEADER = ["run_id", "start_time", "end_time", "total_epochs", "best_val_loss", "best_val_epoch", "stopped_early"]


def _append_csv(path, header, row):
    write_header = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        w.writerow(row)


class Trainer:
    def __init__(self, model: nn.Module, cfg: Config):
        self.cfg = cfg
        self.log = logging.getLogger(__name__)
        self.run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        cfg.paths.training_dir.mkdir(parents=True, exist_ok=True)
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
            self.optimizer = torch.optim.Adam(
                model.parameters(), lr=cfg.training.learning_rate
            )
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
        cfg.paths.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def fit(self, train_loader: DataLoader, val_loader: DataLoader | None):
        best_val = float("inf")
        best_val_epoch = -1
        target_loss = self.cfg.training.target_loss
        stopped_early = False
        start_time = datetime.now(timezone.utc)
        epoch_metrics_path = self.cfg.paths.training_dir / EPOCH_METRICS_FILE
        runs_path = self.cfg.paths.training_dir / RUNS_FILE

        for epoch in tqdm(range(1, self.cfg.training.epochs + 1), desc="epochs"):
            t0 = time.monotonic()
            train_loss = self.train_epoch(train_loader)
            self.scheduler.step()
            lr = self.scheduler.get_last_lr()[0]

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
                        self.cfg.paths.checkpoint_dir / "best.pt",
                    )
                monitored = val_loss
            else:
                val_loss = None
                self.log.info("epoch %d  train=%.6f", epoch, train_loss)
                torch.save(
                    self.model.state_dict(),
                    self.cfg.paths.checkpoint_dir / "best.pt",
                )
                monitored = train_loss

            elapsed = time.monotonic() - t0
            timestamp = datetime.now(timezone.utc).isoformat()
            _append_csv(epoch_metrics_path, EPOCH_METRICS_HEADER, [
                self.run_id, epoch, timestamp, f"{elapsed:.3f}", f"{lr:.2e}",
                f"{train_loss:.6f}", f"{val_loss:.6f}" if val_loss is not None else "",
            ])

            if target_loss is not None and monitored <= target_loss:
                self.log.info("target loss %.6f reached at epoch %d, stopping", target_loss, epoch)
                stopped_early = True
                break

        _append_csv(runs_path, RUNS_HEADER, [
            self.run_id,
            start_time.isoformat(),
            datetime.now(timezone.utc).isoformat(),
            epoch,
            f"{best_val:.6f}" if best_val < float("inf") else "",
            best_val_epoch if best_val_epoch > 0 else "",
            stopped_early,
        ])

    def train_epoch(self, loader: DataLoader) -> float:
        self.model.train()
        total = 0.0
        for x, y in tqdm(loader, desc="train", leave=False):
            x, y = x.to(self.device), y.to(self.device)
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
                total += self.loss_fn(self.model(x), y).item()
        return total / len(loader)
