import logging
from pathlib import Path

import h5py
import numpy as np
import xarray as xr
from tqdm import tqdm

from ml.config import Config, IscaDataConfig
from ml.data.isca_dataset import fix_time_units, validate_segment
from ml.data.splits import Splits
from ml.data.window_selector import build_selector
from ml.diagnostics import (
    compute_enstrophy,
    find_spinup_time,
    find_zonal_mean_convergence_time,
)

log = logging.getLogger(__name__)


CONVERGENCE_DIAGNOSTIC_VAR = "ucomp"


def _open_cached(path: Path, ds_cache: dict[Path, xr.Dataset]) -> xr.Dataset:
    if path not in ds_cache:
        ds_cache[path] = fix_time_units(xr.open_dataset(path, decode_times=False))
    return ds_cache[path]


def _aggregate_field(
    nc_files: list[Path],
    var_name: str,
    ds_cache: dict[Path, xr.Dataset],
) -> np.ndarray:
    arrays = [_open_cached(p, ds_cache)[var_name].values for p in nc_files]
    return np.concatenate(arrays, axis=0)


def extract_pairs(
    exp_dirs: list[Path],
    cfg: IscaDataConfig,
    output_path: Path,
):
    """
    Build (x, y) training pairs and write them to HDF5.

    For window_length=K, each x sample stacks the input variables at K
    consecutive timesteps along the channel axis (oldest to newest,
    x_vars-major within each timestep): channel order is
        [x_vars[0]_{t_0}, ..., x_vars[-1]_{t_0},
         x_vars[0]_{t_0+1}, ..., x_vars[-1]_{t_0+1},
         ...,
         x_vars[0]_{t_0+K-1}, ..., x_vars[-1]_{t_0+K-1}]
    The corresponding y is y_vars at timestep t_0 + K.

    Timesteps are concatenated across the segment files of each
    simulation, so a window may straddle a segment boundary. The set
    of window-start indices t_0 is produced by `WindowSelector` given
    per-simulation t_s and t_c when the spinup / convergence
    sub-sections of `[data.windows]` are configured.
    """
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
                    lat = _open_cached(nc_files[0], ds_cache)["lat"].values
                    vor_full = _aggregate_field(nc_files, "vor", ds_cache)
                    enstrophy = compute_enstrophy(vor_full, lat)
                    t_s = find_spinup_time(
                        enstrophy,
                        tol=spinup_cfg.threshold,
                        hold=spinup_cfg.hold,
                    )
                if convergence_cfg is not None:
                    lat = _open_cached(nc_files[0], ds_cache)["lat"].values
                    u_full = _aggregate_field(
                        nc_files, CONVERGENCE_DIAGNOSTIC_VAR, ds_cache
                    )
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
                        ds_k = _open_cached(path_k, ds_cache)
                        for v in cfg.x_vars:
                            x_channels.append(ds_k[v].isel(time=t_k).values)
                    x = np.stack(x_channels, axis=0)

                    path_y, t_y = timeline[t_0 + K]
                    ds_y = _open_cached(path_y, ds_cache)
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


class IscaDataPreprocessor:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def run(self):
        data_cfg = self.cfg.data
        out_dir = self.cfg.paths.preprocessed_dir

        exp_dirs = sorted(data_cfg.experiment_dir.glob(data_cfg.simulation_pattern))
        assert (
            exp_dirs
        ), f"no experiments found: {data_cfg.experiment_dir}/{data_cfg.simulation_pattern}"

        split_cfg = data_cfg.split

        n = len(exp_dirs)
        n_test = min(int(n * split_cfg.test), split_cfg.test_limit or float("inf"))
        n_val = min(int(n * split_cfg.validation), split_cfg.validation_limit or float("inf"))
        n_train = min(n - n_test - n_val, split_cfg.train_limit or float("inf"))

        splits = Splits(
            test=exp_dirs[:n_test],
            validation=exp_dirs[n_test : n_test + n_val],
            train=exp_dirs[n_test + n_val : n_test + n_val + n_train],
        )

        extract_pairs(splits.train, data_cfg, out_dir / "train.h5")
        extract_pairs(splits.validation, data_cfg, out_dir / "val.h5")
        extract_pairs(splits.test, data_cfg, out_dir / "test.h5")

        splits.save(self.cfg.paths)

        log.info("finished isca preprocessing")
