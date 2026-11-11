import json
from datetime import datetime
from pathlib import Path

import click
import torch
from rich.console import Console
from rich.table import Table

from ml.config import load as load_config, LossKind
from ml.data.isca_dataset import make_loaders, load_grid
from ml.training.model import model_parameter_counts
from ml.training.loss import create_loss_fn
from ml.training import baselines
from ml.diagnostics.grid import gaussian_latitude_weights
from ml.training.info import TrainingSummary, list_training_summaries


@click.group()
def util():
    """Utility commands."""
    pass


@util.command("model-info")
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def model_info(config_path: Path):
    """Print model architecture summary and parameter counts."""
    cfg = load_config(config_path)
    counts = model_parameter_counts(
        cfg.model, dropout=cfg.training.regularization.dropout
    )
    total, trainable = counts.total, counts.trainable

    sub = cfg.model.active_sub_config()
    print(f"architecture:    {cfg.model.architecture}")
    print(f"n_modes:         {sub.n_modes}")
    print(f"hidden_channels: {sub.hidden_channels}")
    print(f"n_layers:        {sub.n_layers}")
    print(f"in_channels:     {sub.in_channels}")
    print(f"out_channels:    {sub.out_channels}")
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
        n_sims = len(manifest.get("validation" if split == "val" else split, []))
        h5 = preprocessed_dir / f"{split}.h5"
        if h5.exists():
            with h5py.File(h5, "r") as f:
                n_samples = f["x"].shape[0]
            ratio = total / n_samples if n_samples > 0 else float("inf")
            print(
                f"{split:5}  {n_sims:4} sims  {n_samples:6,} samples  {ratio:.0f} params/sample"
            )


@util.group("baseline-score")
def baseline_score():
    """
    Compute no-model baseline scores on the val set.

    """
    pass


def _make_loss_fn(cfg):
    lat_weights = None
    if cfg.training.loss == LossKind.LAT_WEIGHTED_RELATIVE_L2:
        lat_weights = torch.from_numpy(
            gaussian_latitude_weights(load_grid(cfg).latitudes)
        )
    return create_loss_fn(cfg.training.loss, lat_weights=lat_weights)


def _baseline_options(fn):
    fn = click.option(
        "-c",
        "--config",
        "config_path",
        required=True,
        type=click.Path(exists=True, path_type=Path),
    )(fn)
    fn = click.option(
        "--workers", default=0, show_default=True, help="DataLoader worker processes."
    )(fn)
    return fn


def _print_baseline_scores(cfg, val_loader, simulation_targets):
    from ml.data.climatology import diagnostic_for

    loss_fn = _make_loss_fn(cfg)
    records = []
    for index, name in enumerate(cfg.data.y_vars):
        target = diagnostic_for(name)
        score = (
            baselines.score_zero(val_loader, loss_fn, index)
            if simulation_targets is None
            else baselines.score_mean(simulation_targets, val_loader, loss_fn, index)
        )
        records.append(
            {
                "target": name,
                "score": score,
                "score_units": (
                    f"({target.units})^2" if cfg.training.loss == LossKind.MSE else "1"
                ),
            }
        )
    print(
        json.dumps(
            {
                "loss_fn": cfg.training.loss,
                "coordinate_space": "physical targets",
                "scoring_population": "validation windows",
                "mean_predictor_population": (
                    "training simulations" if simulation_targets is not None else None
                ),
                "val_samples": len(val_loader.dataset),
                "targets": records,
            },
            indent=2,
            allow_nan=False,
        )
    )


@baseline_score.command("zero")
@_baseline_options
def baseline_zero(config_path: Path, workers: int):
    """Predict zero for every sample."""
    cfg = load_config(config_path)
    _, val_loader, _ = make_loaders(cfg, num_workers=workers)
    assert val_loader is not None, "val split is empty"
    _print_baseline_scores(cfg, val_loader, None)


@baseline_score.command("mean")
@_baseline_options
def baseline_mean(config_path: Path, workers: int):
    """Predict the training-set mean for every sample."""
    cfg = load_config(config_path)
    train_loader, val_loader, _ = make_loaders(cfg, num_workers=workers)
    assert val_loader is not None, "val split is empty"
    _print_baseline_scores(cfg, val_loader, train_loader.dataset.simulation_targets)


@util.command("summarize-trainings")
@click.option(
    "-d",
    "--experiment-dir",
    "experiment_dir",
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


@util.command("summarize-simulations")
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--segments",
    default=150,
    show_default=True,
    help="Total number of segments per simulation.",
)
def summarize_simulations(config_path: Path, segments: int):
    from ml.usecases.fingerprints import summarize_simulations as collect

    summary = collect(config_path, segments)
    if not summary["exists"]:
        print(f"no simulations directory at {summary['sim_dir']}")
        return
    experiment_dir = summary["experiment_dir"]
    total_sims, done_sims = summary["total_sims"], summary["done_sims"]
    total_codes, complete_codes = summary["total_codes"], summary["complete_codes"]
    not_started, in_progress = summary["not_started"], summary["in_progress"]
    codes_str = (
        f"{complete_codes}/{total_codes}" if total_codes else str(complete_codes)
    )
    print(f"experiment:  {experiment_dir.name}")
    print(f"sims done:   {done_sims}/{total_sims}")
    print(f"codes done:  {codes_str}  (all replicates complete)")
    if total_codes:
        print(f"not started: {not_started}")

    if in_progress:
        print()
        print("in progress:")
        bar_width = 20
        for name, last, pct in in_progress:
            filled = int(bar_width * pct / 100)
            bar = "#" * filled + "." * (bar_width - filled)
            print(f"  {name:<16}  {last}  [{bar}]  {pct:5.1f}%")


@util.command("preprocess-fingerprint")
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def preprocess_fingerprint(config_path: Path):
    from ml.usecases.fingerprints import preprocess_fingerprint as collect

    base, results = collect(config_path)
    print(f"preprocessed_dir: {base}")
    for split, info in results.items():
        if info is None:
            print(f"{split}: missing")
            continue
        print(f"{split}:")
        for key, value in info.items():
            print(f"  {key}: {value}")


@util.command("diagnostic-fingerprint")
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def diagnostic_fingerprint(config_path: Path):
    from ml.usecases.fingerprints import diagnostic_fingerprint as collect

    print(json.dumps(collect(config_path), indent=2))
