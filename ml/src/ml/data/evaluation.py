"""Evaluation adapters use the same samples and rejection rules as preparation."""

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import repeat
import logging
from pathlib import Path

from ml.config import IscaDataConfig
from ml.data.simulation_data import (
    SimulationOutcome,
    SimulationSamples,
    try_read_simulation,
)

log = logging.getLogger(__name__)
SimResult = SimulationSamples


@dataclass
class SimulationLoadReport:
    results: list[SimulationSamples]
    excluded: list[SimulationOutcome]


def _load_one_sim(sim_dir: Path, data_cfg: IscaDataConfig) -> SimulationSamples | None:
    outcome = try_read_simulation(sim_dir, data_cfg)
    if outcome.samples is None:
        log.warning("excluded %s: %s", sim_dir, outcome.reason)
    return outcome.samples


def load_all_sims(
    sim_dirs: list[Path],
    data_cfg: IscaDataConfig,
    max_workers: int = 8,
) -> SimulationLoadReport:
    if max_workers < 0:
        raise ValueError("worker count must be nonnegative")
    if max_workers == 0:
        outcomes = [try_read_simulation(path, data_cfg) for path in sim_dirs]
    else:
        with ProcessPoolExecutor(max_workers=max_workers) as pool:
            outcomes = list(pool.map(try_read_simulation, sim_dirs, repeat(data_cfg)))
    report = SimulationLoadReport(
        [o.samples for o in outcomes if o.samples is not None],
        [o for o in outcomes if o.samples is None],
    )
    for outcome in report.excluded:
        log.warning("excluded %s: %s", outcome.sim_dir, outcome.reason)
    return report
