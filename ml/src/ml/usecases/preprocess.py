import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import h5py
from tqdm import tqdm

from ml.config import load as load_config
from ml.data.climatology import is_climatology_var
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

    step_y_vars = [v for v in data_cfg.y_vars if not is_climatology_var(v)]
    clim_y_vars = [v for v in data_cfg.y_vars if is_climatology_var(v)]
    is_clim = bool(clim_y_vars)
    active_y_vars = clim_y_vars if is_clim else step_y_vars

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
                y_ds.attrs["vars"] = active_y_vars
                y_ds.attrs["kind"] = "climatology" if is_clim else "step"

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
        "climatology" if is_clim else "step", active_y_vars,
    )


def _config_key(sim_dir: Path) -> str:
    name = sim_dir.name
    if '-' in name:
        return name.rsplit('-', 1)[0]
    return ''


def _config_split(
    exp_dirs: list[Path],
    test_ratio: float,
    val_ratio: float,
    test_limit: int | None,
    val_limit: int | None,
    train_limit: int | None,
) -> tuple[list[Path], list[Path], list[Path]]:
    from collections import defaultdict
    groups: dict[str, list[Path]] = defaultdict(list)
    for d in exp_dirs:
        groups[_config_key(d)].append(d)

    codes = sorted(groups.keys())
    n = len(codes)
    n_test  = max(1, round(n * test_ratio))
    n_val   = max(1, round(n * val_ratio))

    test_codes  = codes[:n_test]
    val_codes   = codes[n_test:n_test + n_val]
    train_codes = codes[n_test + n_val:]

    test_dirs  = [d for c in test_codes  for d in groups[c]]
    val_dirs   = [d for c in val_codes   for d in groups[c]]
    train_dirs = [d for c in train_codes for d in groups[c]]

    if test_limit:
        test_dirs = test_dirs[:test_limit]
    if val_limit:
        val_dirs = val_dirs[:val_limit]
    if train_limit:
        train_dirs = train_dirs[:train_limit]

    return test_dirs, val_dirs, train_dirs


def run(config_path: Path, n_workers: int = 0) -> None:
    cfg = load_config(config_path)
    data_cfg = cfg.data
    out_dir = cfg.paths.preprocessed_dir
    exp_dirs = list_simulation_dirs(data_cfg)

    split_cfg = data_cfg.split
    test_dirs, val_dirs, train_dirs = _config_split(
        exp_dirs,
        test_ratio=split_cfg.test,
        val_ratio=split_cfg.validation,
        test_limit=split_cfg.test_limit,
        val_limit=split_cfg.validation_limit,
        train_limit=split_cfg.train_limit,
    )
    log.info(
        "processing data; total=%d, n_train=%d, n_val=%d, n_test=%d",
        len(exp_dirs), len(train_dirs), len(val_dirs), len(test_dirs),
    )

    splits = Splits(
        test=test_dirs,
        validation=val_dirs,
        train=train_dirs,
    )

    log.info("extracting val pairs")
    _extract_pairs(splits.validation, config_path, out_dir / "val.h5",   n_workers=n_workers)
    log.info("extracting test pairs")
    _extract_pairs(splits.test,       config_path, out_dir / "test.h5",  n_workers=n_workers)
    log.info("extracting train pairs")
    _extract_pairs(splits.train,      config_path, out_dir / "train.h5", n_workers=n_workers)

    splits.save(cfg.paths)
    log.info("finished preprocessing")
