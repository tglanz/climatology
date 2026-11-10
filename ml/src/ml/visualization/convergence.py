"""Convergence diagnostic figures, preserving the original notebook curves."""

import numpy as np
import matplotlib.pyplot as plt


def plot_enstrophy(enstrophy):
    fig, ax = plt.subplots(figsize=(8, 3.5))
    plt.plot(enstrophy)
    ax.set_title("Mean Enstrophy over time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Mean Enstrophy")


def plot_spinup(enstrophy, spinup_time):
    if spinup_time:
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(enstrophy, marker="o", markersize=3)
        ax.axvline(
            spinup_time,
            color="C3",
            linestyle="-",
            linewidth=1.2,
            label=rf"$t_s = {spinup_time}$",
        )
        ax.set_xlabel("snapshot index")
        ax.set_ylabel("global mean enstrophy")
        ax.set_title("Enstrophy time series with detected spinup_time")
        ax.legend()
        plt.tight_layout()
        plt.show()


def plot_convergence(
    i_values, errors, spinup_time, t_c, num_samples, convergence_config
):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(i_values, errors, marker="o", markersize=3, linewidth=1)
    ax.axhline(
        convergence_config.threshold,
        color="gray",
        linestyle=":",
        linewidth=0.8,
        label=f"threshold = {convergence_config.threshold}",
    )
    ax.axvline(
        spinup_time,
        color="C2",
        linestyle="-",
        linewidth=1.2,
        label=rf"$t_s = {spinup_time}$",
    )
    if t_c is not None:
        ax.axvline(
            t_c, color="C3", linestyle="-", linewidth=1.2, label=rf"$t_c = {t_c}$"
        )
    ax.set_xlabel(r"Window length $i$  (snapshots past $t_s$)")
    ax.set_ylabel(r"$\| D(t_s, t_s+i) - D(t_c, M) \| / \| D(t_c, M) \|$")
    ax.set_title(
        f"Convergence of diagnostic = time-mean zonal-mean u  ($t_s$ = {spinup_time}, M = {num_samples})"
    )
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_profile_evolution(
    i_frames, diagnostics_frames, diagnostic_reference, lat, title=None
):
    N_FRAMES = len(i_frames)
    ncols = 5
    nrows = (N_FRAMES + ncols - 1) // ncols
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(ncols * 2.4, nrows * 3.0),
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )

    for k, i in enumerate(i_frames):
        ax = axes.flat[k]
        ax.plot(diagnostic_reference, lat, color="C3", linewidth=1.4)
        ax.plot(diagnostics_frames[k], lat, color="C0", linewidth=1.4)
        ax.axvline(0.0, color="k", linewidth=0.4, alpha=0.5)
        ax.set_title(f"i = {i}", fontsize=10)
        if k % ncols == 0:
            ax.set_ylabel("lat [deg]")
        if k >= (nrows - 1) * ncols:
            ax.set_xlabel("u [m/s]")

    fig.suptitle(
        title or r"Evolution of $D(t_s, t_s+i)$ (blue) toward $D(t_s, M)$ (red)"
    )
    plt.show()
