"""Target-aware figures for predicted and observed replicate variability."""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from ml.data.climatology import diagnostic_for
from ml.data.simulation_data import SimulationSamples, try_read_simulation
from ml.data.sweep_file import SweepFile
from ml.diagnostics.errors import profile_rel_l2


def plot_code(label: str, results: list[SimulationSamples]):
    if not results:
        return
    lat = results[0].lat
    for channel, name in enumerate(results[0].metadata.y_vars):
        target = diagnostic_for(name)
        fig, axes = plt.subplots(1, 3, figsize=(14, 5), constrained_layout=True)
        fig.suptitle(f"{label}: {target.label}")
        for index, result in enumerate(results):
            truth, pred = result.truth_profile[channel], result.pred_profile[channel]
            axes[0].plot(truth, lat, "--", label=f"truth r{index}")
            axes[0].plot(pred, lat, label=f"prediction r{index}")
            relative = profile_rel_l2(pred, truth, lat)
            axes[1].plot(pred - truth, lat, label=f"r{index}: relL2={relative:.3f}")
            axes[2].plot(result.predictions[:, channel].std(0), lat, label=f"r{index}")
        for ax, title in zip(
            axes,
            (
                "Replica profiles",
                "Error per replica",
                "Within-simulation prediction standard deviation",
            ),
            strict=True,
        ):
            ax.set_title(title)
            ax.set_xlabel(f"[{target.units}]")
            ax.set_ylabel("latitude [deg]")
            ax.legend()
            ax.grid(alpha=0.3)
        plt.show()


def plot_replicate_variability(
    codes: list[str], experiment_dir: Path, data_cfg, ncols: int = 3
):
    sweep = SweepFile.from_experiment_dir(experiment_dir)
    groups = {}
    for code in codes:
        results = []
        for path in sorted((experiment_dir / "simulations").glob(f"{code}-*")):
            outcome = try_read_simulation(path, data_cfg)
            if outcome.samples is not None:
                results.append(outcome.samples)
        if results:
            groups[code] = results
    if not groups:
        raise ValueError("no simulations satisfy the configured sample contract")
    for channel, name in enumerate(data_cfg.y_vars):
        target = diagnostic_for(name)
        nrows = (len(groups) + ncols - 1) // ncols
        fig, axes = plt.subplots(
            nrows, ncols, figsize=(5 * ncols, 5 * nrows), squeeze=False
        )
        for ax, (code, results) in zip(axes.flat, groups.items()):
            lat = results[0].lat
            profiles = np.stack([r.truth_profile[channel] for r in results])
            mean = profiles.mean(0)
            for profile in profiles:
                ax.plot(profile, lat, alpha=0.2)
            ax.plot(mean, lat, label="replica mean")
            if len(results) > 1:
                std = profiles.std(0)
                ax.fill_betweenx(
                    lat,
                    mean - std,
                    mean + std,
                    alpha=0.2,
                    label="mean +/- population std",
                )
            ax.set_title(f"{sweep.describe(code)}; replicas={len(results)}")
            ax.set_xlabel(f"{target.label} [{target.units}]")
            ax.set_ylabel("latitude [deg]")
            ax.legend()
        for ax in list(axes.flat)[len(groups) :]:
            ax.set_visible(False)
        fig.suptitle(f"Observed replicate variability: {target.label}")
        plt.tight_layout()
        plt.show()
