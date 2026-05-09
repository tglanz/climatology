import logging
from pathlib import Path

import h5py
import numpy as np
import torch
import xarray as xr
from torch.utils.data import Dataset, DataLoader

from ml.config import Config

log = logging.getLogger(__name__)


def fix_time_units(ds: xr.Dataset) -> xr.Dataset:
    for v in ds.variables:
        if "units" in ds[v].attrs and "0000-00-00" in ds[v].attrs["units"]:
            ds[v].attrs["units"] = (
                ds[v].attrs["units"].replace("0000-00-00", "0001-01-01")
            )
        if ds[v].attrs.get("calendar") == "NO_CALENDAR":
            ds[v].attrs["calendar"] = "360_day"
    return ds


def validate_segment(
    path: Path, x_vars: list[str], y_vars: list[str]
) -> tuple[int, tuple]:
    ds = xr.open_dataset(path, decode_times=False)
    ds = fix_time_units(ds)

    all_vars = list(dict.fromkeys(x_vars + y_vars))
    for var in all_vars:
        assert var in ds, f"variable '{var}' not in {path}"
        assert (
            "time" in ds[var].dims
        ), f"variable '{var}' has no time dimension in {path}"

    if "average_DT" in ds:
        dt = ds["average_DT"].values
        assert np.allclose(dt, dt[0], rtol=1e-3), f"inconsistent time steps in {path}"

    T = ds.sizes["time"]
    spatial = (ds.sizes["lat"], ds.sizes["lon"])
    ds.close()
    return T, spatial


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
    """
    Load the latitude grid for the dataset.

    Reads the first segment listed in the train split of splits.json and
    returns the 1-D latitude array (degrees north).
    """
    import json

    manifest_path = cfg.paths.preprocessed_dir / "splits.json"
    assert manifest_path.exists(), (
        f"manifest not found: {manifest_path}; run preprocess training-data first"
    )
    with open(manifest_path) as f:
        manifest = json.load(f)

    train_dirs = manifest.get("train", [])
    assert train_dirs, "no train simulations in manifest"

    sim_dir = (cfg.paths.preprocessed_dir / train_dirs[0]).resolve()
    nc_files = sorted(sim_dir.glob(cfg.data.segment_pattern))
    assert nc_files, f"no NC files in {sim_dir} matching {cfg.data.segment_pattern}"

    ds = xr.open_dataset(nc_files[0], decode_times=False)
    assert "lat" in ds, f"variable 'lat' not in {nc_files[0]}"
    lat = ds["lat"].values.astype(np.float32)
    ds.close()
    return lat
