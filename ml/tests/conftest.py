"""Small, physically labelled Gaussian-grid inputs shared by correctness tests."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from ml.config import (
    load,
    ClimatologyConfig,
    WindowsConfig,
    PathsConfig,
    SchedulerConfig,
    EarlyStoppingConfig,
)


@pytest.fixture
def gaussian_coordinates():
    lat = np.rad2deg(np.arcsin(np.polynomial.legendre.leggauss(4)[0]))
    return lat, np.arange(12) * 30.0


def write_simulation(root, lat, lon, offset=0.0):
    values = (
        np.arange(12 * len(lat) * len(lon), dtype=np.float32).reshape(
            12, len(lat), len(lon)
        )
        / 100
        + 1
        + offset
    )
    paths = []
    for segment, start in enumerate((0, 6), 1):
        path = root / f"run{segment:04d}" / "atmos_daily.nc"
        path.parent.mkdir(parents=True)
        ds = xr.Dataset(
            {
                name: (("time", "lat", "lon"), values[start : start + 6] + shift)
                for name, shift in (("vor", 0), ("ucomp", 2), ("vcomp", 4))
            },
            coords={
                "time": np.arange(start, start + 6, dtype=float),
                "lat": lat,
                "lon": lon,
            },
        )
        ds.time.attrs.update(units="days since 2000-01-01", calendar="360_day")
        ds.lat.attrs["units"] = "degrees_N"
        ds.lon.attrs["units"] = "degrees_E"
        for name in ("ucomp", "vcomp"):
            ds[name].attrs["units"] = "m/s"
        ds.vor.attrs["units"] = "1/s"
        ds.to_netcdf(path)
        ds.close()
        paths.append(path)
    return paths, values


@pytest.fixture
def simulation(gaussian_coordinates, tmp_path):
    lat, lon = gaussian_coordinates
    paths, values = write_simulation(tmp_path / "simulations" / "code-0", lat, lon)
    base = load(Path("ml/configs/default.toml"))
    data = replace(
        base.data,
        spinup=None,
        convergence=None,
        x_vars=["vor", "vcomp"],
        y_vars=["time_mean_zonal_mean_ucomp", "time_mean_zonal_mean_vor"],
        windows=WindowsConfig("beginning", "end", 3, 2, 4),
        climatology=ClimatologyConfig(end_at="end", length=2),
    )
    model = replace(
        base.model,
        sfno=replace(
            base.model.sfno,
            n_modes=(4, 4),
            hidden_channels=4,
            n_layers=1,
            in_channels=6,
            out_channels=2,
        ),
    )
    training = replace(
        base.training,
        epochs=2,
        batch_size=3,
        loss="mse",
        scheduler=SchedulerConfig(kind="none"),
        early_stopping=EarlyStoppingConfig(),
    )
    training_dir = tmp_path / "training"
    paths_cfg = PathsConfig(
        experiment_dir=tmp_path,
        preprocessed_dir=tmp_path / "data",
        training_dir=training_dir,
        checkpoint_dir=training_dir,
        training_info_file=training_dir / "training.json",
        epoch_metrics_file=training_dir / "epoch-metrics.csv",
        metrics_file=training_dir / "metrics.h5",
        splits_dir=tmp_path / "splits",
    )
    return (
        paths,
        values,
        replace(base, data=data, model=model, training=training, paths=paths_cfg),
    )
