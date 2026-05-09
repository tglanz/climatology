import json
import logging
from pathlib import Path

import h5py
from ml.data.splits import Splits
import numpy as np
import xarray as xr
from tqdm import tqdm

from ml.config import Config, IscaDataConfig
from ml.data.isca_dataset import fix_time_units, sample_indices, validate_segment

log = logging.getLogger(__name__)


def extract_pairs(
    exp_dirs: list[Path],
    cfg: IscaDataConfig,
    output_path: Path,
):
    """
    Build (x, y) training pairs and write them to HDF5.

    For lag_steps=K, each x sample stacks the input variables at K consecutive
    timesteps along the channel axis (oldest to newest, x_vars-major within
    each timestep): channel order is
        [x_vars[0]_{t-K+1}, ..., x_vars[-1]_{t-K+1},
         x_vars[0]_{t-K+2}, ..., x_vars[-1]_{t-K+2},
         ...,
         x_vars[0]_{t},     ..., x_vars[-1]_{t}]
    The corresponding y is y_vars at timestep t+1.

    Timesteps are concatenated across the segment files of each simulation,
    so a window may straddle a segment boundary.
    """
    K = cfg.lag_steps
    n_in = K * len(cfg.x_vars)
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

            # Flat per-sim sequence of timesteps across all segments,
            # in chronological order.
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

            # Valid target indices: need K timesteps before (inclusive) and 1 after.
            #   target index `j` in `timeline`, where j-K is the oldest input,
            #                                          j-1 is the newest input,
            #                                          j   is the target.
            # So j must satisfy K <= j <= len(timeline) - 1.
            valid_target_indices = list(range(K, len(timeline)))
            valid_target_indices = valid_target_indices[cfg.skip:]
            assert valid_target_indices, (
                f"no valid samples after lag_steps={K} and skip={cfg.skip} in {exp_dir} "
                f"(timeline length {len(timeline)})"
            )

            selected = sample_indices(
                len(valid_target_indices), cfg.samples_per_experiment, cfg.sampling
            )

            # Open each NC file at most once per simulation.
            ds_cache: dict[Path, xr.Dataset] = {}
            try:
                for sel in selected:
                    j = valid_target_indices[sel]

                    x_channels = []
                    for k in range(K):
                        path_k, t_k = timeline[j - K + k]
                        if path_k not in ds_cache:
                            ds_cache[path_k] = fix_time_units(
                                xr.open_dataset(path_k, decode_times=False)
                            )
                        ds_k = ds_cache[path_k]
                        for v in cfg.x_vars:
                            x_channels.append(ds_k[v].isel(time=t_k).values)
                    x = np.stack(x_channels, axis=0)

                    path_y, t_y = timeline[j]
                    if path_y not in ds_cache:
                        ds_cache[path_y] = fix_time_units(
                            xr.open_dataset(path_y, decode_times=False)
                        )
                    ds_y = ds_cache[path_y]
                    y = np.stack(
                        [ds_y[v].isel(time=t_y).values for v in cfg.y_vars], axis=0
                    )

                    x_ds.resize((written + 1, n_in, *spatial_shape))
                    y_ds.resize((written + 1, len(cfg.y_vars), *spatial_shape))
                    x_ds[written] = x
                    y_ds[written] = y
                    written += 1
            finally:
                for ds in ds_cache.values():
                    ds.close()

        log.info(
            "wrote %d pairs to %s (lag_steps=%d, %d input channels)",
            written, output_path, K, n_in,
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

        log.info("finished isca preprocessing")