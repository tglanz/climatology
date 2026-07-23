from pathlib import Path

import click


@click.group()
def tmp():
    """Temporary / ad-hoc commands."""
    pass


@tmp.command("executive")
@click.argument("sim_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path("output/executive"),
    show_default=True,
)
def executive(sim_dir: Path, output_dir: Path):
    """Generate executive summary plots for a single simulation."""
    from ml.usecases.executive import run
    run(sim_dir, output_dir)
