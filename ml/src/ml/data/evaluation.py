"""Simulation loading for evaluation, preserving its existing target and fallback policies."""

from __future__ import annotations

import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ml.config import IscaDataConfig
from ml.data.climatology import compute_climatology, nc_var_for, resolve_window
from ml.data.isca_segment import aggregated_read_field, read_segment
from ml.data.isca_preprocessing import list_segment_files
from ml.diagnostics.convergence import (
    find_zonal_mean_convergence_time,
    compute_time_mean_zonal_mean,
)
from ml.diagnostics.enstrophy import mean_enstrophy
from ml.diagnostics.spinup import find_spinup_time

from ml.data.simulation_data import (
    CONVERGENCE_DIAGNOSTIC_VAR,
    build_timeline,
    stack_input_windows,
)

log = logging.getLogger(__name__)


@dataclass
class SimResult:
    sim_dir: Path
    code: str
    lat: np.ndarray
    truth_profile: np.ndarray
    x_windows: np.ndarray
    y_windows: np.ndarray
    pred_profile: np.ndarray | None = None


def _config_code(sim_dir: Path) -> str:
    name = sim_dir.name
    return name.rsplit("-", 1)[0] if "-" in name else name


def _load_one_sim(sim_dir: Path, data_cfg: IscaDataConfig) -> SimResult | None:
    """Load one simulation: compute climatology truth and extract windows."""
    nc_files = list_segment_files(sim_dir, data_cfg)
    if not nc_files:
        log.warning("no NC files in %s", sim_dir)
        return None

    ds_cache: dict = {}
    try:
        lat = read_segment(nc_files[0], ds_cache)["lat"].values

        t_s: int | None = None
        t_c: int | None = None

        lengths = []
        for path in nc_files:
            ds_tmp = read_segment(path, ds_cache)
            lengths.append(ds_tmp.sizes["time"])
        timeline_len = sum(lengths)

        if data_cfg.spinup is not None:
            vor_full = aggregated_read_field(nc_files, "vor", ds_cache)
            t_s = find_spinup_time(
                mean_enstrophy(vor_full, lat),
                z_threshold=data_cfg.spinup.z_threshold,
                stable_time=data_cfg.spinup.stable_time,
                window_size=data_cfg.spinup.window_size,
            )

        clim_y_vars = data_cfg.y_vars
        if not clim_y_vars:
            log.warning("no y_vars defined")
            return None

        diag_name = clim_y_vars[0]
        nc_var = nc_var_for(diag_name)

        # Load the climatology field once; reuse for both convergence detection and climatology.
        # CONVERGENCE_DIAGNOSTIC_VAR is "ucomp" and the climatology nc_var is also "ucomp" here.
        if nc_var == CONVERGENCE_DIAGNOSTIC_VAR:
            clim_field = aggregated_read_field(nc_files, nc_var, ds_cache)
            u_full = clim_field
        else:
            u_full = aggregated_read_field(
                nc_files, CONVERGENCE_DIAGNOSTIC_VAR, ds_cache
            )
            clim_field = aggregated_read_field(nc_files, nc_var, ds_cache)

        if data_cfg.convergence is not None:
            t_c = find_zonal_mean_convergence_time(
                u_full,
                lat,
                t_s if t_s is not None else 0,
                threshold=data_cfg.convergence.threshold,
                hold=data_cfg.convergence.hold,
            )
            if t_c is None:
                log.warning(
                    "convergence not reached in %s; using end of trajectory", sim_dir
                )
                t_c = timeline_len - 1

        a, b = resolve_window(data_cfg.climatology, t_s, t_c, timeline_len)
        truth_profile = compute_climatology(diag_name, clim_field, a, b).astype(
            np.float32
        )

        from ml.data.window_selector import build_selector

        selector = build_selector(data_cfg.windows)
        K = data_cfg.windows.length

        timeline = build_timeline(nc_files, lengths)

        selected_t0 = selector.select(len(timeline), t_s=t_s, t_c=t_c)
        if not selected_t0:
            log.warning("no valid windows in %s", sim_dir)
            return None

        xs = stack_input_windows(timeline, selected_t0, K, data_cfg.x_vars, ds_cache)
        ys = np.stack([truth_profile[None] for _ in selected_t0], axis=0)

        return SimResult(
            sim_dir=sim_dir,
            code=_config_code(sim_dir),
            lat=lat,
            truth_profile=truth_profile,
            x_windows=xs.astype(np.float32),
            y_windows=ys.astype(np.float32),
        )
    except Exception as exc:
        log.error("failed loading %s: %s", sim_dir, exc)
        return None
    finally:
        for ds in ds_cache.values():
            try:
                ds.close()
            except Exception:
                pass


def load_all_sims(
    sim_dirs: list[Path],
    data_cfg: IscaDataConfig,
    max_workers: int = 8,
) -> list[SimResult]:
    """Load all simulations in parallel, returning only successful results."""
    results: list[SimResult] = []
    failed = 0
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_load_one_sim, sd, data_cfg): sd for sd in sim_dirs}
        total = len(futures)
        done = 0
        for fut in as_completed(futures):
            done += 1
            if done % 20 == 0 or done == total:
                log.info("loaded %d/%d sims", done, total)
            result = fut.result()
            if result is not None:
                results.append(result)
            else:
                failed += 1
    if failed:
        log.warning("%d sims failed to load", failed)
    return results


from ml.data.isca_segment import read_segments


def load_profile(
    sim_dir: Path, spinup_cfg, convergence_cfg
) -> tuple[np.ndarray, np.ndarray, int | None]:
    ds = read_segments(str(sim_dir / "run*/atmos_daily.nc"))
    vor = ds.vor.values
    u = ds.ucomp.values
    lat = ds.lat.values
    M = vor.shape[0]
    t_s = find_spinup_time(mean_enstrophy(vor, lat), **spinup_cfg.to_kwargs())
    t_c = find_zonal_mean_convergence_time(
        u, lat, t_s or 0, **convergence_cfg.to_kwargs()
    )
    start = t_c if t_c is not None else (t_s or 0)
    profile = compute_time_mean_zonal_mean(u, start, M)
    ds.close()
    return lat, profile, t_c
