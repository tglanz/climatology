import logging
from pathlib import Path

import click

from ml.config import Config, LoggingConfig, load as load_config
from ml.model import build_model
from ml.training import Trainer
from ml.isca_dataset import make_loaders


def setup_logging(cfg: LoggingConfig):
    handlers = []
    if cfg.stdout:
        handlers.append(logging.StreamHandler())
    if cfg.output_file:
        cfg.output_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(cfg.output_file))
    logging.basicConfig(level=cfg.level, handlers=handlers,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s")


@click.group()
def cli():
    pass


@cli.command()
@click.option("-c", "--config", "config_path", required=True, type=click.Path(exists=True, path_type=Path))
def train(config_path: Path):
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    model = build_model(cfg.model.fno)
    train_loader, val_loader, _ = make_loaders(cfg)
    Trainer(model, cfg).fit(train_loader, val_loader)


if __name__ == "__main__":
    cli()
