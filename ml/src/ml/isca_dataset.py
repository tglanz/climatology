from pathlib import Path

import torch
from torch.utils.data import Dataset, DataLoader

from ml.config import Config, DataConfig


class IscaDataset(Dataset):
    def __init__(self, experiment_dirs: list[Path], x_vars: list[str], y_vars: list[str]):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        raise NotImplementedError


def make_splits(cfg: DataConfig) -> tuple[IscaDataset, IscaDataset, IscaDataset]:
    raise NotImplementedError


def make_loaders(cfg: Config) -> tuple[DataLoader, DataLoader, DataLoader]:
    raise NotImplementedError
