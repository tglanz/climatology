"""
Metrics and data loading utilities for model evaluation.

Provides:
  - profile_rel_l2: lat-weighted relL2 for 1D profiles
  - profile_rmse: lat-weighted RMSE for 1D profiles
  - load_sim_climatology: compute truth climatology profile from NC files
  - load_all_sims: parallel loader returning per-sim results
"""
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
from ml.diagnostics.convergence import find_zonal_mean_convergence_time
from ml.diagnostics.enstrophy import mean_enstrophy
from ml.diagnostics.spatial import cosine_latitude_weights
from ml.diagnostics.spinup import find_spinup_time

log = logging.getLogger(__name__)

CONVERGENCE_DIAGNOSTIC_VAR = "ucomp"


def profile_rel_l2(
    pred: np.ndarray,
    truth: np.ndarray,
    lat: np.ndarray,
    eps: float = 1e-12,
) -> float:
    """Lat-weighted relL2 for 1D profiles of shape (H,).

    Uses cosine-latitude weights normalized to mean 1.
    """
    w = cosine_latitude_weights(lat)
    num = float(np.sqrt(np.sum(w * (pred - truth) ** 2)))
    den = float(np.sqrt(np.sum(w * truth ** 2)))
    return num / (den + eps)


def profile_rmse(
    pred: np.ndarray,
    truth: np.ndarray,
    lat: np.ndarray,
) -> float:
    """Lat-weighted RMSE for 1D profiles of shape (H,)."""
    w = cosine_latitude_weights(lat)
    return float(np.sqrt(np.sum(w * (pred - truth) ** 2) / np.sum(w)))


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

        timeline_len = 0
        for path in nc_files:
            ds_tmp = read_segment(path, ds_cache)
            timeline_len += ds_tmp.sizes["time"]

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
            u_full = aggregated_read_field(nc_files, CONVERGENCE_DIAGNOSTIC_VAR, ds_cache)
            clim_field = aggregated_read_field(nc_files, nc_var, ds_cache)

        if data_cfg.convergence is not None:
            t_c = find_zonal_mean_convergence_time(
                u_full, lat,
                t_s if t_s is not None else 0,
                threshold=data_cfg.convergence.threshold,
                hold=data_cfg.convergence.hold,
            )
            if t_c is None:
                log.warning("convergence not reached in %s; using end of trajectory", sim_dir)
                t_c = timeline_len - 1

        if data_cfg.climatology is None:
            a, b = 0, timeline_len
        else:
            a, b = resolve_window(data_cfg.climatology, t_s, t_c, timeline_len)
        truth_profile = compute_climatology(diag_name, clim_field, a, b).astype(np.float32)

        from ml.data.window_selector import build_selector
        selector = build_selector(data_cfg.windows)
        K = data_cfg.windows.length

        timeline: list[tuple[Path, int]] = []
        for path in nc_files:
            ds_tmp = read_segment(path, ds_cache)
            T = ds_tmp.sizes["time"]
            timeline.extend((path, t) for t in range(T))

        selected_t0 = selector.select(len(timeline), t_s=t_s, t_c=t_c)
        if not selected_t0:
            log.warning("no valid windows in %s", sim_dir)
            return None

        xs = []
        ys = []
        for t_0 in selected_t0:
            x_channels = []
            for k in range(K):
                path_k, t_k = timeline[t_0 + k]
                ds_k = read_segment(path_k, ds_cache)
                for v in data_cfg.x_vars:
                    x_channels.append(ds_k[v].isel(time=t_k).values)
            xs.append(np.stack(x_channels, axis=0))
            ys.append(truth_profile[None])

        return SimResult(
            sim_dir=sim_dir,
            code=_config_code(sim_dir),
            lat=lat,
            truth_profile=truth_profile,
            x_windows=np.stack(xs, axis=0).astype(np.float32),
            y_windows=np.stack(ys, axis=0).astype(np.float32),
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
