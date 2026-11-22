"""Preparation adapters for the shared simulation sample contract."""

import logging
from pathlib import Path
import numpy as np

from ml.config import load_data as load_config
from ml.data.simulation_data import try_read_simulation

log = logging.getLogger(__name__)


def process_one_sim(
    sim_dir: Path, config_path: Path
) -> tuple[np.ndarray, np.ndarray] | None:
    cfg = load_config(config_path)
    outcome = try_read_simulation(sim_dir, cfg.data, cfg.simulations.segment_pattern)
    if outcome.samples is None:
        log.warning("excluded %s: %s", sim_dir, outcome.reason)
        return None
    return outcome.samples.x_windows, outcome.samples.y_windows
