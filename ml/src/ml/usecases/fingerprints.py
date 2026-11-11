"""Read-only numerical fingerprints and simulation summaries."""

import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
from ml.config import load as load_config
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
    """Diagnostic values for one prepared target and a same-unit perturbation."""
    from dataclasses import asdict
    from ml.data.metadata import DataMetadata
    from ml.data.climatology import diagnostic_for
    from ml.diagnostics.errors import (
        ScoreSummary,
        profile_relative_l2_values,
        profile_rmse,
    )

    cfg = load_config(config_path)
    with h5py.File(cfg.paths.preprocessed_dir / "val.h5", "r") as handle:
        metadata = DataMetadata.read_hdf5(handle)
        metadata.validate_config(cfg.data)
        if len(handle["y"]) == 0:
            raise ValueError("validation split has no diagnostic samples")
        target = handle["y"][0].astype(np.float64)
        x = handle["x"][0]
    lat = metadata.grid.latitudes
    prediction = target * 1.1
    result = {"metadata": metadata.to_dict(), "targets": {}}
    for index, name in enumerate(metadata.y_vars):
        diagnostic = diagnostic_for(name)
        relative = ScoreSummary.from_values(
            profile_relative_l2_values(prediction[index], target[index], lat)
        )
        result["targets"][name] = {
            "units": diagnostic.units,
            "area_mean": float(metadata.grid.weights @ target[index]),
            "rmse": profile_rmse(prediction[index], target[index], lat),
            "relative_l2": asdict(relative),
        }
    if "vor" in metadata.x_vars:
        index = (metadata.data_config["windows"]["length"] - 1) * len(
            metadata.x_vars
        ) + metadata.x_vars.index("vor")
        result["last_input_vorticity"] = {
            "mean_enstrophy": float(mean_enstrophy(x[index], lat)),
            "raw_zonal_fourier_power": zonal_power_spectrum(x[index])
            .mean(0)[:8]
            .tolist(),
        }
    return result
