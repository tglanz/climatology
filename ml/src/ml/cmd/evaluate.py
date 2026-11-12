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
@click.option(
    "--device", default="auto", type=click.Choice(["auto", "cpu", "cuda", "mps"])
)
@click.option("--prepared-dir", type=click.Path(exists=True, path_type=Path))
def evaluate_model(
    training_dir: Path,
    n_workers: int,
    batch_size: int,
    device: str,
    prepared_dir: Path | None,
):
    """Evaluate saved prepared simulations with equal weight per simulation."""
    run(training_dir, n_workers, batch_size, device, prepared_dir)
