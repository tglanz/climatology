"""Evaluation command options."""

from pathlib import Path
import click
from ml.usecases.evaluate import run


@click.group()
def evaluate():
    pass


@evaluate.command("model")
@click.option(
    "--training-dir", required=True, type=click.Path(exists=True, path_type=Path)
)
@click.option("--n-workers", default=8, show_default=True, type=int)
@click.option("--batch-size", default=64, show_default=True, type=int)
def evaluate_model(training_dir: Path, n_workers: int, batch_size: int):
    """Evaluate a trained SFNO model against all available simulation data."""
    run(training_dir, n_workers, batch_size)
