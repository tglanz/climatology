from matplotlib import pyplot as plt
from xarray import Dataset

import numpy as np

from ml.data.isca_segment import validate_segment_dataset
from ml.visualization.common import VariableInfo, resolve_variable_info


def plot_variable_evolution(
        ds: Dataset, variable_name: str,
        num_frames: int = 10, num_cols: int = 5,
        contour_levels: int = 0,
        variable_info: VariableInfo = None):

    variable_info = resolve_variable_info(variable_name, variable_info)

    num_samples, _ = validate_segment_dataset(ds, x_vars=[variable_name], y_vars=[])
    lon, lat, variable = ds.lon.values, ds.lat.values, ds[variable_name].values

    vmax = np.percentile(np.abs(variable), 98)
    indices = np.linspace(0, num_samples - 1, num_frames).astype(int)

    num_rows = int(np.ceil(num_frames / num_cols))
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(18, 4 * num_rows), sharey=True, layout="constrained")
    for i, idx in enumerate(indices):
        ax = axes.flat[i]
        im = ax.pcolormesh(lon, lat, variable[idx], cmap="RdBu_r", vmin=-vmax, vmax=vmax, shading="auto")
        if contour_levels > 0:
            ax.contour(lon, lat, variable[idx], levels=contour_levels, colors="k", linewidths=0.5, alpha=0.4)
        ax.set_title(f"t={idx}")

        if i // num_cols == num_rows - 1:
            ax.set_xlabel("Longitude [deg]")

        if i % num_cols == 0:
            ax.set_ylabel("Latitude [deg]")

    for j in range(num_frames, num_rows * num_cols):
        axes.flat[j].set_visible(False)

    fig.colorbar(im, ax=axes, label=f"{variable_info.label} [{variable_info.units}]", shrink=0.8)
    fig.suptitle(f"Evolution of {variable_info.label}", y=1.02)
    plt.show()
