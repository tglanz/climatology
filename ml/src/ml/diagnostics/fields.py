"""Derived barotropic fields used by globe views."""

import numpy as np


def jet_stream(ds):
    """Time-mean zonal wind -- reveals persistent jet structure."""
    return ds.ucomp.mean(dim="time").values


def wind_speed(ds):
    """Instantaneous wind speed sqrt(u^2 + v^2)."""
    return np.sqrt(ds.ucomp.values**2 + ds.vcomp.values**2)


def eddy_streamfunction(ds):
    """Streamfunction with zonal mean removed: psi' = psi - [psi]."""
    psi = ds.stream.values
    return psi - psi.mean(axis=2, keepdims=True)
