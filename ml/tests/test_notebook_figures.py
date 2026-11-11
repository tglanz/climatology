"""Exercise extracted plots independently of notebook execution order."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest
import xarray as xr
from ml.visualization import barotropic


@pytest.mark.parametrize(
    "name",
    [
        "plot_hovmoller",
        "plot_normalized_enstrophy",
        "plot_rossby_waves",
        "plot_wind_vectors",
        "plot_normalized_energy",
        "plot_jet_structure",
        "plot_wind_direction",
        "plot_polar_views",
        "plot_globe_fields",
        "plot_globe_evolution",
    ],
)
def test_field_view_has_no_notebook_global_dependencies(name, monkeypatch):
    values = np.arange(6 * 4 * 16, dtype=float).reshape(6, 4, 16) / 100 + 1
    ds = xr.Dataset(
        {
            name: (("time", "lat", "lon"), values + offset)
            for name, offset in [
                ("vor", 0.0),
                ("ucomp", 1.0),
                ("vcomp", 2.0),
                ("stream", 3.0),
            ]
        },
        coords={
            "time": np.arange(6),
            "lat": [-65.0, -20.0, 20.0, 65.0],
            "lon": np.arange(16) * 22.5,
        },
    )
    monkeypatch.setattr(plt, "show", lambda: None)
    try:
        getattr(barotropic, name)(ds)
        assert plt.get_fignums()
        plt.gcf().canvas.draw()
    finally:
        plt.close("all")
