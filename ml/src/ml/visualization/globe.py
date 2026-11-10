"""Rotating globe rendering and diagnostic display options."""

import cartopy.crs as ccrs
from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from ml.diagnostics.fields import jet_stream, wind_speed, eddy_streamfunction

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


COMPUTED_DIAGNOSTICS = {
    "jet_stream": {
        "description": "Time-mean zonal wind (jet stream structure)",
        "compute": jet_stream,
        "static": True,
        "cmap": "RdBu_r",
        "diverging": True,
    },
    "wind_speed": {
        "description": "Wind speed magnitude sqrt(u^2 + v^2)",
        "compute": wind_speed,
        "static": False,
        "cmap": "magma",
        "diverging": False,
    },
    "eddy_stream": {
        "description": "Eddy streamfunction (zonal mean removed)",
        "compute": eddy_streamfunction,
        "static": False,
        "cmap": "RdBu_r",
        "diverging": True,
    },
}


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
