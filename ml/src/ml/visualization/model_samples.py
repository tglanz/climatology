"""Prepared-sample evaluation figures."""

import numpy as np
import matplotlib.pyplot as plt
from ml.diagnostics.errors import notebook_profile_rel_l2 as rel_l2


def plot_sample_profiles(preds_all, truth_all, lat, n_show=12):
    N_SHOW = n_show
    rng = np.random.default_rng(0)
    idx = np.sort(
        rng.choice(len(preds_all), size=min(N_SHOW, len(preds_all)), replace=False)
    )

    ncols = 4
    nrows = (len(idx) + ncols - 1) // ncols
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(ncols * 2.8, nrows * 3.2),
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )
    axes_flat = list(np.array(axes).flat)

    for k, i in enumerate(idx):
        ax = axes_flat[k]
        ax.plot(preds_all[i], lat, color="tab:blue", linewidth=1.5, label="pred")
        ax.plot(
            truth_all[i],
            lat,
            color="tab:orange",
            linestyle="--",
            linewidth=1.5,
            label="truth",
        )
        ax.axvline(0.0, color="k", linewidth=0.4, alpha=0.4)
        rl = rel_l2(preds_all[i], truth_all[i], lat)
        ax.set_title(f"sample {i}  relL2={rl:.3f}", fontsize=8)
        ax.set_xlabel("u [m/s]", fontsize=8)
        if k % ncols == 0:
            ax.set_ylabel("lat [deg]")
        if k == 0:
            ax.legend(fontsize=8)

    for ax in axes_flat[len(idx) :]:
        ax.set_visible(False)

    fig.suptitle("Truth (orange) vs prediction (blue): random test samples")
    plt.show()


def plot_sample_errors(preds_all, truth_all, lat):
    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(len(preds_all)):
        ax.plot(
            preds_all[i] - truth_all[i],
            lat,
            alpha=0.15,
            linewidth=0.8,
            color="tab:blue",
        )
    mean_err = (preds_all - truth_all).mean(axis=0)
    ax.plot(mean_err, lat, color="tab:red", linewidth=1.5, label="mean error")
    ax.axvline(0.0, color="k", linewidth=0.8, linestyle="--")
    ax.set_xlabel("error  (pred - truth) [m/s]")
    ax.set_ylabel("lat [deg]")
    ax.set_title("Prediction error by latitude (all test samples)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_sample_scatter(preds_all, truth_all):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(truth_all.ravel(), preds_all.ravel(), s=1, alpha=0.1, color="tab:blue")
    lo = min(truth_all.min(), preds_all.min())
    hi = max(truth_all.max(), preds_all.max())
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=0.8, label="y=x")
    ax.set_xlabel("truth [m/s]")
    ax.set_ylabel("prediction [m/s]")
    ax.set_title("Truth vs prediction at each latitude (all test samples)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_sample_distribution(rmses, rels):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))

    for ax, name, vals in [(axes[0], "RMSE", rmses), (axes[1], "relative L2", rels)]:
        ax.hist(vals, bins=30, edgecolor="k", linewidth=0.4)
        ax.axvline(
            np.median(vals),
            color="tab:red",
            linewidth=1.2,
            linestyle="--",
            label=f"median={np.median(vals):.4f}",
        )
        ax.set_xlabel(name)
        ax.set_ylabel("count")
        ax.set_title(f"Per-sample {name} distribution")
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
