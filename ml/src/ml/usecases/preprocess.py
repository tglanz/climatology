import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import h5py
from tqdm import tqdm

from ml.config import load as load_config
from ml.data.isca_preprocessing import list_simulation_dirs, process_one_sim, sort_simulation_dirs
from ml.data.splits import Splits

log = logging.getLogger(__name__)


def _extract_pairs(
    exp_dirs: list[Path],
    config_path: Path,
    output_path: Path,
    n_workers: int,
) -> None:
    cfg = load_config(config_path)
    data_cfg = cfg.data
    windows_cfg = data_cfg.windows

    exp_dirs = sort_simulation_dirs(exp_dirs)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if n_workers == 0:
        results = (
            process_one_sim(d, config_path)
            for d in tqdm(exp_dirs, desc=output_path.stem)
        )
    else:
        executor = ProcessPoolExecutor(max_workers=n_workers)
        futures = {executor.submit(process_one_sim, d, config_path): d for d in exp_dirs}
        results = (
            f.result()
            for f in tqdm(as_completed(futures), total=len(exp_dirs), desc=output_path.stem)
        )

    written = 0
    x_ds = y_ds = None

    with h5py.File(output_path, "w") as f:
        for result in results:
            if result is None:
                continue
            x_arr, y_arr = result
            n = x_arr.shape[0]

            if x_ds is None:
                x_ds = f.create_dataset(
                    "x",
                    shape=(0, *x_arr.shape[1:]),
                    maxshape=(None, *x_arr.shape[1:]),
                    dtype="float32",
                )
                y_ds = f.create_dataset(
                    "y",
                    shape=(0, *y_arr.shape[1:]),
                    maxshape=(None, *y_arr.shape[1:]),
                    dtype="float32",
                )
                y_ds.attrs["vars"] = data_cfg.y_vars
                y_ds.attrs["kind"] = "climatology"

            x_ds.resize((written + n, *x_ds.shape[1:]))
            x_ds[written : written + n] = x_arr
            y_ds.resize((written + n, *y_ds.shape[1:]))
            y_ds[written : written + n] = y_arr
            written += n

    if n_workers != 0:
        executor.shutdown(wait=False)

    log.info(
        "wrote %d pairs to %s (K=%d, start_at=%s, end_at=%s, stride=%d, limit=%s, y_kind=%s, y_vars=%s)",
        written, output_path, windows_cfg.length,
        windows_cfg.start_at, windows_cfg.end_at, windows_cfg.stride, windows_cfg.limit,
        "climatology", data_cfg.y_vars,
    )


def run(config_path: Path, split_path: Path, n_workers: int = 0) -> None:
    import shutil
    cfg = load_config(config_path)
    out_dir = cfg.paths.preprocessed_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    splits = Splits.load(split_path)
    log.info(
        "processing data; n_train=%d, n_val=%d, n_test=%d",
        len(splits.train), len(splits.validation), len(splits.test),
    )

    log.info("extracting val pairs")
    _extract_pairs(splits.validation, config_path, out_dir / "val.h5",   n_workers=n_workers)
    log.info("extracting test pairs")
    _extract_pairs(splits.test,       config_path, out_dir / "test.h5",  n_workers=n_workers)
    log.info("extracting train pairs")
    _extract_pairs(splits.train,      config_path, out_dir / "train.h5", n_workers=n_workers)

    shutil.copy2(split_path, out_dir / "splits.json")
    log.info("finished preprocessing")
