import logging
from pathlib import Path

import h5py
from ml.diagnostics.enstrophy import mean_enstrophy
import numpy as np
import xarray as xr
from tqdm import tqdm

from ml.config import Config, IscaDataConfig
from ml.data.isca_segment import aggregated_read_field, fix_time_units, read_segment, validate_segment
from ml.data.splits import Splits
from ml.data.window_selector import build_selector

from ml.diagnostics import (
    find_spinup_time,
    find_zonal_mean_convergence_time,
)

log = logging.getLogger(__name__)


CONVERGENCE_DIAGNOSTIC_VAR = "ucomp"

def sort_simulation_dirs(exp_dirs: list[Path]) -> list[Path]:
    return list(sorted(exp_dirs, key=lambda p: int(str(p).split("/")[-1])))

def extract_pairs(
    exp_dirs: list[Path],
    cfg: IscaDataConfig,
    output_path: Path,
):
    """
    Build (x, y) training pairs and write them to HDF5
    """

    exp_dirs = sort_simulation_dirs(exp_dirs)
    windows_cfg = cfg.windows
    spinup_cfg = cfg.spinup
    convergence_cfg = cfg.convergence
    K = windows_cfg.length
    n_in = K * len(cfg.x_vars)
    selector = build_selector(windows_cfg)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(output_path, "w") as f:
        x_ds = f.create_dataset(
            "x",
            shape=(0, n_in, 0, 0),
            maxshape=(None, n_in, None, None),
            dtype="float32",
        )
        y_ds = f.create_dataset(
            "y",
            shape=(0, len(cfg.y_vars), 0, 0),
            maxshape=(None, len(cfg.y_vars), None, None),
            dtype="float32",
        )

        spatial_shape = None
        written = 0

        for exp_dir in tqdm(exp_dirs, desc=f"preprocessing {output_path.stem}"):
            log.debug("processing exp_dir=%s", exp_dir)
            assert exp_dir.exists(), f"experiment directory not found: {exp_dir}"
            nc_files = sorted(exp_dir.glob(cfg.segment_pattern))
            assert nc_files, f"no NC files found: {exp_dir}/{cfg.segment_pattern}"

            timeline: list[tuple[Path, int]] = []
            for path in nc_files:
                T, spatial = validate_segment(path, cfg.x_vars, cfg.y_vars)
                if spatial_shape is None:
                    spatial_shape = spatial
                    x_ds.resize((0, n_in, *spatial_shape))
                    y_ds.resize((0, len(cfg.y_vars), *spatial_shape))
                else:
                    assert spatial == spatial_shape, f"spatial mismatch in {path}"
                for t in range(T):
                    timeline.append((path, t))

            M = len(timeline)
            t_s: int | None = None
            t_c: int | None = None
            ds_cache: dict[Path, xr.Dataset] = {}

            try:
                if spinup_cfg is not None:
                    lat = read_segment(nc_files[0], ds_cache)["lat"].values
                    vor_full = aggregated_read_field(nc_files, "vor", ds_cache)
                    enstrophy = mean_enstrophy(vor_full, lat)
                    t_s = find_spinup_time(
                        enstrophy,
                        z_threshold=spinup_cfg.z_threshold,
                        stable_time=spinup_cfg.stable_time,
                        window_size=spinup_cfg.window_size,
                    )
                if convergence_cfg is not None:
                    lat = read_segment(nc_files[0], ds_cache)["lat"].values
                    u_full = aggregated_read_field(nc_files, CONVERGENCE_DIAGNOSTIC_VAR, ds_cache)
                    t_c = find_zonal_mean_convergence_time(
                        u_full,
                        lat,
                        t_s if t_s is not None else 0,
                        threshold=convergence_cfg.threshold,
                        hold=convergence_cfg.hold,
                    )
            finally:
                for d in ds_cache.values():
                    d.close()
                ds_cache = {}

            selected_t0 = selector.select(M, t_s=t_s, t_c=t_c)

            if not selected_t0:
                log.warning(
                    "skipping %s: no valid windows (M=%d, K=%d, t_s=%s, t_c=%s)",
                    exp_dir, M, K, t_s, t_c,
                )
                continue

            try:
                for t_0 in selected_t0:
                    x_channels = []
                    for k in range(K):
                        path_k, t_k = timeline[t_0 + k]
                        ds_k = read_segment(path_k, ds_cache)
                        for v in cfg.x_vars:
                            x_channels.append(ds_k[v].isel(time=t_k).values)
                    x = np.stack(x_channels, axis=0)

                    path_y, t_y = timeline[t_0 + K]
                    ds_y = read_segment(path_y, ds_cache)
                    y = np.stack(
                        [ds_y[v].isel(time=t_y).values for v in cfg.y_vars], axis=0
                    )

                    x_ds.resize((written + 1, n_in, *spatial_shape))
                    y_ds.resize((written + 1, len(cfg.y_vars), *spatial_shape))
                    x_ds[written] = x
                    y_ds[written] = y
                    written += 1
            finally:
                for d in ds_cache.values():
                    d.close()

        log.info(
            "wrote %d pairs to %s (K=%d, %d input channels, "
            "start_at=%s, end_at=%s, stride=%d, limit=%s)",
            written, output_path, K, n_in,
            windows_cfg.start_at,
            windows_cfg.end_at,
            windows_cfg.stride,
            windows_cfg.limit,
        )

def list_simulation_dirs(cfg: IscaDataConfig, should_sort: bool = True):
    log.debug("listing simulations from %s/%s", cfg.experiment_dir, cfg.simulation_pattern)
    sim_dirs = list(cfg.experiment_dir.glob(cfg.simulation_pattern))

    assert sim_dirs, f"no simulations found: {cfg.experiment_dir}/{cfg.simulation_pattern}"

    if should_sort:
        sim_dirs = sort_simulation_dirs(sim_dirs)

    return sim_dirs

def list_segment_files(sim_dir: str, cfg: IscaDataConfig) -> list[str]:
    return list(sorted(sim_dir.glob(cfg.segment_pattern)))

class IscaDataPreprocessor:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def run(self):
        data_cfg = self.cfg.data
        out_dir = self.cfg.paths.preprocessed_dir
        exp_dirs = list_simulation_dirs(data_cfg)

        split_cfg = data_cfg.split

        n = len(exp_dirs)
        n_test = min(int(n * split_cfg.test), split_cfg.test_limit or float("inf"))
        n_validation = min(int(n * split_cfg.validation), split_cfg.validation_limit or float("inf"))
        n_train = min(n - n_test - n_validation, split_cfg.train_limit or float("inf"))
        log.info("processing data; total_experiments=%s, n_train=%s, n_test=%s, n_validation=%s",
                 n, n_train, n_test, n_validation)

        splits = Splits(
            test=exp_dirs[:n_test],
            validation=exp_dirs[n_test : n_test + n_validation],
            train=exp_dirs[n_test + n_validation : n_test + n_validation + n_train],
        )

        log.info("extracting validation pairs")
        extract_pairs(splits.validation, data_cfg, out_dir / "val.h5")
        
        log.info("extracing test pairs")
        extract_pairs(splits.test, data_cfg, out_dir / "test.h5")

        log.info("extracting train pairs")
        extract_pairs(splits.train, data_cfg, out_dir / "train.h5")


        splits.save(self.cfg.paths)

        log.info("finished isca preprocessing")
