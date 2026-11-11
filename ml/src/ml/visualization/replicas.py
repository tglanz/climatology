"""Figures comparing predictions and truth across replicas."""

import numpy as np
import matplotlib.pyplot as plt
from ml.diagnostics.errors import notebook_profile_rel_l2 as rel_l2


def plot_code(label: str, results: list[dict]):
    n = len(results)
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), constrained_layout=True)
    fig.suptitle(label, fontsize=10)
    lat = results[0]["lat"]

    pred_colors = plt.get_cmap("tab10")(np.linspace(0, 0.9, n))
    gray_levels = np.linspace(0.3, 0.65, n)
    truth_colors = [np.array([v, v, v, 1.0]) for v in gray_levels]

    ax = axes[0]
    for i, res in enumerate(results):
        ax.plot(
            res["truth"],
            lat,
            color=truth_colors[i],
            linestyle="--",
            linewidth=1.4,
            label=f"truth r{i}",
        )
        ax.plot(
            res["mean_pred"],
            lat,
            color=pred_colors[i],
            linewidth=1.5,
            label=f"pred r{i}",
        )
    ax.axvline(0.0, color="k", linewidth=0.4, alpha=0.4)
    ax.set_xlabel("u [m/s]")
    ax.set_ylabel("lat [deg]")
    ax.set_title("truth (gray dashed) vs prediction (colored)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    for i, res in enumerate(results):
        err = res["mean_pred"] - res["truth"]
        rl = rel_l2(res["mean_pred"], res["truth"], lat)
        ax.plot(err, lat, color=pred_colors[i], linewidth=1.2, label=f"r{i}  {rl:.3f}")
    ax.axvline(0.0, color="k", linewidth=0.8, linestyle="--")
    ax.set_xlabel("error (pred - truth) [m/s]")
    ax.set_title("error per replicate")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    for i, res in enumerate(results):
        ax.plot(
            res["predictions"].std(axis=0),
            lat,
            color=pred_colors[i],
            linewidth=1.2,
            label=f"r{i}",
        )
    ax.set_xlabel("prediction std [m/s]")
    ax.set_title("within-sim window variance")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    plt.show()


from pathlib import Path
from tqdm.auto import tqdm
from ml.data.evaluation import load_profile
from ml.data.sweep_file import SweepFile


def _plot_code(
    code: str, profiles: np.ndarray, latitudes: np.ndarray, t_cs: list, ax, sweep
):
    mean_profile = profiles.mean(axis=0)
    std_profile = profiles.std(axis=0)
    params = sweep.params_for(code)
    lat0 = params["stirring_lat0"] if params else None
    jet_lat = latitudes[np.argmax(np.abs(mean_profile))]
    valid_t_cs = [t for t in t_cs if t is not None]
    mean_t_c = np.mean(valid_t_cs) if valid_t_cs else float("nan")

    for profile in profiles:
        ax.plot(profile, latitudes, color="tab:blue", alpha=0.08, linewidth=0.8)
    ax.fill_betweenx(
        latitudes,
        mean_profile - std_profile,
        mean_profile + std_profile,
        color="gray",
        alpha=0.35,
        label="mean +/- std",
    )
    ax.plot(mean_profile, latitudes, color="tab:orange", linewidth=2, label="mean")
    ax.axvline(0, color="k", linewidth=0.5, linestyle="--")
    if lat0 is not None:
        ax.axhline(
            lat0, color="tab:red", linewidth=1.2, linestyle="--", label=f"lat0={lat0}"
        )
    ax.axhline(
        jet_lat,
        color="tab:green",
        linewidth=1.2,
        linestyle="--",
        label=f"jet={jet_lat:.1f}",
    )
    ax.set_xlabel("zonal-mean zonal wind [m/s]")
    ax.set_ylabel("latitude [deg]")
    ax.set_ylim(-90, 90)
    ax.set_title(
        f"{sweep.describe(code)}  [{code}]\nconv={mean_t_c:.1f} days  std={std_profile.mean():.3f}"
    )
    ax.legend(fontsize=7)


def plot_noise_floor(
    codes: list[str], experiment_dir: Path, spinup_cfg, convergence_cfg, ncols: int = 3
):
    sweep = SweepFile.from_experiment_dir(experiment_dir)
    nrows = -(-len(codes) // ncols)

    jobs = [
        (code, d)
        for code in codes
        for d in sorted(
            (experiment_dir / "simulations").glob(code + "-*"),
            key=lambda p: p.name,
        )
        if list(d.glob("run*/atmos_daily.nc"))
    ]

    raw = {code: [] for code in codes}
    for code, d in tqdm(jobs, desc="loading"):
        lat, profile, t_c = load_profile(d, spinup_cfg, convergence_cfg)
        raw[code].append((lat, profile, t_c))

    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 5))
    axes_flat = np.array(axes).flat

    for code, ax in zip(codes, axes_flat):
        latitudes = raw[code][0][0]
        profiles = np.stack([r[1] for r in raw[code]])
        t_cs = [r[2] for r in raw[code]]
        _plot_code(code, profiles, latitudes, t_cs, ax, sweep)

    for ax in list(axes_flat)[len(codes) :]:
        ax.set_visible(False)

    plt.tight_layout()
    plt.show()

    # std bar chart
    labels = [sweep.describe(c) for c in codes]
    stds = [np.stack([r[1] for r in raw[c]]).std(axis=0).mean() for c in codes]
    fig2, ax2 = plt.subplots(figsize=(len(codes) * 1.5, 4))
    ax2.bar(labels, stds, color="tab:blue")
    ax2.set_ylabel("mean std of climatology profiles")
    ax2.set_title("within-config noise floor per parameter config")
    plt.tight_layout()
    plt.show()
