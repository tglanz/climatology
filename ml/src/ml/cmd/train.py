import logging
import shutil
from pathlib import Path

import click
import torch

from ml.config import load as load_config
from ml.common.logging import setup_logging
from ml.data.climatology import is_climatology_var
from ml.training.model import build_model

from ml.diagnostics.spatial import cosine_latitude_weights

from ml.data.isca_dataset import make_loaders, load_latitudes
from ml.training.trainer import Trainer
from ml.training.info import rotate_training_dir


@click.command()
@click.option("-c", "--config", "config_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--track-metrics", is_flag=True, default=False, help="Write spatial error, zonal mean, and power spectrum after each epoch.")
@click.option("--workers", default=0, show_default=True, help="DataLoader worker processes.")
def train(config_path: Path, track_metrics: bool, workers: int):
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    log = logging.getLogger(__name__)

    rotated = rotate_training_dir(cfg.paths.training_dir)
    if rotated is not None:
        log.info("rotated previous training to %s", rotated)

    cfg.paths.training_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(config_path, cfg.paths.training_dir / "config.toml")
    splits_src = cfg.paths.preprocessed_dir / "splits.json"
    assert splits_src.exists(), f"splits.json not found in preprocessed dir: {splits_src}"
    shutil.copy2(splits_src, cfg.paths.training_dir / "splits.json")

    clim_target = all(is_climatology_var(v) for v in cfg.data.y_vars)
    model = build_model(cfg.model, dropout=cfg.training.regularization.dropout, zonal_mean=clim_target)
    train_loader, val_loader, _ = make_loaders(cfg, num_workers=workers)

    lat_weights = None
    if cfg.training.loss == "lat_weighted_relative_l2":
        latitudes = load_latitudes(cfg)
        lat_weights = torch.from_numpy(cosine_latitude_weights(latitudes)).float()

    Trainer(model, cfg, lat_weights=lat_weights).fit(
        train_loader, val_loader, track_metrics=track_metrics
    )
