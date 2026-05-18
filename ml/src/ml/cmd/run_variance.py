"""Cross-simulation variance of the post-spinup diagnostic.

For each of the first P simulations under EXPERIMENT_DIR/simulations/,
detect spinup time t_s from the global enstrophy series, compute the
diagnostic D_n = time-mean zonal-mean of u over [t_s, M_n], and plot all
P diagnostics together with their ensemble mean and one-standard-
deviation envelope.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from ml.cmd.rotating_globe import load_data
from ml.diagnostics import (
    compute_enstrophy,
    compute_time_mean_zonal_mean,
    find_spinup_time,
)

EXPERIMENT_DIR = Path("output/barotropic_stirring-T85")
P = 10


def main():
    sims_dir = EXPERIMENT_DIR / "simulations"
    diagnostics = []
    spinup_times = []
    lat = None

    for n in tqdm(range(P), desc="simulations"):
        ds = load_data(str(sims_dir / str(n)))
        vor = ds.vor.values
        u = ds.ucomp.values
        if lat is None:
            lat = ds.lat.values
        M = vor.shape[0]
        spinup_time = find_spinup_time(compute_enstrophy(vor, lat))
        spinup_times.append(spinup_time)
        diagnostics.append(compute_time_mean_zonal_mean(u, spinup_time, M))

    diagnostics = np.stack(diagnostics, axis=0)
    ensemble_mean = diagnostics.mean(axis=0)
    ensemble_std = diagnostics.std(axis=0, ddof=1)

    print(f"spinup_time per simulation: {spinup_times}")
    print(f"Max envelope width: {2 * ensemble_std.max():.3f} m/s")

    out_dir = EXPERIMENT_DIR / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"variance_P{P}.png"

    fig, ax = plt.subplots(figsize=(7, 6))
    for n in range(P):
        ax.plot(diagnostics[n], lat, color="C0", alpha=0.25, linewidth=0.8)
    ax.plot(ensemble_mean, lat, color="C0", linewidth=2.0, label="ensemble mean")
    ax.fill_betweenx(
        lat,
        ensemble_mean - ensemble_std,
        ensemble_mean + ensemble_std,
        color="C0",
        alpha=0.15,
        label=r"$\pm 1\sigma$",
    )
    ax.axvline(0.0, color="k", linestyle="--", linewidth=0.6)
    ax.set_xlabel("Diagnostic = time-mean zonal-mean u  [m/s]")
    ax.set_ylabel("Latitude  [deg]")
    ax.set_title(f"Cross-simulation variance of post-spinup diagnostic (P = {P})")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    print(f"Saved {out_path}")
    plt.show()


if __name__ == "__main__":
    main()
