"""Read-only numerical fingerprints and simulation summaries."""

import hashlib
from pathlib import Path
import h5py
import numpy as np
from ml.config import load as load_config, load_data
from ml.diagnostics.spectra import zonal_power_spectrum
from ml.diagnostics.enstrophy import mean_enstrophy
from ml.services.simulations import summarize_simulations as summarize_source


def summarize_simulations(config_path: Path, segments: int):
    """Collect progress counts and percentages from the simulation directories."""
    cfg = load_data(config_path)
    return summarize_source(
        cfg.simulations, segments, cfg.paths.experiment_dir / "sweep.json"
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
