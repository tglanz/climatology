import json
import logging
from pathlib import Path

import h5py
import numpy as np
import xarray as xr
from tqdm import tqdm

from ml.config import Config, IscaDataConfig
from ml.isca_dataset import fix_time_units, sample_indices, validate_segment

log = logging.getLogger(__name__)


def extract_pairs(
    exp_dirs: list[Path],
    cfg: IscaDataConfig,
    output_path: Path,
):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(output_path, "w") as f:
        x_ds = f.create_dataset(
            "x",
            shape=(0, len(cfg.x_vars), 0, 0),
            maxshape=(None, len(cfg.x_vars), None, None),
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

            exp_pairs: list[tuple[Path, int]] = []

            for path in nc_files:
                T, spatial = validate_segment(path, cfg.x_vars, cfg.y_vars)
                if spatial_shape is None:
                    spatial_shape = spatial
                    x_ds.resize((0, len(cfg.x_vars), *spatial_shape))
                    y_ds.resize((0, len(cfg.y_vars), *spatial_shape))
                else:
                    assert spatial == spatial_shape, f"spatial mismatch in {path}"

                for t in range(T - 1):
                    exp_pairs.append((path, t))

            exp_pairs = exp_pairs[cfg.skip :]
            assert exp_pairs, f"no pairs after skip={cfg.skip} in {exp_dir}"

            selected = sample_indices(
                len(exp_pairs), cfg.samples_per_experiment, cfg.sampling
            )

            for i in tqdm(selected, desc=exp_dir.name, leave=False):
                path, t = exp_pairs[i]
                ds = xr.open_dataset(path, decode_times=False)
                ds = fix_time_units(ds)

                x = np.stack([ds[v].isel(time=t).values for v in cfg.x_vars])
                y = np.stack([ds[v].isel(time=t + 1).values for v in cfg.y_vars])
                ds.close()

                x_ds.resize((written + 1, len(cfg.x_vars), *spatial_shape))
                y_ds.resize((written + 1, len(cfg.y_vars), *spatial_shape))
                x_ds[written] = x
                y_ds[written] = y
                written += 1

        log.info("wrote %d pairs to %s", written, output_path)


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

        n = len(exp_dirs)
        n_train = int(n * data_cfg.split[0])
        n_val = int(n * data_cfg.split[1])

        splits = {
            "train": exp_dirs[:n_train],
            "val": exp_dirs[n_train : n_train + n_val],
            "test": exp_dirs[n_train + n_val :],
        }

        log.info(
            "experiments: %d train / %d val / %d test",
            len(splits["train"]),
            len(splits["val"]),
            len(splits["test"]),
        )

        for name, dirs in splits.items():
            extract_pairs(dirs, data_cfg, out_dir / f"{name}.h5")

        manifest = {
            name: [str(Path("..") / d.relative_to(data_cfg.experiment_dir)) for d in dirs]
            for name, dirs in splits.items()
        }
        manifest_path = out_dir / "splits.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        log.info("wrote split manifest to %s", manifest_path)
