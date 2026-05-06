from pathlib import Path

import click

from ml.config import load as load_config
from ml.common.logging import setup_logging
from ml.model import build_model
from ml.training import Trainer
from ml.isca_dataset import make_loaders


@click.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def train(config_path: Path):
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    model = build_model(cfg.model.fno)
    train_loader, val_loader, _ = make_loaders(cfg)
    Trainer(model, cfg).fit(train_loader, val_loader)
