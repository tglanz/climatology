"""Descriptive per-target replicate deviation under the shared sample contract."""

from pathlib import Path

import numpy as np

from ml.config import load as load_config
from ml.data.evaluation import load_all_sims
from ml.data.isca_preprocessing import list_simulation_dirs
from ml.diagnostics.errors import ScoreSummary, profile_relative_l2_values


def _within_group_loss(
    clims: list[np.ndarray], latitudes: np.ndarray
) -> tuple[float, float]:
    stack = np.stack(clims)
    if stack.ndim == 3 and stack.shape[1] == 1:
        stack = stack[:, 0]
    if stack.ndim != 2:
        raise ValueError("replicate profiles must have shape (replica, latitude)")
    reference = np.broadcast_to(stack.mean(0), stack.shape)
    values = profile_relative_l2_values(stack, reference, latitudes)
    finite = values[np.isfinite(values)]
    return (
        (float(finite.mean()), float(finite.std()))
        if len(finite)
        else (float("nan"), float("nan"))
    )


def run(config_path: Path, n_workers: int = 0) -> None:
    cfg = load_config(config_path)
    loaded = load_all_sims(
        list_simulation_dirs(cfg.data, cfg.paths.experiment_dir), cfg.data, n_workers
    )
    for channel, name in enumerate(cfg.data.y_vars):
        print(f"Observed replicate relative deviation: {name}")
        print("code replicas mean_relative_deviation included undefined")
        for code in sorted({r.code for r in loaded.results}):
            results = [r for r in loaded.results if r.code == code]
            if len(results) < 2:
                print(f"{code} 1 unavailable 0 0")
                continue
            profiles = np.stack([r.truth_profile[channel] for r in results])
            reference = np.broadcast_to(profiles.mean(0), profiles.shape)
            summary = ScoreSummary.from_values(
                profile_relative_l2_values(profiles, reference, results[0].lat)
            )
            print(
                f"{code} {len(results)} {summary.mean} {summary.count} {summary.undefined}"
            )
    print(
        "Replica deviations describe this finite ensemble; they do not establish an irreducible-error bound."
    )
