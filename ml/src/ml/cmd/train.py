import logging
import shutil
from pathlib import Path

import click

from ml.config import load as load_config
from ml.common.logging import setup_logging
from ml.model import build_model
from ml.training import Trainer, _cosine_lat_weights
from ml.isca_dataset import make_loaders, load_latitudes
from ml.training_info import rotate_training_dir


@click.command()
@click.option("-c", "--config", "config_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--track-metrics", is_flag=True, default=False, help="Write spatial error, zonal mean, and power spectrum after each epoch.")
def train(config_path: Path, track_metrics: bool):
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    log = logging.getLogger(__name__)

    # rotate any existing training_dir to <name>-<N> so the canonical
    # training_dir always points at the most recent run
    rotated = rotate_training_dir(cfg.paths.training_dir)
    if rotated is not None:
        log.info("rotated previous training to %s", rotated)

    # snapshot the config alongside the training artifacts so the run is
    # self-documenting; copy before constructing model/trainer so that any
    # later failure still leaves the config in place
    cfg.paths.training_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(config_path, cfg.paths.training_dir / "config.toml")

    model = build_model(cfg.model.fno, dropout=cfg.training.regularization.dropout)
    train_loader, val_loader, _ = make_loaders(cfg)

    lat_weights = None
    if cfg.training.loss == "lat_weighted_relative_l2":
        latitudes = load_latitudes(cfg)
        lat_weights = _cosine_lat_weights(latitudes)

    Trainer(model, cfg, lat_weights=lat_weights).fit(
        train_loader, val_loader, track_metrics=track_metrics
    )
