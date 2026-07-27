from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from tqdm import tqdm

from ml.config import load as load_config
from ml.data.climatology import nc_var_for, resolve_window
from ml.diagnostics.convergence import find_zonal_mean_convergence_time
from ml.diagnostics.enstrophy import mean_enstrophy
from ml.diagnostics.spinup import find_spinup_time
from ml.data.isca_segment import read_segment, validate_segment, aggregated_read_field
from ml.data.isca_preprocessing import CONVERGENCE_DIAGNOSTIC_VAR, list_simulation_dirs, list_segment_files


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
    K = cfg.data.windows.length
    nc_files = list_segment_files(sim_dir, cfg.data)
    n_runs = len(nc_files)
    n_samples = 0

    if not nc_files:
        return SimResult(sim_dir, n_runs, n_samples, False, "no segments matching segment_pattern")

    segments_cache = {}
    for nc_path in nc_files:
        try:
            segment_samples_count, _ = validate_segment(
                nc_path, cfg.data.x_vars, [], cache=segments_cache)
        except (AssertionError, OSError, ValueError) as e:
            return SimResult(sim_dir, n_runs, n_samples, False, f"{nc_path.name}: {e}")
        n_samples += segment_samples_count

    if n_samples < K + 1:
        return SimResult(sim_dir, n_runs, n_samples, False, f"timeline too short: {n_samples} < {K + 1}")

    t_s: int | None = None
    t_c: int | None = None

    validate_convergence = validate_convergence or validate_climatology
    validate_spinup = validate_spinup or validate_convergence

    if validate_spinup or validate_convergence or validate_climatology:
        lats = read_segment(nc_files[0], cache=segments_cache)["lat"].values

        if cfg.data.spinup is not None:
            vorticities = aggregated_read_field(nc_files, "vor", cache=segments_cache)
            enstrophy = mean_enstrophy(vorticities, lats)
            try:
                t_s = find_spinup_time(
                    diagnostic=enstrophy,
                    stable_time=cfg.data.spinup.stable_time,
                    window_size=cfg.data.spinup.window_size,
                    z_threshold=cfg.data.spinup.z_threshold,
                )
                if validate_spinup and not t_s:
                    raise ValueError(f"unable to infer spinup time with {cfg.data.spinup}")
            except Exception as e:
                return SimResult(sim_dir, n_runs, n_samples, False, str(e))

        if (validate_convergence or validate_climatology) and cfg.data.convergence is not None:
            u_full = aggregated_read_field(nc_files, CONVERGENCE_DIAGNOSTIC_VAR, cache=segments_cache)
            try:
                t_c = find_zonal_mean_convergence_time(
                    u_full,
                    lats,
                    t_s if t_s is not None else 0,
                    threshold=cfg.data.convergence.threshold,
                    hold=cfg.data.convergence.hold,
                )
            except Exception as e:
                return SimResult(sim_dir, n_runs, n_samples, False, f"convergence detection failed: {e}")
            if validate_convergence and t_c is None:
                return SimResult(sim_dir, n_runs, n_samples, False, "convergence not reached")

    if validate_climatology:
        try:
            resolve_window(cfg.data.climatology, t_s, t_c, n_samples)
        except AssertionError as e:
            return SimResult(sim_dir, n_runs, n_samples, False, f"climatology window invalid: {e}")

    return SimResult(sim_dir, n_runs, n_samples, True, "")


def run(
    config_path: Path,
    should_validate_spinup: bool = False,
    should_validate_convergence: bool = False,
    should_validate_climatology: bool = False,
    invalid_only: bool = False,
    workers: int = 8,
) -> int:
    """Returns the number of invalid simulations."""
    cfg = load_config(config_path)
    sim_dirs = list_simulation_dirs(cfg.data)
    n_invalid = 0

    if workers == 0:
        results = (
            _validate_one(sim_dir, config_path, should_validate_spinup, should_validate_convergence, should_validate_climatology)
            for sim_dir in sim_dirs
        )
    else:
        executor = ProcessPoolExecutor(max_workers=workers)
        futures = {
            executor.submit(_validate_one, sim_dir, config_path, should_validate_spinup, should_validate_convergence, should_validate_climatology): sim_dir
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
