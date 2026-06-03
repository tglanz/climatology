from pathlib import Path

import click
from ml.diagnostics.enstrophy import mean_enstrophy
from ml.diagnostics.spinup import find_spinup_time
import numpy as np
from tqdm import tqdm

from ml.config import load as load_config
from ml.common.logging import setup_logging
from ml.data.isca_segment import read_segment, validate_segment, aggregated_read_field
from ml.data.isca_preprocessing import IscaDataPreprocessor, list_simulation_dirs, list_segment_files


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
    help="Only print simulations that fail validation",
)
@click.option(
    "--validate-spinup",
    is_flag=True,
    default=False,
    help="If true, computes spinup time. If no spinup time is found, marks the file is invalid"
)
def validate_simulations(config_path: Path, invalid_only: bool, validate_spinup: bool):
    cfg = load_config(config_path)
    setup_logging(cfg.logging)

    sim_dirs = list_simulation_dirs(cfg.data)

    K = cfg.data.windows.length
    n_invalid = 0

    for sim_dir in tqdm(sim_dirs):
        nc_files = list_segment_files(sim_dir, cfg.data)
        n_runs = len(nc_files)
        n_samples = 0
        valid = True
        reason = ""

        if not nc_files:
            valid = False
            reason = "no segments matching segment_pattern"
        else:
            segments_cache = {}
            for nc_path in nc_files:
                try:
                    segment_samples_count, segment_spatial_shape = validate_segment(
                        nc_path, cfg.data.x_vars, cfg.data.y_vars, cache=segments_cache)
                except (AssertionError, OSError, ValueError) as e:
                    valid = False
                    reason = f"{nc_path.name}: {e}"
                    break
                n_samples += segment_samples_count
            if valid and n_samples < K + 1:
                valid = False
                reason = f"timeline too short: {n_samples} < {K + 1}"

        if valid and validate_spinup:
            lats = read_segment(nc_files[0], cache=segments_cache)["lat"].values
            vorticities = aggregated_read_field(nc_files, "vor", cache=segments_cache)
            enstrophy = mean_enstrophy(vorticities, lats)
            t_spinup = find_spinup_time(diagnostic=enstrophy,
                stable_time=cfg.data.spinup.hold,
                tol=cfg.data.spinup.threshold)
            if not t_spinup:
                valid = False
                reason = f"Unable to infer spinup time with {cfg.data.spinup}"

        if not valid:
            n_invalid += 1

        if invalid_only and valid:
            continue

        tqdm.write(
            f"{sim_dir} -- "
            f"runs={n_runs}; "
            f"samples={n_samples}; "
            f"valid={'true' if valid else 'false'}; "
            f"invalid_reason={reason}"
        )

    if n_invalid > 0:
        raise SystemExit(2)