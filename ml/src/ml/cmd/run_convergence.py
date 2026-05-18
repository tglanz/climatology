"""Convergence diagnostic for a single barotropic simulation.

For a fixed simulation, identify the spinup_time from the global
enstrophy series, take D(spinup_time, M) as the long-run reference
diagnostic (here: time-mean zonal-mean u), and plot the relative
area-weighted L2 error of D(spinup_time, spinup_time + i) against i.
The first index where the error drops below CONVERGENCE_THRESHOLD and
stays below for HOLD steps is the convergence_time and is marked on the
plot.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ml.cmd.rotating_globe import load_data
from ml.diagnostics import (
    area_l2_norm,
    compute_enstrophy,
    compute_time_mean_zonal_mean,
    find_spinup_time,
)

EXPERIMENT_DIR = Path("output/barotropic_stirring-T85")
SIM_INDEX = 0
CONVERGENCE_THRESHOLD = 0.05
HOLD = 3


def find_convergence_time(
    errors: np.ndarray, threshold: float, hold: int
) -> int | None:
    below = errors < threshold
    for start in range(len(below) - hold + 1):
        if below[start : start + hold].all():
            return start + 1
    return None


def main():
    sim_dir = EXPERIMENT_DIR / "simulations" / str(SIM_INDEX)
    print(f"Loading {sim_dir}")
    ds = load_data(str(sim_dir))

    vor = ds.vor.values
    u = ds.ucomp.values
    lat = ds.lat.values
    M = vor.shape[0]
    print(f"Loaded {M} snapshots; grid {len(lat)} x {ds.sizes['lon']}")

    enstrophy = compute_enstrophy(vor, lat)
    spinup_time = find_spinup_time(enstrophy)
    print(f"spinup_time = {spinup_time} (out of M = {M})")

    diagnostic_reference = compute_time_mean_zonal_mean(u, spinup_time, M)
    ref_norm = area_l2_norm(diagnostic_reference, lat)

    i_values = np.arange(1, M - spinup_time)
    errors = np.empty(len(i_values))
    for k, i in enumerate(i_values):
        diagnostic_i = compute_time_mean_zonal_mean(u, spinup_time, spinup_time + i)
        errors[k] = area_l2_norm(diagnostic_i - diagnostic_reference, lat) / ref_norm

    convergence_time = find_convergence_time(errors, CONVERGENCE_THRESHOLD, HOLD)
    if convergence_time is None:
        print(
            f"convergence_time not found (relative err never stayed below "
            f"{CONVERGENCE_THRESHOLD} for {HOLD} steps)"
        )
    else:
        print(
            f"convergence_time = {convergence_time}; "
            f"rel err at convergence_time: {errors[convergence_time - 1]:.4f}"
        )
    print(f"Final rel err at i = {i_values[-1]}: {errors[-1]:.2e}")

    out_dir = EXPERIMENT_DIR / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"convergence_sim{SIM_INDEX}.png"

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(i_values, errors, marker="o", markersize=3, linewidth=1)
    ax.axhline(
        CONVERGENCE_THRESHOLD,
        color="gray",
        linestyle=":",
        linewidth=0.8,
        label=f"threshold = {CONVERGENCE_THRESHOLD}",
    )
    if convergence_time is not None:
        ax.axvline(
            convergence_time,
            color="C3",
            linestyle="-",
            linewidth=1.2,
            label=rf"$t_c = {convergence_time}$",
        )
    ax.set_xlabel(r"Window length $i$  (snapshots past $t_s$)")
    ax.set_ylabel(r"$\| D(t_s, t_s+i) - D(t_s, M) \| / \| D(t_s, M) \|$")
    ax.set_title(
        f"Convergence of diagnostic = time-mean zonal-mean u  "
        f"(sim {SIM_INDEX}, $t_s$ = {spinup_time}, M = {M})"
    )
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    print(f"Saved {out_path}")
    plt.show()


if __name__ == "__main__":
    main()
