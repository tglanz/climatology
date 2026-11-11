"""Convergence analysis used by the short and long simulation examples."""

from pathlib import Path
import numpy as np
from ml.data.isca_segment import read_segments, validate_segment_dataset
from ml.diagnostics.enstrophy import mean_enstrophy
from ml.diagnostics.spinup import find_spinup_time
from ml.diagnostics.convergence import (
    find_zonal_mean_convergence_time,
    compute_time_mean_zonal_mean,
    zonal_mean_convergence_errors,
)


def analyze(sim_dir: Path, spinup_config, convergence_config, n_frames: int = 12):
    if n_frames < 1:
        raise ValueError("n_frames must be positive")
    with read_segments(
        str(sim_dir / "run*" / "atmos_daily.nc"), decode_time=True
    ) as ds:
        num_samples, spatial_shape = validate_segment_dataset(
            ds, x_vars=["vor"], y_vars=["ucomp"]
        )
        vor, u, lat = ds.vor.values, ds.ucomp.values, ds.lat.values
    enstrophy = mean_enstrophy(vor, lat)
    spinup_time = find_spinup_time(diagnostic=enstrophy, **spinup_config.to_kwargs())
    if spinup_time is None:
        raise ValueError("Spinup stability criterion not reached")
    t_c = find_zonal_mean_convergence_time(
        u, lat, spinup_time, **convergence_config.to_kwargs()
    )
    if t_c is None:
        raise ValueError("Failed to reach convergence")
    diagnostic_reference = compute_time_mean_zonal_mean(u, spinup_time, num_samples)
    errors = zonal_mean_convergence_errors(u, lat, spinup_time)
    i_values = np.arange(1, len(errors) + 1)
    i_frames = np.linspace(1, num_samples - spinup_time - 1, n_frames).astype(int)
    diagnostics_frames = np.stack(
        [
            compute_time_mean_zonal_mean(u, spinup_time, spinup_time + i)
            for i in i_frames
        ]
    )
    return dict(
        enstrophy=enstrophy,
        spinup_time=spinup_time,
        t_c=t_c,
        diagnostic_reference=diagnostic_reference,
        errors=errors,
        i_values=i_values,
        i_frames=i_frames,
        diagnostics_frames=diagnostics_frames,
        lat=lat,
        num_samples=num_samples,
        spatial_shape=spatial_shape,
    )
