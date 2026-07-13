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
        self._file: h5py.File | None = None
        log.info("dataset: %d pairs from %s", self.length, h5_path)

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        if self._file is None:
            import weakref
            self._file = h5py.File(self.h5_path, "r")
            weakref.finalize(self, self._file.close)
        x = torch.from_numpy(self._file["x"][idx])
        y = torch.from_numpy(self._file["y"][idx])
        return x, y


def make_loader(path: Path, batch_size: int, shuffle: bool, num_workers: int = 0) -> DataLoader | None:
    assert (
        path.exists()
    ), f"preprocessed file missing: {path} - run preprocess-training-data first"
    ds = IscaDataset(path)
    if len(ds) == 0:
        return None
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle,
                      num_workers=num_workers, persistent_workers=num_workers > 0)


def make_loaders(
    cfg: Config,
    num_workers: int = 0,
) -> tuple[DataLoader, DataLoader | None, DataLoader | None]:
    out_dir = cfg.paths.preprocessed_dir
    bs = cfg.training.batch_size
    return (
        make_loader(out_dir / "train.h5", bs, shuffle=True, num_workers=num_workers),
        make_loader(out_dir / "val.h5", bs, shuffle=False, num_workers=num_workers),
        make_loader(out_dir / "test.h5", bs, shuffle=False, num_workers=num_workers),
    )


def load_latitudes(cfg: Config) -> np.ndarray:
    splits = Splits.load(cfg.paths.preprocessed_dir / "splits.json")
    assert splits.train, "no train simulations in splits"
    nc_files = list_segment_files(splits.train[0], cfg.data)
    assert nc_files, f"no NC files in {splits.train[0]} matching {cfg.data.segment_pattern}"
    ds = read_segment(nc_files[0], {})
    lat = ds["lat"].values.astype(np.float32)
    ds.close()
    return lat
