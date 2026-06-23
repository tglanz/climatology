from pathlib import Path

import click

from ml.config import load as load_config
from ml.common.logging import setup_logging


@click.group()
def data():
    """Data analysis commands."""
    pass


@data.command("climatology-analysis")
@click.option("-c", "--config", "config_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--workers", default=0, show_default=True, help="Parallel worker processes. 0 = serial.")
def climatology_analysis(config_path: Path, workers: int):
    """Within-config climatology variance analysis and noise floor estimate."""
    from ml.usecases.climatology_analysis import run
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    run(config_path, n_workers=workers)
