from pathlib import Path

import click
import torch

from ml.config import load as load_config, save as save_config
from ml.data.prepared import verify, bind
from ml.common.logging import setup_logging
from ml.training.model import build_model

from ml.data.isca_dataset import make_loaders
from ml.training.trainer import Trainer
from ml.inference import select_device
from ml.data.splits import Splits


@click.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--track-metrics",
    is_flag=True,
    default=False,
    help="Write per-target spatial errors and profile diagnostics after each epoch.",
)
@click.option(
    "--workers", default=0, show_default=True, help="DataLoader worker processes."
)
@click.option(
    "--device", default="auto", type=click.Choice(["auto", "cpu", "cuda", "mps"])
)
def train(config_path: Path, track_metrics: bool, workers: int, device: str):
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    verify(cfg.paths.preprocessed_dir)
    if cfg.paths.training_dir.exists():
        raise FileExistsError("training directory exists; choose a fresh training_dir")

    selected_device = select_device(device)
    torch.manual_seed(cfg.training.seed)
    train_loader, val_loader, _ = make_loaders(cfg, num_workers=workers)
    model = build_model(
        cfg.model,
        train_loader.dataset.metadata.grid,
        dropout=cfg.training.regularization.dropout,
    )

    splits = Splits.load(cfg.paths.preprocessed_dir / "splits.json")
    splits.validate()
    cfg.paths.training_dir.mkdir(parents=True, exist_ok=False)
    save_config(cfg, cfg.paths.training_dir / "config.toml")
    bind(cfg.paths.preprocessed_dir, cfg.paths.training_dir)
    splits.save(
        cfg.paths.training_dir,
        "splits",
        "Training simulation assignments",
        cfg.data.split,
    )
    Trainer(
        model, cfg, device=selected_device, metadata=train_loader.dataset.metadata
    ).fit(train_loader, val_loader, track_metrics=track_metrics)
