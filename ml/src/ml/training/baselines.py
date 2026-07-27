import torch
import torch.nn as nn
from torch.utils.data import DataLoader


def score_zero(val_loader: DataLoader, loss_fn: nn.Module) -> float:
    total = 0.0
    n = 0
    with torch.no_grad():
        for _, y in val_loader:
            total += loss_fn(torch.zeros_like(y), y).item()
            n += 1
    return total / n


def score_mean(train_loader: DataLoader, val_loader: DataLoader, loss_fn: nn.Module) -> float:
    y_train = torch.cat([y for _, y in train_loader], dim=0)
    pred = y_train.mean(dim=0, keepdim=True)
    total = 0.0
    n = 0
    with torch.no_grad():
        for _, y in val_loader:
            total += loss_fn(pred.expand_as(y), y).item()
            n += 1
    return total / n
