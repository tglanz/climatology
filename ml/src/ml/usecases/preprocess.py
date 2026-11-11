"""Write split arrays using the shared simulation contract and actual coordinates."""

from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
import json
import logging
from pathlib import Path

import h5py
import numpy as np
from tqdm import tqdm

from ml.config import load as load_config
from ml.data.climatology import diagnostic_for
from ml.data.metadata import DataMetadata
from ml.data.simulation_data import try_read_simulation
from ml.data.splits import Splits

log = logging.getLogger(__name__)


def _extract_pairs(
    exp_dirs: list[Path],
    config_path: Path,
    output_path: Path,
    n_workers: int,
    metadata: DataMetadata | None = None,
) -> tuple[DataMetadata | None, int]:
    cfg = load_config(config_path)
    if n_workers < 0:
        raise ValueError("worker count must be nonnegative")
    paths = sorted(exp_dirs)
    executor = ProcessPoolExecutor(max_workers=n_workers) if n_workers else None
    results = (
        executor.map(try_read_simulation, paths, repeat(cfg.data))
        if executor
        else (try_read_simulation(path, cfg.data) for path in paths)
    )
    written, exclusions = 0, []
    simulation_paths, simulation_targets = [], []
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with h5py.File(output_path, "x") as handle:
            xs = ys = None
            for outcome in tqdm(results, total=len(paths), desc=output_path.stem):
                samples = outcome.samples
                if samples is None:
                    exclusions.append(
                        {"simulation": str(outcome.sim_dir), "reason": outcome.reason}
                    )
                    log.warning("excluded %s: %s", outcome.sim_dir, outcome.reason)
                    continue
                if metadata is None:
                    metadata = samples.metadata
                if not metadata.matches(samples.metadata):
                    raise ValueError(
                        "sample coordinates or settings differ across simulations"
                    )
                if xs is None:
                    xs = handle.create_dataset(
                        "x",
                        shape=(0, *samples.x_windows.shape[1:]),
                        maxshape=(None, *samples.x_windows.shape[1:]),
                        dtype="float32",
                    )
                    ys = handle.create_dataset(
                        "y",
                        shape=(0, *samples.y_windows.shape[1:]),
                        maxshape=(None, *samples.y_windows.shape[1:]),
                        dtype="float32",
                    )
                n = len(samples.x_windows)
                xs.resize(written + n, axis=0)
                ys.resize(written + n, axis=0)
                xs[written : written + n], ys[written : written + n] = (
                    samples.x_windows,
                    samples.y_windows,
                )
                written += n
                simulation_paths.append(str(samples.sim_dir))
                simulation_targets.append(samples.truth_profile)
            if metadata is not None:
                metadata.write_hdf5(handle)
                if xs is None:
                    height, width = metadata.grid.shape
                    handle.create_dataset(
                        "x",
                        shape=(0, metadata.input_channels, height, width),
                        dtype="float32",
                    )
                    handle.create_dataset(
                        "y", shape=(0, len(metadata.y_vars), height), dtype="float32"
                    )
                height, _ = metadata.grid.shape
                targets = (
                    np.stack(simulation_targets)
                    if simulation_targets
                    else np.empty((0, len(metadata.y_vars), height), dtype=np.float32)
                )
                handle.create_dataset("simulation_targets", data=targets)
                handle.create_dataset(
                    "simulation_paths",
                    data=simulation_paths,
                    dtype=h5py.string_dtype("utf-8"),
                )
                handle["y"].attrs["vars"] = list(metadata.y_vars)
                handle["y"].attrs["units"] = [
                    diagnostic_for(v).units for v in metadata.y_vars
                ]
                handle["y"].attrs["kind"] = "finite-run climatology"
            handle.attrs["exclusions"] = json.dumps(exclusions)
            handle.attrs["simulations_requested"] = len(paths)
            handle.attrs["simulations_loaded"] = len(paths) - len(exclusions)
    finally:
        if executor is not None:
            executor.shutdown(wait=True, cancel_futures=True)
    log.info("wrote %d pairs to %s", written, output_path)
    return metadata, written


def run(config_path: Path, split_path: Path, n_workers: int = 0) -> None:
    cfg = load_config(config_path)
    if n_workers < 0:
        raise ValueError("worker count must be nonnegative")
    splits = Splits.load(split_path)
    splits.validate()
    out_dir = cfg.paths.preprocessed_dir
    if any(
        (out_dir / name).exists()
        for name in ("train.h5", "val.h5", "test.h5", "splits.json")
    ):
        raise FileExistsError("prepared output exists; choose a fresh preprocessed_dir")
    metadata, count = _extract_pairs(
        splits.train, config_path, out_dir / "train.h5", n_workers
    )
    if count == 0:
        raise ValueError(
            "no usable training samples; inspect train.h5 exclusion reasons"
        )
    _extract_pairs(
        splits.validation, config_path, out_dir / "val.h5", n_workers, metadata
    )
    _extract_pairs(splits.test, config_path, out_dir / "test.h5", n_workers, metadata)
    splits.save(out_dir, "splits", "Prepared simulation assignments", cfg.data.split)
