"""Figures for the historical executive-summary talk."""

from pathlib import Path
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_vorticity_window(
    snapshots: np.ndarray, lon: np.ndarray, lat: np.ndarray, t_start: int, path: Path
) -> None:
    vmax = np.percentile(np.abs(snapshots), 98)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), layout="constrained")
    for i, ax in enumerate(axes):
        im = ax.pcolormesh(
            lon, lat, snapshots[i], cmap="RdBu_r", vmin=-vmax, vmax=vmax, shading="auto"
        )
        ax.set_title(f"vorticity (t={t_start + i})")
        ax.set_xlabel("longitude [deg]")
        ax.set_ylabel("latitude [deg]")
        fig.colorbar(im, ax=ax, label="vor [1/s]")
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_vorticity_snapshot(
    snapshot: np.ndarray, lon: np.ndarray, lat: np.ndarray, t: int, path: Path
) -> None:
    vmax = np.percentile(np.abs(snapshot), 98)
    fig, ax = plt.subplots(figsize=(12, 5), layout="constrained")
    im = ax.pcolormesh(
        lon, lat, snapshot, cmap="RdBu_r", vmin=-vmax, vmax=vmax, shading="auto"
    )
    ax.set_title(f"vorticity (t={t})")
    ax.set_xlabel("longitude [deg]")
    ax.set_ylabel("latitude [deg]")
    fig.colorbar(im, ax=ax, label="vor [1/s]")
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_climatology(profile: np.ndarray, lat: np.ndarray, path: Path) -> None:
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
