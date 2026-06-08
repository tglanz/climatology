import logging
from pathlib import Path

import h5py
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from ml.config import Config
from ml.data.splits import Splits
from ml.data.isca_segment import read_segment
from ml.data.isca_preprocessing import list_segment_files

log = logging.getLogger(__name__)

class IscaDataset(Dataset):
    def __init__(self, h5_path: Path):
        assert h5_path.exists(), f"preprocessed file not found: {h5_path}"
        self.h5_path = h5_path
        with h5py.File(h5_path, "r") as f:
            self.length = f["x"].shape[0]
        log.info("dataset: %d pairs from %s", self.length, h5_path)

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        with h5py.File(self.h5_path, "r") as f:
            x = torch.from_numpy(f["x"][idx])
            y = torch.from_numpy(f["y"][idx])
        return x, y


def make_loader(path: Path, batch_size: int, shuffle: bool) -> DataLoader | None:
    assert (
        path.exists()
    ), f"preprocessed file missing: {path} - run preprocess-training-data first"
    ds = IscaDataset(path)
    if len(ds) == 0:
        return None
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle)


def make_loaders(
    cfg: Config,
) -> tuple[DataLoader, DataLoader | None, DataLoader | None]:
    out_dir = cfg.paths.preprocessed_dir
    bs = cfg.training.batch_size
    return (
        make_loader(out_dir / "train.h5", bs, shuffle=True),
        make_loader(out_dir / "val.h5", bs, shuffle=False),
        make_loader(out_dir / "test.h5", bs, shuffle=False),
    )


def load_latitudes(cfg: Config) -> np.ndarray:
    splits = Splits.from_config(cfg.paths)
    assert splits.train, "no train simulations in splits"
    nc_files = list_segment_files(splits.train[0], cfg.data)
    assert nc_files, f"no NC files in {splits.train[0]} matching {cfg.data.segment_pattern}"
    ds = read_segment(nc_files[0], {})
    lat = ds["lat"].values.astype(np.float32)
    ds.close()
    return lat
