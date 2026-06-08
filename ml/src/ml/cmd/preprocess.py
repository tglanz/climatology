from pathlib import Path

import click

from ml.config import load as load_config
from ml.common.logging import setup_logging

@click.group()
def preprocess():
    pass


@preprocess.command("training-data")
@click.option("-c", "--config", "config_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--workers", default=0, show_default=True, help="Parallel worker processes. 0 = serial.")
def preprocess_training_data(config_path: Path, workers: int):
    from ml.usecases.preprocess import run
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    run(config_path, n_workers=workers)


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
    help="If true, computes spinup time. If no spinup time is found, marks the simulation invalid",
)
@click.option(
    "--validate-convergence",
    is_flag=True,
    default=False,
    help="If true, runs convergence detection. If convergence is not reached, marks the simulation invalid",
)
@click.option(
    "--validate-climatology",
    is_flag=True,
    default=False,
    help="If true, resolves the climatology window and marks simulations invalid if it cannot be satisfied",
)
@click.option(
    "--workers",
    default=8,
    show_default=True,
    help="Number of parallel worker processes. 0 = run on main thread",
)
def validate_simulations(config_path: Path, invalid_only: bool, validate_spinup: bool, validate_convergence: bool, validate_climatology: bool, workers: int):
    from ml.usecases.validate_simulations import run
    setup_logging(load_config(config_path).logging)

    n_invalid = run(
        config_path=config_path,
        should_validate_spinup=validate_spinup,
        should_validate_convergence=validate_convergence,
        should_validate_climatology=validate_climatology,
        invalid_only=invalid_only,
        workers=workers,
    )

    if n_invalid > 0:
        raise SystemExit(2)
