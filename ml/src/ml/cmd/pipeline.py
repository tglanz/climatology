"""Stage orchestration; science stays in the existing stage owners."""

from pathlib import Path
import click

from ml.config import load_data
from ml.cmd.train import train


@click.group()
def pipeline():
    """Prepare once, train into a fresh run, and evaluate saved inputs."""


@pipeline.command("prepare")
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option("--split", "split_path", type=click.Path(exists=True, path_type=Path))
@click.option("--workers", default=0, type=click.IntRange(min=0), show_default=True)
def prepare(config_path, split_path, workers):
    """Generate assignments unless supplied, then write one prepared artifact."""
    from ml.usecases.generate_splits import run as generate
    from ml.usecases.preprocess import run

    cfg = load_data(config_path)
    if cfg.paths.preprocessed_dir.exists():
        raise click.ClickException(
            "prepared directory exists; reuse it or choose a fresh path"
        )
    if split_path is None:
        split_path = cfg.paths.splits_dir / "pipeline.json"
        if split_path.exists():
            raise click.ClickException(
                "split already exists; pass it explicitly with --split"
            )
        split_path = generate(
            config_path, "pipeline", "Pipeline configuration assignments"
        )
    run(config_path, split_path, workers)


@pipeline.command("run")
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option("--workers", default=0, type=click.IntRange(min=0), show_default=True)
@click.option(
    "--device", default="auto", type=click.Choice(["auto", "cpu", "cuda", "mps"])
)
@click.pass_context
def run_experiment(ctx, config_path, workers, device):
    """Train on prepared data; evaluate only after successful training."""
    from ml.config import load
    from ml.usecases.evaluate import run

    cfg = load(config_path)
    ctx.invoke(
        train,
        config_path=config_path,
        workers=workers,
        device=device,
        track_metrics=True,
    )
    run(
        cfg.paths.training_dir,
        n_workers=0,
        batch_size=cfg.training.batch_size,
        device=device,
    )


@pipeline.command("example")
@click.option("--directory", required=True, type=click.Path(path_type=Path))
@click.option(
    "--real-root", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
def example(directory, real_root):
    """Create a synthetic smoke recipe or a fixed real-simulation subset recipe."""
    from ml.usecases.pipeline_example import create

    create(directory, real_root)
    click.echo(f"Recipe: {directory / 'prepare.toml'}, {directory / 'run.toml'}")
