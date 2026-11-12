"""Bounded examples use the same preparation, training, and evaluation stages."""

from dataclasses import replace
from pathlib import Path
import json
import numpy as np
import xarray as xr

from ml.config import (
    load,
    save,
    PreparationConfig,
    WindowsConfig,
    ClimatologyConfig,
    SchedulerConfig,
    EarlyStoppingConfig,
    PathsConfig,
    SplitConfig,
)
from ml.data.splits import Splits

# Kept explicit: changing the subset is a new experimental recipe.
REAL_CODES = ("10bb40-0", "0f0ad6-0", "021787-0")  # train, validation, test


def create(directory: Path, real_root: Path | None = None):
    directory = directory.resolve()
    base = load(Path(__file__).resolve().parents[3] / "configs" / "default.toml")
    source = real_root.resolve() if real_root else directory
    names = REAL_CODES if real_root else ("train-0", "validation-0", "test-0")
    paths = [source / "simulations" / n for n in names]
    if real_root and not all(p.is_dir() for p in paths):
        raise ValueError(f"fixed real subset missing: {paths}")
    directory.mkdir(parents=True, exist_ok=False)
    if real_root:
        data = replace(base.data, windows=replace(base.data.windows, limit=2))
    else:
        rng = np.random.default_rng(17)
        lat = np.rad2deg(np.arcsin(np.polynomial.legendre.leggauss(8)[0]))
        lon = np.arange(24) * 15.0
        for index, path in enumerate(paths):
            path.mkdir(parents=True)
            shape = (24, len(lat), len(lon))
            wave = np.cos(np.deg2rad(lat))[None, :, None]
            u = np.broadcast_to(10 * wave + index, shape).copy()
            vor = rng.normal(0, 1e-6, shape)
            ds = xr.Dataset(
                {
                    "vor": (("time", "lat", "lon"), vor),
                    "ucomp": (("time", "lat", "lon"), u),
                },
                coords={"time": np.arange(24, dtype=float), "lat": lat, "lon": lon},
            )
            ds.time.attrs.update(units="days since 2000-01-01", calendar="360_day")
            ds.lat.attrs["units"], ds.lon.attrs["units"] = "degrees_N", "degrees_E"
            ds.vor.attrs["units"], ds.ucomp.attrs["units"] = "1/s", "m/s"
            ds.to_netcdf(path / "atmos_daily.nc")
            ds.close()
        data = replace(
            base.data,
            segment_pattern="atmos_daily.nc",
            spinup=None,
            convergence=None,
            windows=WindowsConfig("beginning", "end", 2, 3, 3),
            climatology=ClimatologyConfig(end_at="end", length=12),
        )
    data = replace(data, split=SplitConfig(validation_ratio=0.2, test_ratio=0.2))
    paths_cfg = PathsConfig(
        source,
        preprocessed_dir=directory / "prepared",
        training_dir=directory / "run",
        splits_dir=directory / "splits",
    )
    save(PreparationConfig(data, base.logging, paths_cfg), directory / "prepare.toml")
    Splits([paths[2]], [paths[1]], [paths[0]]).save(
        directory / "splits", "fixed", "Fixed pipeline iteration subset", data.split
    )
    model = replace(
        base.model,
        fno=None,
        sfno=replace(
            base.model.sfno,
            n_modes=(4, 4),
            hidden_channels=4,
            n_layers=1,
            in_channels=data.windows.length * len(data.x_vars),
        ),
    )
    training = replace(
        base.training,
        epochs=2,
        batch_size=2,
        seed=17,
        scheduler=SchedulerConfig(kind="none"),
        early_stopping=EarlyStoppingConfig(),
    )
    import tomli_w
    from dataclasses import asdict

    # Keep the model recipe separate while its saved run snapshot is standalone.
    raw = {
        "data_config": "prepare.toml",
        "model": {"architecture": "sfno", "sfno": asdict(model.sfno)},
        "training": {
            "epochs": training.epochs,
            "batch_size": training.batch_size,
            "seed": training.seed,
            "loss": training.loss,
            "learning_rate": training.learning_rate,
            "scheduler": {"kind": "none"},
        },
        "paths": {"training_dir": str(directory / "run")},
    }
    (directory / "run.toml").write_text(tomli_w.dumps(raw))
    raw["model"]["sfno"]["hidden_channels"] = 6
    raw["paths"]["training_dir"] = str(directory / "run-wide")
    (directory / "run-wide.toml").write_text(tomli_w.dumps(raw))
    (directory / "recipe.json").write_text(
        json.dumps(
            {
                "kind": "real-subset" if real_root else "synthetic",
                "seed": 17,
                "simulations": [str(p) for p in paths],
                "purpose": "software iteration; no claim of scientific model quality",
            },
            indent=2,
        )
        + "\n"
    )
