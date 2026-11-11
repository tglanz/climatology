"""Target-aware prepared-window figures using saved physical coordinates."""

import numpy as np
import matplotlib.pyplot as plt

from ml.data.climatology import diagnostic_for
from ml.diagnostics.errors import profile_rel_l2
from ml.usecases.evaluate_samples import SampleEvaluation


def _channels(result: SampleEvaluation):
    if len(result.predictions) == 0:
        raise ValueError("no prepared test windows to plot")
    for index, name in enumerate(result.metadata.y_vars):
        yield index, diagnostic_for(name)


def plot_sample_profiles(result: SampleEvaluation, n_show=12):
    if n_show < 1:
        raise ValueError("n_show must be positive")
    indices = np.sort(
        np.random.default_rng(0).choice(
            len(result.predictions), min(n_show, len(result.predictions)), replace=False
        )
    )
    figures = []
    for channel, target in _channels(result):
        ncols = min(4, len(indices))
        nrows = (len(indices) + ncols - 1) // ncols
        fig, axes = plt.subplots(
            nrows,
            ncols,
            figsize=(ncols * 2.8, nrows * 3.2),
            squeeze=False,
            constrained_layout=True,
        )
        for ax, index in zip(axes.flat, indices):
            prediction, truth = (
                result.predictions[index, channel],
                result.truth[index, channel],
            )
            ax.plot(prediction, result.latitudes, label="prediction")
            ax.plot(truth, result.latitudes, "--", label="truth")
            ax.set_title(
                f"window {index}: relL2={profile_rel_l2(prediction,truth,result.latitudes):.3f}"
            )
            ax.set_xlabel(f"{target.label} [{target.units}]")
            ax.set_ylabel("latitude [deg]")
            ax.legend()
        for ax in list(axes.flat)[len(indices) :]:
            ax.set_visible(False)
        figures.append(fig)
        plt.show()
    return figures


def plot_sample_errors(result: SampleEvaluation):
    figures = []
    for channel, target in _channels(result):
        errors = result.predictions[:, channel] - result.truth[:, channel]
        fig, ax = plt.subplots(figsize=(6, 5))
        for error in errors:
            ax.plot(error, result.latitudes, alpha=0.15)
        ax.plot(errors.mean(0), result.latitudes, color="red", label="mean error")
        ax.set_xlabel(f"prediction - truth [{target.units}]")
        ax.set_ylabel("latitude [deg]")
        ax.set_title(f"Prepared-window errors: {target.label}")
        ax.legend()
        figures.append(fig)
        plt.show()
    return figures


def plot_sample_scatter(result: SampleEvaluation):
    figures = []
    for channel, target in _channels(result):
        truth, prediction = result.truth[:, channel], result.predictions[:, channel]
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.scatter(truth.ravel(), prediction.ravel(), s=1, alpha=0.1)
        low, high = min(truth.min(), prediction.min()), max(
            truth.max(), prediction.max()
        )
        ax.plot([low, high], [low, high], "k--")
        ax.set_xlabel(f"truth [{target.units}]")
        ax.set_ylabel(f"prediction [{target.units}]")
        ax.set_title(f"Prepared windows: {target.label}")
        figures.append(fig)
        plt.show()
    return figures


def plot_sample_distribution(result: SampleEvaluation):
    figures = []
    for channel, target in _channels(result):
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
        for ax, name, values in (
            (axes[0], f"RMSE [{target.units}]", result.rmses[:, channel]),
            (axes[1], "relative L2", result.relatives[:, channel]),
        ):
            finite = values[np.isfinite(values)]
            if len(finite):
                ax.hist(finite, bins=30)
                ax.axvline(
                    np.median(finite),
                    color="red",
                    label=f"median={np.median(finite):.3g}",
                )
                ax.legend()
            ax.set_xlabel(name)
            ax.set_ylabel("windows")
            ax.set_title(f"included={len(finite)}, undefined={len(values)-len(finite)}")
        fig.suptitle(target.label)
        figures.append(fig)
        plt.show()
    return figures
