from pathlib import Path

import click

from ml.config import load as load_config
from ml.common.logging import setup_logging
from ml.data.isca_preprocessing import IscaDataPreprocessor

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
    help="If true, computes spinup time. If no spinup time is found, marks the simulation invalid",
)
@click.option(
    "--workers",
    default=8,
    show_default=True,
    help="Number of parallel worker processes. 0 = run on main thread",
)
def validate_simulations(config_path: Path, invalid_only: bool, validate_spinup: bool, workers: int):
    from ml.usecases.validate_simulations import run
    setup_logging(load_config(config_path).logging)

    n_invalid = run(
        config_path=config_path,
        validate_spinup=validate_spinup,
        invalid_only=invalid_only,
        workers=workers,
    )

    if n_invalid > 0:
        raise SystemExit(2)
