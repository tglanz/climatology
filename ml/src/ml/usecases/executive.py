from pathlib import Path


from ml.data.isca_segment import read_segment, aggregated_read_field
from ml.diagnostics.enstrophy import mean_enstrophy
from ml.diagnostics.spinup import find_spinup_time

from ml.visualization.executive import (
    plot_vorticity_window,
    plot_vorticity_snapshot,
    plot_climatology,
)

SEGMENT_PATTERN = "run*/atmos_daily.nc"


def run(sim_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    nc_files = sorted(sim_dir.glob(SEGMENT_PATTERN))
    if not nc_files:
        raise FileNotFoundError(
            f"No NC files matching '{SEGMENT_PATTERN}' in {sim_dir}"
        )

    ds0 = read_segment(nc_files[0])
    lat = ds0.lat.values
    lon = ds0.lon.values

    vor = aggregated_read_field(nc_files, "vor")

    enstrophy = mean_enstrophy(vor, lat)
    t_s = find_spinup_time(enstrophy)
    if t_s is None:
        t_s = 0

    snapshots = vor[t_s : t_s + 4]
    if snapshots.shape[0] < 4:
        raise ValueError(f"Not enough timesteps after spinup: t_s={t_s}, T={len(vor)}")

    plot_vorticity_window(
        snapshots[:3], lon, lat, t_s, output_dir / "vorticity_window.png"
    )
    plot_vorticity_snapshot(
        snapshots[3], lon, lat, t_s + 3, output_dir / "vorticity_target.png"
    )

    ucomp = aggregated_read_field(nc_files, "ucomp")
    climatology = ucomp[t_s:].mean(axis=0).mean(axis=-1)
    plot_climatology(climatology, lat, output_dir / "climatology.png")
