"""By-code notebook evaluation; selection differences are recorded for phase 2."""

from pathlib import Path
import json
import numpy as np
import torch
from ml.data.isca_segment import read_segment, aggregated_read_field
from ml.data.simulation_data import extract_windows
from ml.diagnostics.spinup import find_spinup_time
from ml.diagnostics.enstrophy import mean_enstrophy
from ml.diagnostics.convergence import (
    find_zonal_mean_convergence_time,
    compute_time_mean_zonal_mean,
)
from ml.inference import predict_windows


def code_label(code: str, sim_root: Path) -> str:
    nl_path = next(sim_root.glob(f"{code}-*/namelist.json"), None)
    if nl_path is None:
        return code
    s = json.load(open(nl_path))["stirring_nml"]
    return f"{code}  lat0={s['lat0']} amp={s['amplitude']:.2e} widthy={s['widthy']}"


def find_replicates(code: str, sim_root: Path) -> list[Path]:
    dirs = sorted(sim_root.glob(f"{code}-*"))
    assert dirs, f"no simulation directories found for code {code!r}"
    return dirs


def evaluate_sim(sim_dir: Path, cfg, model, norm) -> dict | None:
    nc_files = sorted(sim_dir.glob(cfg.data.segment_pattern))
    if not nc_files:
        return None

    ds_cache: dict = {}
    try:
        lat = read_segment(nc_files[0], ds_cache)["lat"].values.astype(np.float64)
        vor_full = aggregated_read_field(nc_files, "vor", ds_cache)
        u_full = aggregated_read_field(nc_files, "ucomp", ds_cache)
    finally:
        for d in ds_cache.values():
            d.close()

    T = vor_full.shape[0]

    t_s = 0
    if cfg.data.spinup is not None:
        detected = find_spinup_time(
            mean_enstrophy(vor_full, lat), **cfg.data.spinup.to_kwargs()
        )
        if detected is not None:
            t_s = detected

    t_c = t_s
    if cfg.data.convergence is not None:
        detected = find_zonal_mean_convergence_time(
            u_full,
            lat,
            t_s,
            threshold=cfg.data.convergence.threshold,
            hold=cfg.data.convergence.hold,
        )
        if detected is not None:
            t_c = detected

    truth = compute_time_mean_zonal_mean(u_full, t_c, T)

    K = cfg.data.windows.length
    windows = extract_windows(vor_full, t_s, K, cfg.data.windows.stride)
    if len(windows) == 0:
        return None

    preds = predict_windows(
        model, norm, windows.astype(np.float32), torch.device("cpu"), len(windows)
    )

    return {
        "sim_dir": sim_dir,
        "lat": lat,
        "truth": truth,
        "predictions": preds,
        "mean_pred": preds.mean(axis=0),
        "t_s": t_s,
        "t_c": t_c,
    }


def collect(codes, sim_root, cfg, model, norm):
    return {
        code: (
            code_label(code, sim_root),
            [
                result
                for sim_dir in find_replicates(code, sim_root)
                if (result := evaluate_sim(sim_dir, cfg, model, norm)) is not None
            ],
        )
        for code in codes
    }


def print_metrics(code_results):
    from ml.diagnostics.errors import (
        notebook_profile_rel_l2 as rel_l2,
        profile_rmse as rmse,
    )

    header = (
        f"  {'code / replicate':<38} {'t_s':>6} {'t_c':>6} {'rmse':>10} {'relL2':>10}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))
    for code, (label, results) in code_results.items():
        print(f"  {label}")
        all_rl = []
        for res in results:
            lat = res["lat"]
            r = rmse(res["mean_pred"], res["truth"], lat)
            rl = rel_l2(res["mean_pred"], res["truth"], lat)
            all_rl.append(rl)
            print(
                f"    {res['sim_dir'].name:<36} {res['t_s']:>6} {res['t_c']:>6} {r:>10.4f} {rl:>10.4f}"
            )
        print(
            f"    {'mean relL2':>36} {'':>6} {'':>6} {'':>10} {np.mean(all_rl):>10.4f}"
        )
        print()
