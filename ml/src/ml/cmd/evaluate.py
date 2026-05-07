import json
import logging
from pathlib import Path

import click
import numpy as np
import xarray as xr

from ml.config import load as load_config
from ml.common.logging import setup_logging
from ml.model import build_model
from ml.inference import Autoregressor
from ml.isca_dataset import fix_time_units


@click.group()
def evaluate():
    pass


@evaluate.command()
@click.option("-c", "--config", "config_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--start", "t0", required=True, type=int, help="Index of initial timestep.")
@click.option("--timesteps", "T", required=True, type=int, help="Number of steps to roll out.")
@click.option("--output", "output_path", default=None, type=click.Path(path_type=Path),
              help="Output NC path. Defaults to <experiment_dir>/eval/autoregression.nc.")
def autoregression(config_path: Path, input_path: Path, t0: int, T: int, output_path: Path | None):
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    log = logging.getLogger(__name__)

    if output_path is None:
        output_path = cfg.data.experiment_dir / "eval" / "autoregression.nc"

    # Verify input is from the test split.
    manifest_path = cfg.paths.preprocessed_dir / "splits.json"
    assert manifest_path.exists(), f"splits.json not found: {manifest_path} — run preprocess first"
    with open(manifest_path) as f:
        manifest = json.load(f)

    test_dirs = {
        (manifest_path.parent / rel).resolve()
        for rel in manifest.get("test", [])
    }
    sim_dir = input_path.parent.parent.resolve()
    assert sim_dir in test_dirs, (
        f"input simulation {sim_dir} is not in the test split — "
        f"refusing to evaluate on training or validation data"
    )

    # Load dataset and slice.
    ds = xr.open_dataset(input_path, decode_times=False)
    ds = fix_time_units(ds)
    n_times = ds.sizes["time"]
    assert n_times >= t0 + T + 1, (
        f"file has {n_times} timesteps but need at least {t0 + T + 1} "
        f"(--start {t0} + --timesteps {T} + 1)"
    )
    ds_slice = ds.isel(time=slice(t0, t0 + T + 1))

    vor0 = ds_slice["vor"].values[0]
    stirring_seq = ds_slice["stirring"].values[:T]

    # Run autoregression.
    model = build_model(cfg.model.fno)
    autoregressor = Autoregressor(model, cfg.paths.checkpoint_dir)
    vor_pred = autoregressor.rollout(vor0, stirring_seq)

    vor_truth = ds_slice["vor"].values
    vor_pred_err = vor_pred - vor_truth

    rms = float(np.sqrt(np.mean(vor_pred_err ** 2)))
    log.info("RMS error over rollout: %.6f", rms)

    # Build output dataset.
    dims = ("time", "lat", "lon")
    out_ds = ds_slice.copy()
    out_ds["vor_pred"] = xr.DataArray(
        vor_pred.astype(np.float32),
        dims=dims,
        attrs=ds["vor"].attrs,
    )
    out_ds["vor_pred_err"] = xr.DataArray(
        vor_pred_err.astype(np.float32),
        dims=dims,
        attrs={"units": ds["vor"].attrs.get("units", "1/s"), "long_name": "vorticity prediction error (pred - truth)"},
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_ds.to_netcdf(output_path)
    log.info("wrote evaluation output to %s", output_path)
