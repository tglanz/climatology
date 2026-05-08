from datetime import datetime
from pathlib import Path

import click
import torch
from rich.console import Console
from rich.table import Table

from ml.config import load as load_config
from ml.isca_dataset import make_loaders, load_latitudes
from ml.model import build_model
from ml.training import create_loss_fn, _cosine_lat_weights
from ml.training_info import TrainingSummary, list_training_summaries


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
    model = build_model(cfg.model.fno, dropout=cfg.training.regularization.dropout)

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
    lat_weights = None
    if cfg.training.loss == "lat_weighted_relative_l2":
        lat_weights = _cosine_lat_weights(load_latitudes(cfg))
    loss_fn = create_loss_fn(cfg.training.loss, lat_weights=lat_weights)

    _, val_loader, _ = make_loaders(cfg)
    assert val_loader is not None, "val split is empty"

    # The most recent vor channel under the lag-stacked input layout
    # (oldest-to-newest, x_vars-major within each timestep).
    assert "vor" in cfg.data.x_vars, (
        f"persistence baseline assumes 'vor' is in x_vars, got {cfg.data.x_vars}"
    )
    K = cfg.data.lag_steps
    n_vars = len(cfg.data.x_vars)
    vor_t_channel = (K - 1) * n_vars + cfg.data.x_vars.index("vor")

    persistence_total = 0.0
    zero_total = 0.0
    n = 0

    with torch.no_grad():
        for x, y in val_loader:
            persistence_pred = x[:, vor_t_channel : vor_t_channel + 1, :, :]
            zero_pred = torch.zeros_like(y)

            persistence_total += loss_fn(persistence_pred, y).item()
            zero_total += loss_fn(zero_pred, y).item()
            n += 1

    print(f"loss:        {cfg.training.loss}")
    print(f"val samples: {len(val_loader.dataset)}")
    print(f"persistence: {persistence_total / n:.4f}  (predict vor(t+1) = vor(t))")
    print(f"zero:        {zero_total / n:.4f}  (predict zero everywhere)")


@util.command("summarize-trainings")
@click.option(
    "-d", "--experiment-dir", "experiment_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Experiment directory containing the training* subdirectories.",
)
@click.option(
    "--limit",
    default=None,
    type=int,
    help="Only show the most recent N training runs.",
)
def summarize_trainings(experiment_dir: Path, limit: int | None):
    """Print a table of past training runs in <experiment-dir>/training* directories."""
    summaries = list_training_summaries(experiment_dir)
    if limit is not None:
        summaries = summaries[:limit]

    if not summaries:
        print(f"no training runs found under {experiment_dir}")
        return

    _print_summary_table(summaries)


def _print_summary_table(summaries: list[TrainingSummary]) -> None:
    console = Console()
    table = Table(show_header=True, header_style="bold")
    table.add_column("name")
    table.add_column("start", style="dim")
    table.add_column("duration", justify="right")
    table.add_column("epochs", justify="right")
    table.add_column("best_val", justify="right")
    table.add_column("@ ep", justify="right")
    table.add_column("final_train", justify="right")
    table.add_column("final_val", justify="right")
    table.add_column("status", justify="center")
    table.add_column("loss")
    table.add_column("opt")
    table.add_column("sched")
    table.add_column("params", justify="right")

    for s in summaries:
        table.add_row(
            s.name,
            _fmt_time(s.start_time),
            _fmt_duration(s.duration_seconds),
            str(s.total_epochs) if s.total_epochs is not None else "-",
            _fmt_loss(s.best_val_loss),
            str(s.best_val_epoch) if s.best_val_epoch is not None else "-",
            _fmt_loss(s.final_train_loss),
            _fmt_loss(s.final_val_loss),
            _fmt_status(s),
            s.loss_kind or "-",
            s.optimizer or "-",
            s.scheduler or "-",
            _fmt_params(s.n_params),
        )
    console.print(table)


def _fmt_time(iso: str | None) -> str:
    if not iso:
        return "-"
    try:
        return datetime.fromisoformat(iso).strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return iso[:16]


def _fmt_duration(seconds: float | None) -> str:
    if seconds is None or seconds <= 0:
        return "-"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    sec = int(seconds % 60)
    if h > 0:
        return f"{h}h{m:02d}m"
    if m > 0:
        return f"{m}m{sec:02d}s"
    return f"{sec}s"


def _fmt_loss(v: float | None) -> str:
    return f"{v:.4f}" if v is not None else "-"


def _fmt_status(s: TrainingSummary) -> str:
    if s.stopped_early is True:
        return "early"
    if s.end_time:
        return "done"
    return "running"


def _fmt_params(n: int | None) -> str:
    if n is None:
        return "-"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)
