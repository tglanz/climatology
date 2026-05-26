from pathlib import Path

import click
import numpy as np
import xarray as xr

from ml.config import load as load_config
from ml.common.logging import setup_logging
from ml.data.isca_dataset import validate_segment
from ml.data.isca_preprocessing import IscaDataPreprocessor
from ml.diagnostics import mean_enstrophy


@click.group()
def preprocess():
    pass


@preprocess.command("training-data")
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def preprocess_training_data(config_path: Path):
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    IscaDataPreprocessor(cfg).run()


@preprocess.command("validate-simulations")
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--invalid-only",
    is_flag=True,
    default=False,
    help="Only print simulations that fail validation.",
)
@click.option(
    "--analyze",
    is_flag=True,
    default=False,
    help=(
        "Also compute mean global enstrophy (cos-lat-weighted spatial mean of "
        "0.5*vor**2, averaged over time) for each valid simulation."
    ),
)
def validate_simulations(config_path: Path, invalid_only: bool, analyze: bool):
    """
    Walk every simulation under data.simulation_pattern and emit one line per sim:

        <sim_dir> -- runs=<N>; samples=<T>; enstrophy=<F | ->; valid=<true|false>; invalid_reason=<...>

    The format is stable so callers can `cut -d' ' -f1` to extract the sim path,
    or `awk -F'; ' '{...}'` to slice the key=value pairs.
    """
    cfg = load_config(config_path)
    setup_logging(cfg.logging)

    sim_dirs = sorted(cfg.data.experiment_dir.glob(cfg.data.simulation_pattern))
    if not sim_dirs:
        print(
            f"no simulations matched "
            f"{cfg.data.experiment_dir}/{cfg.data.simulation_pattern}"
        )
        raise SystemExit(1)

    K = cfg.data.windows.length
    n_invalid = 0

    for sim_dir in sim_dirs:
        nc_files = sorted(sim_dir.glob(cfg.data.segment_pattern))
        n_runs = len(nc_files)
        n_samples = 0
        valid = True
        reason = ""

        if not nc_files:
            valid = False
            reason = "no segments matching segment_pattern"
        else:
            for nc in nc_files:
                try:
                    T, _ = validate_segment(nc, cfg.data.x_vars, cfg.data.y_vars)
                except (AssertionError, OSError, ValueError) as e:
                    valid = False
                    reason = f"{nc.name}: {e}"
                    break
                n_samples += T
            if valid and n_samples < K + 1:
                valid = False
                reason = f"timeline too short: {n_samples} < {K + 1}"

        enstrophy_str = "-"
        if analyze and valid:
            try:
                e = _per_simulation_mean_enstrophy(nc_files)
                enstrophy_str = f"{e:.6e}" if e is not None else "-"
            except Exception as ex:
                enstrophy_str = f"err:{ex}"

        if not valid:
            n_invalid += 1

        if invalid_only and valid:
            continue

        print(
            f"{sim_dir} -- "
            f"runs={n_runs}; "
            f"samples={n_samples}; "
            f"enstrophy={enstrophy_str}; "
            f"valid={'true' if valid else 'false'}; "
            f"invalid_reason={reason}"
        )

    if n_invalid > 0:
        raise SystemExit(2)


def _per_simulation_mean_enstrophy(nc_files: list[Path]) -> float | None:
    """
    Time-mean global enstrophy across every timestep contained in
    `nc_files` (the segments that make up one simulation). Returns None
    if 'vor' is absent. Per-timestep math is delegated to
    `ml.diagnostics.mean_enstrophy`.
    """
    total = 0.0
    n_steps = 0
    for nc in nc_files:
        ds = xr.open_dataset(nc, decode_times=False)
        try:
            if "vor" not in ds:
                continue
            vor = ds["vor"].values.astype(np.float64)
            lat = ds["lat"].values.astype(np.float64)
            per_t = mean_enstrophy(vor, lat)  # shape (T,)
            total += float(per_t.sum())
            n_steps += per_t.size
        finally:
            ds.close()
    return total / n_steps if n_steps > 0 else None
