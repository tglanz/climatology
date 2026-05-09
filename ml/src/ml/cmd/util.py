import hashlib
import json
from datetime import datetime
from pathlib import Path

import click
import h5py
import numpy as np
import torch
from rich.console import Console
from rich.table import Table

from ml.config import load as load_config
from ml.data.isca_dataset import make_loaders, load_latitudes
from ml.diagnostics import persistence_prediction
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
    K = cfg.data.windows.input_length
    n_vars = len(cfg.data.x_vars)
    vor_t_channel = (K - 1) * n_vars + cfg.data.x_vars.index("vor")

    persistence_total = 0.0
    zero_total = 0.0
    n = 0

    with torch.no_grad():
        for x, y in val_loader:
            persistence_pred = persistence_prediction(x, vor_t_channel)
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


@util.command("preprocess-fingerprint")
@click.option(
    "-c", "--config", "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def preprocess_fingerprint(config_path: Path):
    """
    Print a stable, content-only fingerprint of preprocessed train/val/test
    HDF5 files. Hashing the HDF5 files directly is unreliable because HDF5
    stores creation timestamps and chunk metadata; we hash the dataset
    arrays themselves instead. Use this to compare preprocessing output
    across refactors that should leave the data unchanged.
    """
    cfg = load_config(config_path)
    base = cfg.paths.preprocessed_dir
    print(f"preprocessed_dir: {base}")
    out: dict = {}
    for split in ("train", "val", "test"):
        h5_path = base / f"{split}.h5"
        if not h5_path.exists():
            print(f"{split}: missing")
            continue
        with h5py.File(h5_path, "r") as f:
            x = f["x"][:]
            y = f["y"][:]
        x_hash = hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
        y_hash = hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest()
        info = {
            "n_pairs":  int(x.shape[0]),
            "x_shape":  list(x.shape),
            "y_shape":  list(y.shape),
            "x_dtype":  str(x.dtype),
            "y_dtype":  str(y.dtype),
            "x_sha256": x_hash,
            "y_sha256": y_hash,
            "x0_sum":   float(x[0].sum()) if x.shape[0] > 0 else None,
            "x0_mean":  float(x[0].mean()) if x.shape[0] > 0 else None,
            "x0_std":   float(x[0].std()) if x.shape[0] > 0 else None,
            "y0_sum":   float(y[0].sum()) if y.shape[0] > 0 else None,
            "y0_mean":  float(y[0].mean()) if y.shape[0] > 0 else None,
            "y0_std":   float(y[0].std()) if y.shape[0] > 0 else None,
        }
        out[split] = info
        print(f"{split}:")
        for k, v in info.items():
            print(f"  {k}: {v}")


@util.command("diagnostic-fingerprint")
@click.option(
    "-c", "--config", "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def diagnostic_fingerprint(config_path: Path):
    """
    Print a JSON-shaped, deterministic dump of every diagnostic primitive
    evaluated on the first batch from val.h5. Used to verify that a
    refactor of the diagnostic computations leaves their numerical outputs
    unchanged.

    Operates without the trainer's seed (the trainer is not seeded today),
    by reading val.h5 directly and constructing predictions and weights
    from fixed inputs only.
    """
    cfg = load_config(config_path)

    # Load fixed inputs.
    val_path = cfg.paths.preprocessed_dir / "val.h5"
    assert val_path.exists(), f"val.h5 missing at {val_path}"
    with h5py.File(val_path, "r") as f:
        x = torch.from_numpy(f["x"][:1])  # (1, C_in, H, W)
        y = torch.from_numpy(f["y"][:1])  # (1, C_out, H, W)

    lat = load_latitudes(cfg)
    w_t = _cosine_lat_weights(lat)
    w = w_t.numpy().astype(np.float64)

    # Build a deterministic synthetic prediction so we can exercise loss /
    # error / spectrum primitives without needing a trained model.
    # Persistence is the most natural choice: the most recent vor channel.
    K = cfg.data.windows.input_length
    n_vars = len(cfg.data.x_vars)
    assert "vor" in cfg.data.x_vars, "vor must be in x_vars for this fingerprint"
    vor_t_channel = (K - 1) * n_vars + cfg.data.x_vars.index("vor")
    pred_t = x[:, vor_t_channel : vor_t_channel + 1, :, :]
    pred = pred_t.numpy().astype(np.float64)
    target = y.numpy().astype(np.float64)

    # Compute each diagnostic. Mirror the existing inline implementations
    # so this fingerprint is meaningful before the diagnostics module is
    # introduced; the implementations that move into ml.diagnostics must
    # produce the same numbers afterward.

    # Spatial reductions of y[0]
    y0 = target[0, 0]  # (H, W)
    pred0 = pred[0, 0]
    error = pred0 - y0
    abs_err = np.abs(error)
    rel_err = abs_err / (np.abs(y0) + 1e-12)

    cos_w = w  # cos-lat weights, mean1
    weighted = y0 * cos_w[:, None]
    area_mean_y0 = float(weighted.mean())
    area_l2_y0 = float(np.sqrt((y0 ** 2 * cos_w[:, None]).mean()))

    zonal_mean_y0 = y0.mean(axis=1)

    # Zonal power spectra (rfft along longitude, then |.|^2)
    zonal_power_y0 = np.abs(np.fft.rfft(y0, axis=-1)) ** 2  # (H, W//2+1)
    error_power = np.abs(np.fft.rfft(error, axis=-1)) ** 2
    signal_power = zonal_power_y0  # same definition for "signal"

    # Errors as scalars
    rms = float(np.sqrt((error ** 2).mean()))

    # Relative L2 (per sample, here just one sample)
    num = np.linalg.norm(error)
    den = np.linalg.norm(y0)
    rel_l2 = float(num / (den + 1e-12))

    # Lat-weighted relative L2 (matches the loss closure formula)
    num_w = np.sqrt((error ** 2 * cos_w[:, None]).sum())
    den_w = np.sqrt((y0 ** 2 * cos_w[:, None]).sum())
    lat_w_rel_l2 = float(num_w / (den_w + 1e-12))

    # Enstrophy (mean of 0.5 * vor^2, area-weighted)
    enstrophy_y0 = float(0.5 * (y0 ** 2 * cos_w[:, None]).mean())

    # First N modes only (so the dump is short and stable across resolutions)
    N_MODES = 8
    out = {
        "x_shape":  list(x.shape),
        "y_shape":  list(y.shape),
        "lat_n":    int(len(lat)),
        "cos_lat_weights": {
            "mean": float(cos_w.mean()),
            "std":  float(cos_w.std()),
            "min":  float(cos_w.min()),
            "max":  float(cos_w.max()),
        },
        "area_mean_y0":  area_mean_y0,
        "area_l2_y0":    area_l2_y0,
        "zonal_mean_y0": {
            "mean": float(zonal_mean_y0.mean()),
            "std":  float(zonal_mean_y0.std()),
        },
        "signed_error":   {"mean": float(error.mean()),   "std": float(error.std())},
        "absolute_error": {"mean": float(abs_err.mean()), "std": float(abs_err.std())},
        "relative_error": {"mean": float(rel_err.mean())},
        "rms_error":   rms,
        "relative_l2": rel_l2,
        "lat_weighted_relative_l2": lat_w_rel_l2,
        "zonal_power_signal_first_modes": [
            float(zonal_power_y0.mean(axis=0)[k]) for k in range(min(N_MODES, zonal_power_y0.shape[-1]))
        ],
        "zonal_power_error_first_modes": [
            float(error_power.mean(axis=0)[k]) for k in range(min(N_MODES, error_power.shape[-1]))
        ],
        "mean_enstrophy_y0": enstrophy_y0,
    }
    print(json.dumps(out, indent=2))
