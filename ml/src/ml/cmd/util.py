from pathlib import Path

import click
import torch

from ml.config import load as load_config
from ml.isca_dataset import make_loaders
from ml.training import create_loss_fn


@click.group()
def util():
    """Utility commands."""
    pass


@util.command("persistence-score")
@click.option(
    "-c", "--config", "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def persistence_score(config_path: Path):
    """Compute baseline loss scores on the val set (no model required)."""
    cfg = load_config(config_path)
    loss_fn = create_loss_fn(cfg.training.loss)

    _, val_loader, _ = make_loaders(cfg)
    assert val_loader is not None, "val split is empty"

    persistence_total = 0.0
    zero_total = 0.0
    n = 0

    with torch.no_grad():
        for x, y in val_loader:
            persistence_pred = x[:, 0:1, :, :]  # vor(t) as prediction for vor(t+1)
            zero_pred = torch.zeros_like(y)

            persistence_total += loss_fn(persistence_pred, y).item()
            zero_total += loss_fn(zero_pred, y).item()
            n += 1

    print(f"loss:        {cfg.training.loss}")
    print(f"val samples: {len(val_loader.dataset)}")
    print(f"persistence: {persistence_total / n:.4f}  (predict vor(t+1) = vor(t))")
    print(f"zero:        {zero_total / n:.4f}  (predict zero everywhere)")
