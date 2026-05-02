import logging
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
                torch.norm(pred - target, dim=(-2, -1)) / torch.norm(target, dim=(-2, -1))
            )
        return relative_l2
    raise ValueError(f"unknown loss: {kind}")


class Trainer:
    def __init__(self, model: nn.Module, cfg: Config):
        self.cfg = cfg
        self.log = logging.getLogger(__name__)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.log.info("device: %s", self.device)

        self.model = model.to(self.device)
        self.loss_fn = create_loss_fn(cfg.training.loss)

        if cfg.training.optimizer == "adam":
            self.optimizer = torch.optim.Adam(model.parameters(), lr=cfg.training.learning_rate)
        elif cfg.training.optimizer == "adamw":
            self.optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.training.learning_rate, weight_decay=cfg.training.weight_decay)
        else:
            raise ValueError(f"unknown optimizer: {cfg.training.optimizer}")

        self.scheduler = torch.optim.lr_scheduler.StepLR(
            self.optimizer,
            step_size=cfg.training.lr_decay_every,
            gamma=cfg.training.lr_decay_factor,
        )
        cfg.paths.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def fit(self, train_loader: DataLoader, val_loader: DataLoader):
        best_val = float("inf")

        for epoch in tqdm(range(1, self.cfg.training.epochs + 1), desc="epochs"):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.evaluate(val_loader)
            self.scheduler.step()

            self.log.info("epoch %d  train=%.6f  val=%.6f", epoch, train_loss, val_loss)

            if val_loss < best_val:
                best_val = val_loss
                torch.save(self.model.state_dict(), self.cfg.paths.checkpoint_dir / "best.pt")

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
