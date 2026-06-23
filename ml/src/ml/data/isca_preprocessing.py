import logging
from pathlib import Path

import numpy as np
import xarray as xr

from ml.config import IscaDataConfig, load as load_config
from ml.data.climatology import compute_climatology, is_climatology_var, nc_var_for, resolve_window
from ml.data.isca_segment import aggregated_read_field, read_segment, validate_segment
from ml.data.window_selector import build_selector
from ml.diagnostics import find_spinup_time, find_zonal_mean_convergence_time
from ml.diagnostics.enstrophy import mean_enstrophy

log = logging.getLogger(__name__)

CONVERGENCE_DIAGNOSTIC_VAR = "ucomp"


def sort_simulation_dirs(exp_dirs: list[Path]) -> list[Path]:
    # return list(sorted(exp_dirs, key=lambda p: int(str(p).split("/")[-1])))
    return list(sorted(exp_dirs, key=lambda p: str(p).split("/")[-1]))


def list_simulation_dirs(cfg: IscaDataConfig, should_sort: bool = True) -> list[Path]:
    log.debug("listing simulations from %s/%s", cfg.experiment_dir, cfg.simulation_pattern)
    sim_dirs = list(cfg.experiment_dir.glob(cfg.simulation_pattern))
    assert sim_dirs, f"no simulations found: {cfg.experiment_dir}/{cfg.simulation_pattern}"
    if should_sort:
        sim_dirs = sort_simulation_dirs(sim_dirs)
    return sim_dirs


def list_segment_files(sim_dir: Path, cfg: IscaDataConfig) -> list[Path]:
    return list(sorted(sim_dir.glob(cfg.segment_pattern)))


def process_one_sim(
    exp_dir: Path,
    config_path: Path,
) -> tuple[np.ndarray, np.ndarray] | None:
    """
    Process one simulation directory and return (x, y) window arrays, or None
    if no valid windows exist. Safe to call from a worker process.
    """
    cfg = load_config(config_path)
    data_cfg = cfg.data
    K = data_cfg.windows.length
    selector = build_selector(data_cfg.windows)

    step_y_vars = [v for v in data_cfg.y_vars if not is_climatology_var(v)]
    clim_y_vars = [v for v in data_cfg.y_vars if is_climatology_var(v)]
    is_clim = bool(clim_y_vars)

    nc_files = sorted(exp_dir.glob(data_cfg.segment_pattern))
    if not nc_files:
        log.warning("no NC files in %s", exp_dir)
        return None

    timeline: list[tuple[Path, int]] = []
    spatial_shape: tuple | None = None
    for path in nc_files:
        T, spatial = validate_segment(path, data_cfg.x_vars, step_y_vars)
        if spatial_shape is None:
            spatial_shape = spatial
        timeline.extend((path, t) for t in range(T))

    M = len(timeline)
    t_s: int | None = None
    t_c: int | None = None
    clim_array: np.ndarray | None = None
    ds_cache: dict[Path, xr.Dataset] = {}

    try:
        if data_cfg.spinup is not None:
            lat = read_segment(nc_files[0], ds_cache)["lat"].values
            vor_full = aggregated_read_field(nc_files, "vor", ds_cache)
            t_s = find_spinup_time(
                mean_enstrophy(vor_full, lat),
                z_threshold=data_cfg.spinup.z_threshold,
                stable_time=data_cfg.spinup.stable_time,
                window_size=data_cfg.spinup.window_size,
            )
        if data_cfg.convergence is not None:
            lat = read_segment(nc_files[0], ds_cache)["lat"].values
            u_full = aggregated_read_field(nc_files, CONVERGENCE_DIAGNOSTIC_VAR, ds_cache)
            t_c = find_zonal_mean_convergence_time(
                u_full, lat,
                t_s if t_s is not None else 0,
                threshold=data_cfg.convergence.threshold,
                hold=data_cfg.convergence.hold,
            )
            if t_c is None:
                raise ValueError(
                    f"convergence not reached for {exp_dir}; "
                    "run validate-simulations --validate-convergence before preprocessing"
                )
        if clim_y_vars:
            a, b = resolve_window(data_cfg.climatology, t_s, t_c, M)
            clim_array = np.stack([
                compute_climatology(
                    diag, aggregated_read_field(nc_files, nc_var_for(diag), ds_cache), a, b
                )
                for diag in clim_y_vars
            ], axis=0).astype(np.float32)
    finally:
        for d in ds_cache.values():
            d.close()
        ds_cache = {}

    selected_t0 = selector.select(M, t_s=t_s, t_c=t_c)
    if not selected_t0:
        log.warning("skipping %s: no valid windows (M=%d, t_s=%s, t_c=%s)", exp_dir, M, t_s, t_c)
        return None

    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    try:
        for t_0 in selected_t0:
            x_channels = []
            for k in range(K):
                path_k, t_k = timeline[t_0 + k]
                ds_k = read_segment(path_k, ds_cache)
                for v in data_cfg.x_vars:
                    x_channels.append(ds_k[v].isel(time=t_k).values)
            xs.append(np.stack(x_channels, axis=0))
            if is_clim:
                ys.append(clim_array)
            else:
                path_y, t_y = timeline[t_0 + K]
                ds_y = read_segment(path_y, ds_cache)
                ys.append(np.stack([ds_y[v].isel(time=t_y).values for v in step_y_vars], axis=0))
    finally:
        for d in ds_cache.values():
            d.close()

    return np.stack(xs, axis=0), np.stack(ys, axis=0)
