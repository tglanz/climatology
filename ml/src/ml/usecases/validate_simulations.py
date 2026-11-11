from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from tqdm import tqdm

from ml.config import load as load_config
from ml.data.simulation_data import open_simulation, select_samples
from ml.data.isca_preprocessing import list_simulation_dirs, list_segment_files


@dataclass
class SimResult:
    sim_dir: Path
    n_runs: int
    n_samples: int
    valid: bool
    reason: str


def _validate_one(
    sim_dir: Path,
    config_path: Path,
    validate_spinup: bool,
    validate_convergence: bool,
    validate_climatology: bool,
) -> SimResult:
    cfg = load_config(config_path)
    n_runs = len(list_segment_files(sim_dir, cfg.data))
    n_samples = 0
    try:
        with open_simulation(sim_dir, cfg.data) as source:
            n_samples = source.length
            if n_samples < cfg.data.windows.length:
                raise ValueError("timeline is shorter than one input window")
            if validate_spinup or validate_convergence or validate_climatology:
                select_samples(source, cfg.data)
        return SimResult(sim_dir, n_runs, n_samples, True, "")
    except (ValueError, OSError, KeyError) as exc:
        return SimResult(sim_dir, n_runs, n_samples, False, str(exc))


def run(
    config_path: Path,
    should_validate_spinup: bool = False,
    should_validate_convergence: bool = False,
    should_validate_climatology: bool = False,
    invalid_only: bool = False,
    workers: int = 8,
) -> int:
    """Returns the number of invalid simulations."""
    if workers < 0:
        raise ValueError("worker count must be nonnegative")
    cfg = load_config(config_path)
    sim_dirs = list_simulation_dirs(cfg.data, cfg.paths.experiment_dir)
    n_invalid = 0

    if workers == 0:
        results = (
            _validate_one(
                sim_dir,
                config_path,
                should_validate_spinup,
                should_validate_convergence,
                should_validate_climatology,
            )
            for sim_dir in sim_dirs
        )
    else:
        executor = ProcessPoolExecutor(max_workers=workers)
        futures = {
            executor.submit(
                _validate_one,
                sim_dir,
                config_path,
                should_validate_spinup,
                should_validate_convergence,
                should_validate_climatology,
            ): sim_dir
            for sim_dir in sim_dirs
        }
        results = (f.result() for f in as_completed(futures))

    for result in tqdm(results, total=len(sim_dirs)):
        if not result.valid:
            n_invalid += 1

        if invalid_only and result.valid:
            continue

        tqdm.write(
            f"{result.sim_dir} -- "
            f"runs={result.n_runs}; "
            f"samples={result.n_samples}; "
            f"valid={'true' if result.valid else 'false'}; "
            f"invalid_reason={result.reason}"
        )

    if workers != 0:
        executor.shutdown(wait=False)

    return n_invalid
