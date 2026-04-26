"""Generate a rotating globe GIF from Isca barotropic simulation output.

Usage examples:
    # Evolving vorticity (default)
    python rotating_globe.py --input-path ../output/barotropic_stirring-T85

    # Single time step, PV field, custom colormap
    python rotating_globe.py --input-path ../output/barotropic_stirring-T85 \
        --time 50 --diagnostic pv --cmap PuOr --output-path pv_globe.gif

    # High quality, slow rotation
    python rotating_globe.py --input-path ../output/barotropic_stirring-T85 \
        --n-frames 180 --fps 12 --dpi 150 --rotations 0.5
"""

import argparse
from pathlib import Path

import cartopy.crs as ccrs
from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from tqdm import tqdm

DIVERGING_FIELDS = {
    "vor",
    "vcomp",
    "ucomp",
    "pv",
    "stream",
    "eddy_vor",
    "delta_u",
    "stirring",
}
SEQUENTIAL_FIELDS = {"tr", "trs", "stirring_amp", "stirring_sqr"}

DEFAULT_CMAPS = {
    "vor": "RdBu_r",
    "pv": "PuOr",
    "stream": "RdBu_r",
    "ucomp": "RdBu_r",
    "vcomp": "RdBu_r",
    "tr": "viridis",
}


# --- Computed diagnostics ---
# Each entry: (description, compute_fn, is_static)
#   compute_fn(ds) -> np.ndarray with shape (lat, lon) if static, (time, lat, lon) if not
#   is_static: True means the field is time-independent (same frame for all time steps)


def _compute_jet_stream(ds):
    """Time-mean zonal wind -- reveals persistent jet structure."""
    return ds.ucomp.mean(dim="time").values


def _compute_wind_speed(ds):
    """Instantaneous wind speed sqrt(u^2 + v^2)."""
    return np.sqrt(ds.ucomp.values**2 + ds.vcomp.values**2)


def _compute_eddy_streamfunction(ds):
    """Streamfunction with zonal mean removed: psi' = psi - [psi]."""
    psi = ds.stream.values
    return psi - psi.mean(axis=2, keepdims=True)


COMPUTED_DIAGNOSTICS = {
    "jet_stream": {
        "description": "Time-mean zonal wind (jet stream structure)",
        "compute": _compute_jet_stream,
        "static": True,
        "cmap": "RdBu_r",
        "diverging": True,
    },
    "wind_speed": {
        "description": "Wind speed magnitude sqrt(u^2 + v^2)",
        "compute": _compute_wind_speed,
        "static": False,
        "cmap": "magma",
        "diverging": False,
    },
    "eddy_stream": {
        "description": "Eddy streamfunction (zonal mean removed)",
        "compute": _compute_eddy_streamfunction,
        "static": False,
        "cmap": "RdBu_r",
        "diverging": True,
    },
}


def preprocess_dataset(ds):
    for v in ds.variables:
        if "units" in ds[v].attrs and "0000-00-00" in ds[v].attrs["units"]:
            ds[v].attrs["units"] = (
                ds[v].attrs["units"].replace("0000-00-00", "0001-01-01")
            )
        if ds[v].attrs.get("calendar") == "NO_CALENDAR":
            ds[v].attrs["calendar"] = "360_day"
    return ds


def load_data(input_path):
    pattern = str(Path(input_path) / "run*" / "atmos_daily.nc")
    ds = xr.open_mfdataset(
        pattern,
        combine="by_coords",
        data_vars="minimal",
        coords="minimal",
        compat="override",
        decode_times=False,
        preprocess=preprocess_dataset,
    )
    ds = xr.decode_cf(
        ds,
        decode_times=xr.coders.CFDatetimeCoder(use_cftime=True),
        decode_timedelta=True,
    )
    return ds


def get_available_diagnostics(ds):
    skip = {"average_T1", "average_T2", "average_DT", "time_bounds"}
    raw = sorted(v for v in ds.data_vars if v not in skip and ds[v].ndim >= 2)
    computed = sorted(COMPUTED_DIAGNOSTICS.keys())
    return raw, computed


def resolve_diagnostic(ds, diag):
    """Resolve a diagnostic name to (data, is_static, is_diverging, default_cmap).

    Works for both raw dataset variables and computed diagnostics.
    Returns data as ndarray: (time, lat, lon) or (lat, lon) if static.
    """
    if diag in COMPUTED_DIAGNOSTICS:
        entry = COMPUTED_DIAGNOSTICS[diag]
        print(f"Computing '{diag}': {entry['description']}")
        data = entry["compute"](ds)
        return data, entry["static"], entry["diverging"], entry["cmap"]

    if diag not in ds.data_vars:
        raw, computed = get_available_diagnostics(ds)
        all_diags = raw + computed
        raise ValueError(f"Diagnostic '{diag}' not found. Available: {all_diags}")

    data = ds[diag].values
    if data.ndim < 2:
        raise ValueError(
            f"Diagnostic '{diag}' is not a spatial field (shape {data.shape})"
        )
    is_static = data.ndim == 2
    is_diverging = diag in DIVERGING_FIELDS
    default_cmap = DEFAULT_CMAPS.get(diag, "RdBu_r" if is_diverging else "viridis")
    return data, is_static, is_diverging, default_cmap


def make_gif(ds, args):
    diag = args.diagnostic
    data, is_static, is_diverging, default_cmap = resolve_diagnostic(ds, diag)

    lon = ds.lon.values
    lat = ds.lat.values
    ntime = len(ds.time)

    # For static fields, broadcast to 3D so indexing is uniform
    if is_static:
        data_2d = data
        data = np.broadcast_to(data_2d[None, :, :], (ntime, *data_2d.shape))

    # Color limits
    percentile = args.percentile
    vlim = np.percentile(np.abs(data), percentile)

    # Override diverging detection if user explicitly chose a diverging cmap
    if args.cmap in {
        "RdBu_r",
        "RdBu",
        "seismic",
        "bwr",
        "PuOr",
        "coolwarm",
        "PiYG",
        "PRGn",
    }:
        is_diverging = True

    cmap = args.cmap if args.cmap is not None else default_cmap

    if is_diverging:
        vmin, vmax = -vlim, vlim
    else:
        vmin, vmax = 0, vlim

    # Frame configuration
    if args.time == "evolve":
        n_frames = args.n_frames if args.n_frames else ntime
        time_indices = np.linspace(0, ntime - 1, n_frames).astype(int)
    else:
        t_fixed = int(args.time)
        if t_fixed < 0 or t_fixed >= ntime:
            raise ValueError(f"Time index {t_fixed} out of range [0, {ntime - 1}]")
        n_frames = args.n_frames if args.n_frames else 90
        time_indices = np.full(n_frames, t_fixed, dtype=int)

    total_rotation = args.rotations * 360.0
    rotation_per_frame = total_rotation / n_frames

    pc = ccrs.PlateCarree()
    fig = plt.figure(figsize=(args.figsize, args.figsize))

    progress = tqdm(total=n_frames, desc="Rendering frames")

    def make_frame(i):
        fig.clf()
        central_lon = (args.center_lon + i * rotation_per_frame) % 360
        proj = ccrs.Orthographic(central_lon, args.center_lat)
        ax = fig.add_subplot(1, 1, 1, projection=proj)
        t_idx = time_indices[i]
        ax.pcolormesh(
            lon,
            lat,
            data[t_idx],
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            shading="auto",
            transform=pc,
        )
        ax.set_global()
        ax.gridlines(alpha=0.3)
        title = (
            f"{diag} (t={t_idx}/{ntime - 1})"
            if args.time == "evolve"
            else f"{diag} (t={t_fixed})"
        )
        ax.set_title(title)
        progress.update(1)
        return []

    ani = animation.FuncAnimation(fig, make_frame, frames=n_frames, blit=False)
    ani.save(args.output_path, writer="pillow", fps=args.fps, dpi=args.dpi)
    plt.close()
    progress.close()

    print(f"Saved: {args.output_path} ({n_frames} frames, {args.fps} fps)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a rotating globe GIF from Isca simulation output.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s --input-path ../output/barotropic_stirring-T85\n"
            "  %(prog)s --input-path ../output/barotropic_stirring-T85 --time 50 --diagnostic pv\n"
            "  %(prog)s --input-path ../output/barotropic_stirring-T85 --rotations 2 --fps 12\n"
        ),
    )

    parser.add_argument(
        "--input-path",
        required=True,
        help="Path to simulator output directory containing run*/atmos_daily.nc",
    )
    parser.add_argument(
        "--output-path",
        default="globe.gif",
        help="Output GIF path (default: globe.gif)",
    )
    parser.add_argument(
        "--time",
        default="evolve",
        help=(
            "'evolve' to advance through all time steps, or an integer for a "
            "fixed time step (default: evolve)"
        ),
    )
    parser.add_argument(
        "--diagnostic",
        default="vor",
        help="Variable name from the dataset (default: vor). "
        "Use --list-diagnostics to see options.",
    )
    parser.add_argument(
        "--list-diagnostics",
        action="store_true",
        help="Print available diagnostics and exit",
    )
    parser.add_argument(
        "--list-times",
        action="store_true",
        help="Print available time steps and exit",
    )
    parser.add_argument(
        "--cmap",
        default=None,
        help="Matplotlib colormap (default: auto based on diagnostic)",
    )
    parser.add_argument(
        "--rotations",
        type=float,
        default=1.0,
        help="Number of full rotations over the animation (default: 1.0)",
    )
    parser.add_argument(
        "--n-frames",
        type=int,
        default=None,
        help="Number of frames (default: number of time steps for evolve, 90 for fixed)",
    )
    parser.add_argument(
        "--center-lat",
        type=float,
        default=30.0,
        help="Latitude of the view center in degrees (default: 30.0)",
    )
    parser.add_argument(
        "--center-lon",
        type=float,
        default=0.0,
        help="Starting longitude of the view center in degrees (default: 0.0)",
    )
    parser.add_argument(
        "--figsize",
        type=float,
        default=6.0,
        help="Figure size in inches (square) (default: 6.0)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=6,
        help="Frames per second (default: 6)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=100,
        help="Resolution in dots per inch (default: 100)",
    )
    parser.add_argument(
        "--percentile",
        type=float,
        default=98.0,
        help="Percentile for robust color scaling (default: 98.0)",
    )

    args = parser.parse_args()

    print(f"Loading data from {args.input_path}...")
    ds = load_data(args.input_path)

    if args.list_diagnostics:
        raw, computed = get_available_diagnostics(ds)
        print("Available diagnostics:")
        print("  Raw (from dataset):")
        for v in raw:
            shape = ds[v].shape
            print(f"    {v:20s} {shape}")
        print("  Computed:")
        for v in computed:
            entry = COMPUTED_DIAGNOSTICS[v]
            tag = "static" if entry["static"] else "time-varying"
            print(f"    {v:20s} {entry['description']} ({tag})")
        return

    if args.list_times:
        times = ds.time.values
        print(f"Available time steps: {len(times)} (indices 0 to {len(times) - 1})")
        for i, t in enumerate(times):
            print(f"  {i:4d}  {t}")
        return

    make_gif(ds, args)


if __name__ == "__main__":
    main()
