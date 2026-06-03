import json
import logging
from pathlib import Path

import click
from ml.data.splits import Splits
import numpy as np
import xarray as xr

from ml.config import load as load_config
from ml.common.logging import setup_logging
from ml.diagnostics import rms_error
from ml.model import build_model
from ml.inference import Autoregressor
from ml.data.isca_segment import read_segment


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

    splits = Splits.from_config(cfg.paths)

    sim_dir = input_path.parent.parent.resolve()
    assert splits.has_test(sim_dir), (
        f"input simulation {sim_dir} is not in the test split - "
        f"refusing to evaluate on training or validation data"
    )

    K = cfg.data.windows.length

    # Load dataset and slice. With input_length=K we need K-1 timesteps before
    # t0 to form the first input window, and one timestep after the last
    # prediction for ground-truth comparison.
    ds = read_segment(input_path)
    n_times = ds.sizes["time"]
    assert t0 >= K - 1, (
        f"--start {t0} must be >= input_length - 1 = {K - 1} so that K={K} "
        f"history timesteps are available"
    )
    history_start = t0 - (K - 1)
    end_exclusive = t0 + T + 1
    assert n_times >= end_exclusive, (
        f"file has {n_times} timesteps but need at least {end_exclusive} "
        f"(--start {t0} + --timesteps {T} + 1)"
    )
    ds_slice = ds.isel(time=slice(history_start, end_exclusive))

    vor_history = ds_slice["vor"].values[:K]
    # stirring covers all K-step windows used during the rollout:
    # last window is (t0+T-K, ..., t0+T-1), i.e. K + T - 1 timesteps total.
    stirring_seq = ds_slice["stirring"].values[: K + T - 1]

    # Run autoregression. Reconstruct the architecture exactly as it was at
    # training time, including dropout layers (no-ops in eval mode).
    model = build_model(cfg.model, dropout=cfg.training.regularization.dropout)
    autoregressor = Autoregressor(model, cfg.paths.checkpoint_dir)
    vor_pred = autoregressor.rollout(vor_history, stirring_seq)

    vor_truth = ds_slice["vor"].values
    vor_pred_err = vor_pred - vor_truth

    rms = rms_error(vor_pred, vor_truth)
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
