import logging
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from tqdm import tqdm

from ml.config import load as load_config
from ml.data.isca_dataset import load_latitudes
from ml.data.isca_preprocessing import list_simulation_dirs, process_one_sim
from ml.data.sweep_file import SweepFile
from ml.diagnostics.errors import lat_weighted_relative_l2

log = logging.getLogger(__name__)


def _config_code(sim_dir: Path) -> str:
    name = sim_dir.name
    return name.rsplit("-", 1)[0] if "-" in name else name


def _collect_climatologies(
    sim_dirs: list[Path],
    config_path: Path,
    n_workers: int,
) -> dict[str, list[tuple[Path, np.ndarray]]]:
    if n_workers == 0:
        results = (
            (d, process_one_sim(d, config_path))
            for d in tqdm(sim_dirs, desc="processing sims")
        )
    else:
        executor = ProcessPoolExecutor(max_workers=n_workers)
        futures = {executor.submit(process_one_sim, d, config_path): d for d in sim_dirs}
        results = (
            (futures[f], f.result())
            for f in tqdm(as_completed(futures), total=len(sim_dirs), desc="processing sims")
        )

    groups: dict[str, list[tuple[Path, np.ndarray]]] = defaultdict(list)
    for sim_dir, result in results:
        if result is None:
            log.warning("skipped %s", sim_dir)
            continue
        _, y_arr = result
        clim = y_arr[0]
        groups[_config_code(sim_dir)].append((sim_dir, clim))

    if n_workers != 0:
        executor.shutdown(wait=False)

    return groups


def _within_group_loss(
    clims: list[np.ndarray],
    latitudes: np.ndarray,
) -> tuple[float, float]:
    stack = np.stack(clims, axis=0)
    grand_mean = stack.mean(axis=0)

    losses = []
    for clim in clims:
        pred = clim.squeeze(0) if clim.ndim > 1 and clim.shape[0] == 1 else clim
        truth = grand_mean.squeeze(0) if grand_mean.ndim > 1 and grand_mean.shape[0] == 1 else grand_mean
        losses.append(lat_weighted_relative_l2(pred, truth, latitudes))

    return float(np.mean(losses)), float(np.std(losses))


def run(config_path: Path, n_workers: int = 0) -> None:
    cfg = load_config(config_path)
    latitudes = load_latitudes(cfg)
    sim_dirs = list_simulation_dirs(cfg.data, cfg.paths.experiment_dir)
    log.info("found %d simulation dirs", len(sim_dirs))

    sweep = None
    sweep_path = cfg.paths.experiment_dir / "sweep.json"
    if sweep_path.exists():
        sweep = SweepFile(sweep_path)

    groups = _collect_climatologies(sim_dirs, config_path, n_workers)
    log.info("grouped into %d configs", len(groups))

    col_w = 40
    all_losses = []
    print(f"\n{'config':<{col_w}} {'n_reps':>6}  {'mean_loss':>10}  {'std_loss':>10}")
    print("-" * (col_w + 32))
    for code, entries in sorted(groups.items()):
        label = sweep.describe(code) if sweep else code
        clims = [clim for _, clim in entries]
        if len(clims) < 2:
            print(f"{label:<{col_w}} {'1':>6}  {'n/a':>10}  {'n/a':>10}")
            continue
        mean_loss, std_loss = _within_group_loss(clims, latitudes)
        all_losses.extend([mean_loss] * len(clims))
        print(f"{label:<{col_w}} {len(clims):>6}  {mean_loss:>10.4f}  {std_loss:>10.4f}")

    if all_losses:
        print("-" * (col_w + 32))
        print(f"{'overall':<{col_w}} {len(sim_dirs):>6}  {np.mean(all_losses):>10.4f}  {np.std(all_losses):>10.4f}")
        print(f"\nNoise floor (mean within-config loss): {np.mean(all_losses):.4f}")
        print("A model cannot do better than this on per-replicate targets.")
