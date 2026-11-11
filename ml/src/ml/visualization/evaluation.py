"""
Plot functions for model evaluation.

All functions return a matplotlib Figure. No plt.show() or file saving
is done here -- that is the orchestrator's responsibility.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def plot_baselines_bar(
    names: list[str],
    scores: list[float],
    highlight_idx: int,
) -> plt.Figure:
    """Bar chart of relL2 for each baseline predictor plus the model."""
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["tab:gray"] * len(names)
    colors[highlight_idx] = "tab:blue"
    ax.bar(names, scores, color=colors, edgecolor="black", linewidth=0.6)
    ax.set_ylabel("mean relL2")
    ax.set_title("Baseline comparison (test split)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_baselines_profiles(
    lat: np.ndarray,
    truth_mean: np.ndarray,
    pred_profiles: dict[str, np.ndarray],
) -> plt.Figure:
    """Overlay of mean truth and each baseline predictor's mean prediction."""
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(truth_mean, lat, color="black", linewidth=1.8, label="truth mean")
    linestyles = ["-", "--", "-.", ":"]
    for i, (name, profile) in enumerate(pred_profiles.items()):
        ls = linestyles[i % len(linestyles)]
        ax.plot(profile, lat, linestyle=ls, linewidth=1.4, label=name)
    ax.set_xlabel("u [m/s]")
    ax.set_ylabel("lat [deg]")
    ax.set_title("Mean profiles: truth vs predictors")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def plot_training_curve(csv_path: Path) -> plt.Figure:
    import csv

    epochs, train_loss, val_loss = [], [], []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            epochs.append(int(row["epoch"]))
            train_loss.append(float(row["train_loss"]))
            val_loss.append(float(row["val_loss"]))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(epochs, train_loss, label="train", color="tab:blue")
    ax.plot(epochs, val_loss, label="val", color="tab:orange", linestyle="--")
    ax.set_xlabel("epoch")
    ax.set_ylabel("loss")
    ax.set_title("Training curve")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def plot_noise_floor_summary(
    codes: list[str],
    noise_rels: list[float],
    model_rels: list[float],
) -> plt.Figure:
    """Sorted bar chart of across-replicate noise floor with model relL2 overlaid."""
    order = np.argsort(noise_rels)
    sorted_codes = [codes[i] for i in order]
    sorted_noise = [noise_rels[i] for i in order]
    sorted_model = [model_rels[i] for i in order]

    x = np.arange(len(sorted_codes))
    fig, ax = plt.subplots(figsize=(max(8, len(codes) * 0.35), 4))
    ax.bar(
        x,
        sorted_noise,
        color="tab:gray",
        alpha=0.6,
        label="noise floor",
        edgecolor="none",
    )
    ax.scatter(x, sorted_model, color="tab:blue", s=18, zorder=3, label="model relL2")
    ax.set_xticks(x)
    ax.set_xticklabels(sorted_codes, rotation=90, fontsize=6)
    ax.set_ylabel("relL2")
    ax.set_title("Noise floor vs model relL2 (per config code)")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_generalization_param(
    param_name: str,
    param_values: list[float],
    model_rels: list[float],
    split_labels: list[str],
) -> plt.Figure:
    """Scatter of relL2 vs parameter value, colored by split."""
    split_order = ["train", "val", "test", "unknown"]
    palette = {
        "train": "tab:blue",
        "val": "tab:orange",
        "test": "tab:red",
        "unknown": "tab:gray",
    }
    fig, ax = plt.subplots(figsize=(6, 4))
    added = set()
    for pv, rel, spl in zip(param_values, model_rels, split_labels):
        color = palette.get(spl, "tab:gray")
        label = spl if spl not in added else None
        ax.scatter(pv, rel, color=color, s=40, label=label, alpha=0.8)
        added.add(spl)
    ax.set_xlabel(param_name)
    ax.set_ylabel("mean relL2")
    ax.set_title(f"Generalization: relL2 vs {param_name}")
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def plot_generalization_worst(
    lat: np.ndarray,
    worst_cases: list[tuple[str, np.ndarray, np.ndarray, float]],
) -> plt.Figure:
    """Profile overlays for the 6 worst-scoring config codes."""
    n = len(worst_cases)
    ncols = 3
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(ncols * 3.5, nrows * 3.5), constrained_layout=True
    )
    axes_flat = list(np.array(axes).flat) if n > 1 else [axes]
    for k, (code, truth_p, pred_p, rel) in enumerate(worst_cases):
        ax = axes_flat[k]
        ax.plot(truth_p, lat, color="tab:orange", linewidth=1.4, label="truth")
        ax.plot(
            pred_p, lat, color="tab:blue", linewidth=1.4, linestyle="--", label="pred"
        )
        ax.set_title(f"{code}  relL2={rel:.3f}", fontsize=8)
        ax.set_xlabel("u [m/s]", fontsize=7)
        if k % ncols == 0:
            ax.set_ylabel("lat [deg]", fontsize=7)
        if k == 0:
            ax.legend(fontsize=7)
        ax.grid(alpha=0.3)
    for ax in axes_flat[n:]:
        ax.set_visible(False)
    fig.suptitle("Worst 6 config codes by relL2")
    return fig


def plot_error_bias(
    lat: np.ndarray,
    errors: np.ndarray,
) -> plt.Figure:
    """Fan plot of per-sample (pred - truth) vs latitude with mean bias."""
    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(min(errors.shape[0], 500)):
        ax.plot(errors[i], lat, color="tab:blue", linewidth=0.5, alpha=0.1)
    mean_err = errors.mean(axis=0)
    ax.plot(mean_err, lat, color="tab:red", linewidth=1.8, label="mean bias")
    ax.axvline(0.0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("error (pred - truth) [m/s]")
    ax.set_ylabel("lat [deg]")
    ax.set_title("Prediction bias by latitude (test split)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def plot_error_histogram(
    rel_l2_vals: np.ndarray,
) -> plt.Figure:
    """Histogram of per-sample relL2."""
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.hist(rel_l2_vals, bins=40, edgecolor="black", linewidth=0.4)
    median = float(np.median(rel_l2_vals))
    ax.axvline(
        median,
        color="tab:red",
        linewidth=1.4,
        linestyle="--",
        label=f"median={median:.4f}",
    )
    ax.set_xlabel("relL2")
    ax.set_ylabel("count")
    ax.set_title("Per-sample relL2 distribution (test split)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def plot_jet_scatter(
    truth_vals: np.ndarray,
    pred_vals: np.ndarray,
    xlabel: str,
    ylabel: str,
    title: str,
) -> plt.Figure:
    """Scatter of predicted vs truth values (jet lat or amplitude)."""
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(truth_vals, pred_vals, s=8, alpha=0.4, color="tab:blue")
    lo = min(truth_vals.min(), pred_vals.min())
    hi = max(truth_vals.max(), pred_vals.max())
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=0.8, label="y=x")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def plot_model_vs_noise_floor(
    codes: list[str],
    noise_rels: list[float],
    model_rels: list[float],
    split_labels: list[str],
) -> plt.Figure:
    """Scatter of model relL2 vs noise floor relL2, one point per config code.

    Points above the diagonal have model error exceeding the noise floor.
    Points on or below the diagonal are near the achievable limit.
    """
    palette = {
        "train": "tab:blue",
        "val": "tab:orange",
        "test": "tab:red",
        "unknown": "tab:gray",
    }
    fig, ax = plt.subplots(figsize=(6, 6))
    added: set[str] = set()
    for code, nf, mr, spl in zip(codes, noise_rels, model_rels, split_labels):
        color = palette.get(spl, "tab:gray")
        label = spl if spl not in added else None
        ax.scatter(nf, mr, color=color, s=40, alpha=0.85, label=label, zorder=3)
        added.add(spl)
    lo = 0.0
    hi = max(max(noise_rels), max(model_rels)) * 1.1
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=0.8, label="model = noise floor")
    ax.set_xlabel("noise floor relL2 (replicate std)")
    ax.set_ylabel("model relL2")
    ax.set_title("Model error vs noise floor per config")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig
