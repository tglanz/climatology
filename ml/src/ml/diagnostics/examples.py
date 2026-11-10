"""Exploratory approximations retained for comparison, not solver residual guarantees."""

import numpy as np
from scipy.ndimage import gaussian_filter


def synthetic_prediction(ds):
    rng = np.random.default_rng(42)

    # Use first time step as "truth", blur it as "prediction"
    VOR_TRUE = ds.vor.isel(time=0).values
    VOR_PRED = (
        gaussian_filter(VOR_TRUE, sigma=1.5)
        + 0.08 * rng.standard_normal(VOR_TRUE.shape) * VOR_TRUE.std()
    )
    return VOR_TRUE, VOR_PRED


def advection_residual(ds, earth_radius=6.371e6, dt=86400.0):
    lon, lat = ds.lon.values, ds.lat.values
    lat_rad = np.deg2rad(lat)
    dlat = lat_rad[1] - lat_rad[0]
    dlon = np.deg2rad(lon[1] - lon[0])
    cos_lat_2d = np.cos(np.deg2rad(lat))[:, None] * np.ones((1, len(lon)))
    cos_lat_2d = cos_lat_2d.clip(1e-6)
    vor0 = ds.vor.isel(time=0).values
    vor1 = ds.vor.isel(time=1).values
    u0 = ds.ucomp.isel(time=0).values
    v0 = ds.vcomp.isel(time=0).values
    dvdt = (vor1 - vor0) / dt
    dvor_dx = np.gradient(vor0, dlon, axis=1) / (earth_radius * cos_lat_2d)
    dvor_dy = np.gradient(vor0, dlat, axis=0) / earth_radius
    advection = u0 * dvor_dx + v0 * dvor_dy
    return dvdt + advection
