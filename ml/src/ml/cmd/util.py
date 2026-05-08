from pathlib import Path

import click
import torch

from ml.config import load as load_config
from ml.isca_dataset import make_loaders
from ml.model import build_model
from ml.training import create_loss_fn


@click.group()
def util():
    """Utility commands."""
    pass


@util.command("model-info")
@click.option(
    "-c", "--config", "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def model_info(config_path: Path):
    """Print model architecture summary and parameter counts."""
    cfg = load_config(config_path)
    model = build_model(cfg.model.fno)

    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)

    fno = cfg.model.fno
    print(f"architecture:    FNO")
    print(f"n_modes:         {fno.n_modes}")
    print(f"hidden_channels: {fno.hidden_channels}")
    print(f"n_layers:        {fno.n_layers}")
    print(f"in_channels:     {fno.in_channels}")
    print(f"out_channels:    {fno.out_channels}")
    print(f"total params:    {total:,}")
    print(f"trainable:       {trainable:,}")

    import json, h5py
    preprocessed_dir = cfg.paths.preprocessed_dir
    manifest_path = preprocessed_dir / "splits.json"
    manifest = {}
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)

    print()
    for split in ("train", "val", "test"):
        n_sims = len(manifest.get(split, []))
        h5 = preprocessed_dir / f"{split}.h5"
        if h5.exists():
            with h5py.File(h5, "r") as f:
                n_samples = f["x"].shape[0]
            ratio = total / n_samples if n_samples > 0 else float("inf")
            print(f"{split:5}  {n_sims:4} sims  {n_samples:6,} samples  {ratio:.0f} params/sample")


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
