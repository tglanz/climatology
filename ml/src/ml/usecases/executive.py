from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ml.data.isca_segment import read_segment, aggregated_read_field
from ml.diagnostics.enstrophy import mean_enstrophy
from ml.diagnostics.spinup import find_spinup_time

SEGMENT_PATTERN = "run*/atmos_daily.nc"


def run(sim_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    nc_files = sorted(sim_dir.glob(SEGMENT_PATTERN))
    if not nc_files:
        raise FileNotFoundError(f"No NC files matching '{SEGMENT_PATTERN}' in {sim_dir}")

    ds0 = read_segment(nc_files[0])
    lat = ds0.lat.values
    lon = ds0.lon.values

    vor = aggregated_read_field(nc_files, "vor")

    enstrophy = mean_enstrophy(vor, lat)
    t_s = find_spinup_time(enstrophy)
    if t_s is None:
        t_s = 0

    snapshots = vor[t_s:t_s + 4]
    if snapshots.shape[0] < 4:
        raise ValueError(f"Not enough timesteps after spinup: t_s={t_s}, T={len(vor)}")

    _plot_vorticity_window(snapshots[:3], lon, lat, t_s, output_dir / "vorticity_window.png")
    _plot_vorticity_snapshot(snapshots[3], lon, lat, t_s + 3, output_dir / "vorticity_target.png")

    ucomp = aggregated_read_field(nc_files, "ucomp")
    climatology = ucomp[t_s:].mean(axis=0).mean(axis=-1)
    _plot_climatology(climatology, lat, output_dir / "climatology.png")


def _plot_vorticity_window(
    snapshots: np.ndarray, lon: np.ndarray, lat: np.ndarray, t_start: int, path: Path
) -> None:
    vmax = np.percentile(np.abs(snapshots), 98)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), layout="constrained")
    for i, ax in enumerate(axes):
        im = ax.pcolormesh(lon, lat, snapshots[i], cmap="RdBu_r", vmin=-vmax, vmax=vmax, shading="auto")
        ax.set_title(f"vorticity (t={t_start + i})")
        ax.set_xlabel("longitude [deg]")
        ax.set_ylabel("latitude [deg]")
        fig.colorbar(im, ax=ax, label="vor [1/s]")
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_vorticity_snapshot(
    snapshot: np.ndarray, lon: np.ndarray, lat: np.ndarray, t: int, path: Path
) -> None:
    vmax = np.percentile(np.abs(snapshot), 98)
    fig, ax = plt.subplots(figsize=(12, 5), layout="constrained")
    im = ax.pcolormesh(lon, lat, snapshot, cmap="RdBu_r", vmin=-vmax, vmax=vmax, shading="auto")
    ax.set_title(f"vorticity (t={t})")
    ax.set_xlabel("longitude [deg]")
    ax.set_ylabel("latitude [deg]")
    fig.colorbar(im, ax=ax, label="vor [1/s]")
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_climatology(profile: np.ndarray, lat: np.ndarray, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(5, 7), layout="constrained")
    ax.plot(profile, lat, color="black", linewidth=1.5)
    ax.axvline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xlabel("u [m/s]")
    ax.set_ylabel("latitude [deg]")
    ax.set_ylim(-90, 90)
    ax.set_title(r"$[\bar{u}]$ climatology")
    ax.grid(alpha=0.3)
    fig.savefig(path, dpi=150)
    plt.close(fig)
