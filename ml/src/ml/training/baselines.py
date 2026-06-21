import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from ml.data.climatology import is_climatology_var
from ml.diagnostics import persistence_prediction


def _assert_persistence_supported(x_vars: list[str], y_vars: list[str]) -> None:
    if any(is_climatology_var(v) for v in y_vars):
        raise ValueError(
            f"persistence baseline requires step-mode y_vars, got climatology vars in {y_vars}"
        )
    if "vor" not in x_vars:
        raise ValueError(
            f"persistence baseline requires 'vor' in x_vars, got {x_vars}"
        )


def score_zero(val_loader: DataLoader, loss_fn: nn.Module) -> float:
    total = 0.0
    n = 0
    with torch.no_grad():
        for _, y in val_loader:
            total += loss_fn(torch.zeros_like(y), y).item()
            n += 1
    return total / n


def score_mean(train_loader: DataLoader, val_loader: DataLoader, loss_fn: nn.Module) -> float:
    

    # Each y is a meridional profile; e.g. (1, H)
    ys = [y for _, y in train_loader]

    # We concatenate all profiles by the first dimension;
    # We get a tensor (N, 1, H)
    y_train = torch.cat(ys, dim=0)

    # We predice a baseline of mean; the result tensor is (1, H).
    # This prediction will be used for all validation samples, irrespective to their x.
    pred = y_train.mean(dim=0, keepdim=True)

    total = 0.0
    n = 0

    with torch.no_grad():
        for _, y in val_loader:
            total += loss_fn(pred.expand_as(y), y).item()
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

def score_persistence(
    val_loader: DataLoader,
    loss_fn: nn.Module,
    x_vars: list[str],
    y_vars: list[str],
    window_length: int,
) -> float:
    _assert_persistence_supported(x_vars, y_vars)
    n_vars = len(x_vars)
    vor_t_channel = (window_length - 1) * n_vars + x_vars.index("vor")
    total = 0.0
    n = 0
    with torch.no_grad():
        for x, y in val_loader:
            pred = persistence_prediction(x, vor_t_channel)
            total += loss_fn(pred, y).item()
            n += 1
    return total / n
