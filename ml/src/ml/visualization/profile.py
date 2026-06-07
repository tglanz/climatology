from matplotlib import pyplot as plt
from xarray import Dataset

import numpy as np

from ml.data.isca_segment import validate_segment_dataset
from ml.visualization.common import VariableInfo, resolve_variable_info


def plot_zonal_mean_profile(
        ds: Dataset, variable_name: str,
        time_fraction: float = 1.0,
        variable_info: VariableInfo = None):

    assert 0.0 < time_fraction <= 1.0, "time_fraction must be in (0, 1]"

    variable_info = resolve_variable_info(variable_name, variable_info)

    num_samples, _ = validate_segment_dataset(ds, x_vars=[variable_name], y_vars=[])
    num_plot = max(1, int(num_samples * time_fraction))
    indices = np.linspace(0, num_samples - 1, num_plot).astype(int)
    lat = ds.lat.values
    variable = ds[variable_name].values[indices]
    zonal_mean = variable.mean(axis=2)

    cmap = plt.cm.viridis
    colors = cmap(np.linspace(0, 1, num_plot))

    fig, ax = plt.subplots(figsize=(6, 7), layout="constrained")
    for t in range(num_plot):
        ax.plot(zonal_mean[t], lat, color=colors[t], alpha=0.5, linewidth=0.8)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(indices[0], indices[-1]))
    sm.set_array([])
    fig.colorbar(sm, ax=ax, label="Time index")
    ax.axvline(0, color="k", linewidth=0.5)
    ax.set_xlabel(f"Zonal Mean {variable_info.label} [{variable_info.units}]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title(f"Zonal Mean of {variable_info.label}")
    plt.show()
