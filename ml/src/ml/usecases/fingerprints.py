"""Read-only numerical fingerprints and simulation summaries."""

import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
import torch
from ml.config import load as load_config
from ml.data.isca_dataset import load_latitudes
from ml.diagnostics.spatial import cosine_latitude_weights, area_mean, area_l2_norm
from ml.diagnostics.errors import (
    signed_error,
    absolute_error,
    relative_error,
    rms_error,
    relative_l2,
    lat_weighted_relative_l2,
)
from ml.diagnostics.spectra import zonal_power_spectrum
from ml.diagnostics.enstrophy import mean_enstrophy


def summarize_simulations(config_path: Path, segments: int):
    """Collect progress counts and percentages from the simulation directories."""
    cfg = load_config(config_path)
    experiment_dir = cfg.paths.experiment_dir
    sim_dir = experiment_dir / "simulations"
    sweep_path = experiment_dir / "sweep.json"

    if not sim_dir.exists():
        return dict(exists=False, experiment_dir=experiment_dir, sim_dir=sim_dir)

    total_codes = None
    if sweep_path.exists():
        total_codes = len(json.loads(sweep_path.read_text()))

    by_code: dict[str, list[tuple[str, str, bool]]] = {}
    for d in sim_dir.iterdir():
        parts = d.name.rsplit("-", 1)
        if len(parts) != 2:
            continue
        code, idx = parts
        runs = sorted(
            [x.name for x in d.iterdir() if x.name.startswith("run")], reverse=True
        )
        last = runs[0] if runs else ""
        done = last == f"run{segments:04d}"
        by_code.setdefault(code, []).append((idx, last, done))

    total_sims = sum(len(v) for v in by_code.values())
    done_sims = sum(sum(x[2] for x in v) for v in by_code.values())
    complete_codes = sum(1 for v in by_code.values() if all(x[2] for x in v))

    in_progress = []
    for code, reps in by_code.items():
        for idx, last, done in reps:
            if last and not done:
                pct = int(last[3:]) / segments * 100
                in_progress.append((f"{code}-{idx}", last, pct))
    in_progress.sort(key=lambda x: -x[2])

    return dict(
        exists=True,
        experiment_dir=experiment_dir,
        sim_dir=sim_dir,
        total_codes=total_codes,
        total_sims=total_sims,
        done_sims=done_sims,
        complete_codes=complete_codes,
        in_progress=in_progress,
        not_started=(total_codes - len(by_code)) if total_codes else 0,
    )


def preprocess_fingerprint(config_path: Path):
    """
    Collect content fingerprints of preprocessed train/val/test HDF5 files.
    """
    cfg = load_config(config_path)
    base = cfg.paths.preprocessed_dir
    out: dict = {}
    for split in ("train", "val", "test"):
        h5_path = base / f"{split}.h5"
        if not h5_path.exists():
            out[split] = None
            continue
        with h5py.File(h5_path, "r") as f:
            x = f["x"][:]
            y = f["y"][:]
        x_hash = hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
        y_hash = hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest()
        info = {
            "n_pairs": int(x.shape[0]),
            "x_shape": list(x.shape),
            "y_shape": list(y.shape),
            "x_dtype": str(x.dtype),
            "y_dtype": str(y.dtype),
            "x_sha256": x_hash,
            "y_sha256": y_hash,
            "x0_sum": float(x[0].sum()) if x.shape[0] > 0 else None,
            "x0_mean": float(x[0].mean()) if x.shape[0] > 0 else None,
            "x0_std": float(x[0].std()) if x.shape[0] > 0 else None,
            "y0_sum": float(y[0].sum()) if y.shape[0] > 0 else None,
            "y0_mean": float(y[0].mean()) if y.shape[0] > 0 else None,
            "y0_std": float(y[0].std()) if y.shape[0] > 0 else None,
        }
        out[split] = info
    return base, out


def diagnostic_fingerprint(config_path: Path):
    """
    Collect a deterministic dump of every diagnostic primitive
    evaluated on the first batch from val.h5
    """
    cfg = load_config(config_path)

    # Load fixed inputs.
    val_path = cfg.paths.preprocessed_dir / "val.h5"
    assert val_path.exists(), f"val.h5 missing at {val_path}"
    with h5py.File(val_path, "r") as f:
        x = torch.from_numpy(f["x"][:1])  # (1, C_in, H, W)
        y = torch.from_numpy(f["y"][:1])  # (1, C_out, H, W)

    lat = load_latitudes(cfg)
    w_t = cosine_latitude_weights(lat)
    w = w_t.astype(np.float64)

    # Build a deterministic synthetic prediction so we can exercise loss /
    # error / spectrum primitives without needing a trained model.
    # Persistence is the most natural choice: the most recent vor channel.
    K = cfg.data.windows.length
    n_vars = len(cfg.data.x_vars)
    assert "vor" in cfg.data.x_vars, "vor must be in x_vars for this fingerprint"
    vor_t_channel = (K - 1) * n_vars + cfg.data.x_vars.index("vor")
    pred_t = x[:, vor_t_channel : vor_t_channel + 1, :, :]
    pred = pred_t.numpy().astype(np.float64)
    target = y.numpy().astype(np.float64)

    # Preserve the fingerprint's legacy field layout and reduction formulas.

    # Spatial reductions of y[0]
    y0 = target[0, 0]  # (H, W)
    pred0 = pred[0, 0]
    error = signed_error(pred0, y0)
    abs_err = absolute_error(pred0, y0)
    rel_err = relative_error(pred0, y0)

    cos_w = w  # cos-lat weights, mean1
    area_mean_y0 = float(area_mean(y0, lat))
    area_l2_y0 = float(area_l2_norm(y0, lat))

    zonal_mean_y0 = y0.mean(axis=1)

    # Zonal power spectra (rfft along longitude, then |.|^2)
    zonal_power_y0 = zonal_power_spectrum(y0)  # (H, W//2+1)
    error_power = zonal_power_spectrum(error)

    # Errors as scalars
    rms = rms_error(pred0, y0)

    # Relative L2 (per sample, here just one sample)
    rel_l2 = relative_l2(pred0, y0)

    # Lat-weighted relative L2 (matches the loss closure formula)
    lat_w_rel_l2 = lat_weighted_relative_l2(pred0, y0, lat)

    # Enstrophy (mean of 0.5 * vor^2, area-weighted)
    enstrophy_y0 = float(mean_enstrophy(y0, lat))

    # First N modes only (so the dump is short and stable across resolutions)
    N_MODES = 8
    out = {
        "x_shape": list(x.shape),
        "y_shape": list(y.shape),
        "lat_n": int(len(lat)),
        "cos_lat_weights": {
            "mean": float(cos_w.mean()),
            "std": float(cos_w.std()),
            "min": float(cos_w.min()),
            "max": float(cos_w.max()),
        },
        "area_mean_y0": area_mean_y0,
        "area_l2_y0": area_l2_y0,
        "zonal_mean_y0": {
            "mean": float(zonal_mean_y0.mean()),
            "std": float(zonal_mean_y0.std()),
        },
        "signed_error": {"mean": float(error.mean()), "std": float(error.std())},
        "absolute_error": {"mean": float(abs_err.mean()), "std": float(abs_err.std())},
        "relative_error": {"mean": float(rel_err.mean())},
        "rms_error": rms,
        "relative_l2": rel_l2,
        "lat_weighted_relative_l2": lat_w_rel_l2,
        "zonal_power_signal_first_modes": [
            float(zonal_power_y0.mean(axis=0)[k])
            for k in range(min(N_MODES, zonal_power_y0.shape[-1]))
        ],
        "zonal_power_error_first_modes": [
            float(error_power.mean(axis=0)[k])
            for k in range(min(N_MODES, error_power.shape[-1]))
        ],
        "mean_enstrophy_y0": enstrophy_y0,
    }
    return out
