"""Validated HDF5 datasets with process-local file handles."""

import logging
from pathlib import Path

import h5py
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from ml.config import Config
from ml.data.metadata import DataMetadata
from ml.diagnostics.grid import GaussianGrid

log = logging.getLogger(__name__)


class IscaDataset(Dataset):
    def __init__(self, h5_path: Path):
        self.h5_path = h5_path
        with h5py.File(h5_path, "r") as handle:
            self.metadata = DataMetadata.read_hdf5(handle)
            self.length = handle["x"].shape[0]
            height, width = self.metadata.grid.shape
            if handle["x"].shape != (
                self.length,
                self.metadata.input_channels,
                height,
                width,
            ):
                raise ValueError("prepared input shape differs from its metadata")
            if handle["y"].shape != (self.length, len(self.metadata.y_vars), height):
                raise ValueError("prepared target shape differs from its metadata")
            if "simulation_targets" not in handle or "simulation_paths" not in handle:
                raise ValueError(
                    "prepared data lack simulation identity; regenerate the splits"
                )
            profiles = handle["simulation_targets"]
            paths = handle["simulation_paths"].asstr()[:]
            if (
                profiles.shape != (len(paths), len(self.metadata.y_vars), height)
                or len(set(paths)) != len(paths)
                or len(paths) > self.length
                or (self.length > 0 and len(paths) == 0)
            ):
                raise ValueError("invalid prepared simulation target table")
        self._file: h5py.File | None = None
        log.info("dataset: %d pairs from %s", self.length, h5_path)

    @property
    def simulation_targets(self) -> torch.Tensor:
        """One target profile per accepted simulation, independent of window count."""
        with h5py.File(self.h5_path, "r") as handle:
            return torch.from_numpy(handle["simulation_targets"][:])

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        if self._file is None:
            import weakref

            self._file = h5py.File(self.h5_path, "r")
            weakref.finalize(self, self._file.close)
        return torch.from_numpy(self._file["x"][idx]), torch.from_numpy(
            self._file["y"][idx]
        )


def make_loader(
    path: Path, batch_size: int, shuffle: bool, num_workers: int = 0
) -> DataLoader | None:
    if num_workers < 0 or batch_size < 1:
        raise ValueError("invalid data-loader settings")
    ds = IscaDataset(path)
    if len(ds) == 0:
        return None
    return DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        persistent_workers=num_workers > 0,
    )


def make_loaders(
    cfg: Config, num_workers: int = 0
) -> tuple[DataLoader, DataLoader | None, DataLoader | None]:
    out_dir = cfg.paths.preprocessed_dir
    loaders = [
        make_loader(
            out_dir / f"{split}.h5",
            cfg.training.batch_size,
            split == "train",
            num_workers,
        )
        for split in ("train", "val", "test")
    ]
    if loaders[0] is None:
        raise ValueError("training split has no usable samples")
    reference = loaders[0].dataset.metadata
    for split, loader in zip(("train", "val", "test"), loaders, strict=True):
        metadata = (
            loader.dataset.metadata
            if loader
            else IscaDataset(out_dir / f"{split}.h5").metadata
        )
        metadata.validate_config(cfg.data)
        if not reference.matches(metadata):
            raise ValueError("prepared split coordinates differ")
    cfg.training.validate_loaders(loaders[0], loaders[1])
    return tuple(loaders)


def load_grid(cfg: Config) -> GaussianGrid:
    ds = IscaDataset(cfg.paths.preprocessed_dir / "train.h5")
    ds.metadata.validate_config(cfg.data)
    return ds.metadata.grid


def load_latitudes(cfg: Config) -> np.ndarray:
    return load_grid(cfg).latitudes.copy()
