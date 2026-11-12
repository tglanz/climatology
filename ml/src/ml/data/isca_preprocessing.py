"""Preparation adapters for the shared simulation sample contract."""

import logging
from pathlib import Path
import numpy as np

from ml.config import IscaDataConfig, load_data as load_config
from ml.data.simulation_data import list_segment_files, try_read_simulation

log = logging.getLogger(__name__)


def sort_simulation_dirs(exp_dirs: list[Path]) -> list[Path]:
    return sorted(exp_dirs, key=lambda p: p.name)


def list_simulation_dirs(
    cfg: IscaDataConfig, experiment_dir: Path, should_sort: bool = True
) -> list[Path]:
    sim_dirs = [p for p in experiment_dir.glob(cfg.simulation_pattern) if p.is_dir()]
    if not sim_dirs:
        raise ValueError(
            f"no simulations found: {experiment_dir}/{cfg.simulation_pattern}"
        )
    return sort_simulation_dirs(sim_dirs) if should_sort else sim_dirs


def process_one_sim(
    exp_dir: Path, config_path: Path
) -> tuple[np.ndarray, np.ndarray] | None:
    outcome = try_read_simulation(exp_dir, load_config(config_path).data)
    if outcome.samples is None:
        log.warning("excluded %s: %s", exp_dir, outcome.reason)
        return None
    return outcome.samples.x_windows, outcome.samples.y_windows
