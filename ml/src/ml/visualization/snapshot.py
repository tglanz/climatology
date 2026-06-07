from matplotlib import pyplot as plt
from xarray import Dataset

import numpy as np

from ml.data.isca_segment import validate_segment_dataset
from ml.visualization.common import VariableInfo, resolve_variable_info


def plot_variable_snapshot(
        ds: Dataset,
        variable_name: str,
        snapshot_index: int,
        contour_levels: int = 0,
        variable_info: VariableInfo = None):

    variable_info = resolve_variable_info(variable_name, variable_info)

    validate_segment_dataset(ds, x_vars=[variable_name], y_vars=[])
    lon, lat = ds.lon.values, ds.lat.values
    snapshot = ds[variable_name].values[snapshot_index]
    vmax = np.percentile(np.abs(snapshot), 98)

    fig, ax = plt.subplots(figsize=(12, 5), layout="constrained")
    im = ax.pcolormesh(lon, lat, snapshot, cmap="RdBu_r", vmin=-vmax, vmax=vmax, shading="auto")
    if contour_levels > 0:
        ax.contour(lon, lat, snapshot, levels=contour_levels, colors="k", linewidths=0.5, alpha=0.4)
    fig.colorbar(im, ax=ax, label=f"{variable_info.label} [{variable_info.units}]")
    ax.set_title(f"{variable_info.label} (t={snapshot_index})")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    plt.show()
