from pathlib import Path

import click

from ml.config import load as load_config
from ml.common.logging import setup_logging
from ml.model import build_model
from ml.training import Trainer, _cosine_lat_weights
from ml.isca_dataset import make_loaders, load_latitudes


@click.command()
@click.option("-c", "--config", "config_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--track-metrics", is_flag=True, default=False, help="Write spatial error, zonal mean, and power spectrum after each epoch.")
def train(config_path: Path, track_metrics: bool):
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    model = build_model(cfg.model.fno)
    train_loader, val_loader, _ = make_loaders(cfg)

    lat_weights = None
    if cfg.training.loss == "lat_weighted_relative_l2":
        latitudes = load_latitudes(cfg)
        lat_weights = _cosine_lat_weights(latitudes)

    Trainer(model, cfg, lat_weights=lat_weights).fit(
        train_loader, val_loader, track_metrics=track_metrics
    )
