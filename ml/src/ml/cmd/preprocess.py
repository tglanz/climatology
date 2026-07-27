from pathlib import Path

import click

from ml.config import load as load_config
from ml.common.logging import setup_logging

class _OrderedGroup(click.Group):
    def list_commands(self, ctx):
        return list(self.commands)


@click.group(cls=_OrderedGroup)
def preprocess():
    """Prepare simulation data for training."""


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
    """Check simulations are complete and valid."""
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


@preprocess.command("create-sweep-file")
@click.option("--experiment-dir", "experiment_dir", required=True, type=click.Path(file_okay=False, path_type=Path))
@click.option(
    "--key", "keys",
    multiple=True,
    required=True,
    help="alias=nml.path, e.g. stirring_lat0=stirring_nml.lat0. Repeat for multiple keys.",
)
def create_sweep_file(experiment_dir: Path, keys: tuple[str, ...]):
    """Build sweep.json from completed simulation namelist.json files."""
    from ml.usecases.create_sweep_file import run

    key_specs = []
    for key in keys:
        if "=" not in key:
            raise click.ClickException(f"--key must be alias=nml.path, got: {key}")
        alias, path = key.split("=", 1)
        key_specs.append((alias, path.split(".")))

    run(experiment_dir, key_specs)


@preprocess.command("generate-splits")
@click.option("-c", "--config", "config_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--name", required=True, help="Split name; written to splits/<name>.json")
@click.option("--description", default="", help="Human-readable description stored in meta")
def generate_splits(config_path: Path, name: str, description: str):
    """Assign simulations to train/val/test splits."""
    from ml.usecases.generate_splits import run
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    run(config_path, name, description)


@preprocess.command("training-data")
@click.option("-c", "--config", "config_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--split", "split_path", required=True, type=click.Path(exists=True, path_type=Path), help="Path to split JSON file")
@click.option("--workers", default=0, show_default=True, help="Parallel worker processes. 0 = serial.")
def preprocess_training_data(config_path: Path, split_path: Path, workers: int):
    """Extract and preprocess windows into HDF5."""
    from ml.usecases.preprocess import run
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    run(config_path, Path(split_path), n_workers=workers)
