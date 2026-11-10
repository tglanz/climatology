"""Barotropic field views extracted from the exploratory notebook."""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from ml.diagnostics.spatial import area_mean, zonal_anomaly
from ml.diagnostics.enstrophy import mean_enstrophy
from ml.diagnostics.spectra import lat_weighted_zonal_power_spectrum

EARTH_RADIUS = 6.371e6


def plot_hovmoller(ds):
    lon, lat = ds.lon.values, ds.lat.values
    target_lat = 45.0
    lat_idx = np.argmin(np.abs(lat - target_lat))
    v = ds.vcomp.values
    v_at_lat = v[:, lat_idx, :]

    time_indices = np.arange(len(ds.time))
    vlim = np.percentile(np.abs(v_at_lat), 98)

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.pcolormesh(
        lon,
        time_indices,
        v_at_lat,
        cmap="RdBu_r",
        vmin=-vlim,
        vmax=vlim,
        shading="auto",
    )
    fig.colorbar(im, ax=ax, label="v [m/s]")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Time index")
    ax.set_title(f"Hovmoller: Meridional Wind at {lat[lat_idx]:.1f}N")
    plt.tight_layout()
    plt.show()


def plot_normalized_enstrophy(ds):
    lon, lat = ds.lon.values, ds.lat.values
    vor = ds.vor.values
    ntime = vor.shape[0]
    enstrophy = mean_enstrophy(vor, lat)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(np.arange(ntime), enstrophy / enstrophy[0], marker="o", markersize=3)
    ax.axhline(1.0, color="k", linestyle="--", linewidth=0.8, label="Initial value")
    ax.set_xlabel("Time index")
    ax.set_ylabel("Enstrophy / E_0")
    ax.set_title("Enstrophy Time Series (Normalized)")
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_rossby_waves(ds):
    lon, lat = ds.lon.values, ds.lat.values
    target_lat = 45.0
    lat_idx = np.argmin(np.abs(lat - target_lat))
    v_at_lat = ds.vcomp.values[:, lat_idx, :]  # (time, lon)
    v_hat = np.fft.rfft(v_at_lat, axis=1)
    ntime_steps = len(ds.time)
    time_ax = np.arange(ntime_steps)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    # Top row: individual wavenumber Hovmollers
    for i, k_show in enumerate([3, 4, 5]):
        ax = axes[0, i]
        v_hat_k = np.zeros_like(v_hat)
        v_hat_k[:, k_show] = v_hat[:, k_show]
        v_k = np.fft.irfft(v_hat_k, n=v_at_lat.shape[1], axis=1)
        vlim = np.percentile(np.abs(v_k), 98)
        im = ax.pcolormesh(
            lon, time_ax, v_k, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto"
        )
        fig.colorbar(im, ax=ax, label="v [m/s]")
        ax.set_title(f"Wavenumber k={k_show}")
        ax.set_xlabel("Longitude [deg]")
        ax.set_ylabel("Time index")

    # Bottom left: planetary scale k=1-4
    ax = axes[1, 0]
    v_hat_filt = np.zeros_like(v_hat)
    v_hat_filt[:, 1:5] = v_hat[:, 1:5]
    v_filt = np.fft.irfft(v_hat_filt, n=v_at_lat.shape[1], axis=1)
    vlim = np.percentile(np.abs(v_filt), 98)
    im = ax.pcolormesh(
        lon, time_ax, v_filt, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto"
    )
    fig.colorbar(im, ax=ax, label="v [m/s]")
    ax.set_title("Filtered k=1-4 (planetary)")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Time index")

    # Bottom center: synoptic scale k=4-8
    ax = axes[1, 1]
    v_hat_filt2 = np.zeros_like(v_hat)
    v_hat_filt2[:, 4:9] = v_hat[:, 4:9]
    v_filt2 = np.fft.irfft(v_hat_filt2, n=v_at_lat.shape[1], axis=1)
    vlim = np.percentile(np.abs(v_filt2), 98)
    im = ax.pcolormesh(
        lon, time_ax, v_filt2, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto"
    )
    fig.colorbar(im, ax=ax, label="v [m/s]")
    ax.set_title("Filtered k=4-8 (synoptic)")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Time index")

    # Bottom right: eddy streamfunction
    ax = axes[1, 2]
    t_mid = ntime_steps // 2
    psi_snap = ds.stream.isel(time=t_mid).values
    psi_eddy = zonal_anomaly(psi_snap)
    vlim = np.percentile(np.abs(psi_eddy), 98)
    im = ax.pcolormesh(
        lon, lat, psi_eddy, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto"
    )
    fig.colorbar(im, ax=ax, label="psi' [m^2 s^-1]")
    ax.set_title(f"Eddy Streamfunction (t={t_mid})")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")

    fig.suptitle(
        f"Rossby Wave Diagnostics at {lat[lat_idx]:.1f}N",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.show()


def plot_wind_vectors(ds):
    lon, lat = ds.lon.values, ds.lat.values
    t_idx = len(ds.time) // 2
    u_snap = ds.ucomp.isel(time=t_idx).values
    v_snap = ds.vcomp.isel(time=t_idx).values
    vor_snap = ds.vor.isel(time=t_idx).values

    vlim = np.percentile(np.abs(vor_snap), 98)
    skip = 4
    lat_mask = np.abs(lat) <= 70.0
    lat_q = lat[lat_mask]

    DEG_PER_M = 180.0 / (np.pi * EARTH_RADIUS)
    SECS_PER_DAY = 86400.0
    LAT_2D = np.deg2rad(lat)[:, None] * np.ones((1, len(lon)))
    cos_lat_2d = np.cos(LAT_2D).clip(1e-6)
    u_deg = u_snap * DEG_PER_M / cos_lat_2d * SECS_PER_DAY
    v_deg = v_snap * DEG_PER_M * SECS_PER_DAY

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.pcolormesh(
        lon,
        lat,
        vor_snap,
        cmap="RdBu_r",
        vmin=-vlim,
        vmax=vlim,
        shading="auto",
        alpha=0.6,
    )
    ax.quiver(
        lon[::skip],
        lat_q[::skip],
        u_deg[lat_mask, :][::skip, ::skip],
        v_deg[lat_mask, :][::skip, ::skip],
    )
    ax.set_title("Wind Vectors on Vorticity (arrows: deg/day)")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    plt.tight_layout()
    plt.show()


def plot_wind_spectrum(ds):
    lon, lat = ds.lon.values, ds.lat.values
    t_idx = len(ds.time) // 2
    u_snap = ds.ucomp.isel(time=t_idx).values

    E_k = lat_weighted_zonal_power_spectrum(u_snap, lat)
    k = np.arange(len(E_k))
    k[0] = 1

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.loglog(k[1:], E_k[1:], label="KE spectrum")
    k_ref = np.array([2, 30])
    ax.loglog(k_ref, E_k[2] * (k_ref / 2.0) ** (-3), "k--", label="$k^{-3}$")
    ax.set_xlabel("Zonal wavenumber k")
    ax.set_ylabel("Energy")
    ax.set_title("Kinetic Energy Spectrum")
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_normalized_energy(ds):
    lon, lat = ds.lon.values, ds.lat.values
    u = ds.ucomp.values
    ke = area_mean(0.5 * u**2, lat)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(np.arange(len(ke)), ke / ke[0], marker="o", markersize=3)
    ax.axhline(1.0, color="k", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Time index")
    ax.set_ylabel("KE / KE_0")
    ax.set_title("Kinetic Energy Time Series (Normalized)")
    plt.tight_layout()
    plt.show()


def plot_jet_structure(ds):
    lon, lat = ds.lon.values, ds.lat.values
    u_mean = ds.ucomp.mean(dim="time").values

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # Panel 1: Lat-lon map
    ax = axes[0]
    vlim = np.percentile(np.abs(u_mean), 98)
    im = ax.pcolormesh(
        lon, lat, u_mean, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto"
    )
    fig.colorbar(im, ax=ax, label="u [m/s]")
    ax.set_title("Time-Mean Zonal Wind (u)")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")

    # Panel 2: Zonal + time mean profile
    ax = axes[1]
    u_profile = u_mean.mean(axis=1)
    ax.plot(u_profile, lat, "b-", linewidth=2)
    ax.axvline(0, color="k", linewidth=0.5)
    ax.fill_betweenx(lat, 0, u_profile, where=u_profile > 0, alpha=0.3, color="red")
    ax.fill_betweenx(lat, 0, u_profile, where=u_profile < 0, alpha=0.3, color="blue")
    ax.set_xlabel("U [m/s]")
    ax.set_ylabel("Latitude [deg]")
    ax.set_title("Zonal + Time Mean U Profile")

    fig.suptitle("Jet Stream Structure", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_wind_direction(ds):
    lon, lat = ds.lon.values, ds.lat.values
    num_snaps = 5
    total = len(ds.time)
    indices = np.linspace(0, total - 1, num_snaps).astype(int)
    subsample = 6

    fig, axes = plt.subplots(1, num_snaps, figsize=(18, 4), sharey=True)

    speed_all = np.sqrt(ds.ucomp.values**2 + ds.vcomp.values**2)
    vmax_color = np.percentile(speed_all, 95)

    for i, idx in enumerate(indices):
        ax = axes[i]
        u_snap = ds.ucomp.isel(time=idx).values
        v_snap = ds.vcomp.isel(time=idx).values
        s = np.sqrt(u_snap**2 + v_snap**2)

        im = ax.pcolormesh(
            lon,
            lat,
            s,
            cmap="magma",
            vmin=0,
            vmax=vmax_color,
            shading="auto",
            alpha=0.5,
        )

        skip = (slice(None, None, subsample), slice(None, None, subsample))
        u_norm = u_snap[skip] / (s[skip] + 1e-10)
        v_norm = v_snap[skip] / (s[skip] + 1e-10)
        ax.quiver(
            lon[skip[1]],
            lat[skip[0]],
            u_norm,
            v_norm,
            color="black",
            scale=25,
            pivot="middle",
            width=0.005,
            headwidth=2.5,
            headlength=3,
            headaxislength=3,
        )
        ax.set_title(f"t={idx}")
        ax.set_xlabel("Longitude [deg]")
        if i == 0:
            ax.set_ylabel("Latitude [deg]")

    fig.colorbar(im, ax=axes, label="Speed [m/s]", shrink=0.8)
    fig.suptitle("Wind Speed and Direction (Normalized Vectors)", y=1.02)
    plt.tight_layout()
    plt.show()


def plot_polar_views(ds):
    lon, lat = ds.lon.values, ds.lat.values
    pc = ccrs.PlateCarree()

    t_idx = len(ds.time) // 2
    vor_snap = ds.vor.isel(time=t_idx).values
    vlim = np.percentile(np.abs(vor_snap), 98)

    views = [
        ("North Pole", ccrs.Orthographic(0, 90)),
        ("South Pole", ccrs.Orthographic(0, -90)),
        ("Atlantic", ccrs.Orthographic(-30, 30)),
        ("Pacific", ccrs.Orthographic(180, 30)),
    ]

    fig = plt.figure(figsize=(20, 5))
    ax_list = []
    for i, (title, proj) in enumerate(views):
        ax = fig.add_subplot(1, 4, i + 1, projection=proj)
        im = ax.pcolormesh(
            lon,
            lat,
            vor_snap,
            cmap="RdBu_r",
            vmin=-vlim,
            vmax=vlim,
            shading="auto",
            transform=pc,
        )
        ax.set_global()
        ax.gridlines(alpha=0.3)
        ax.set_title(title)
        ax_list.append(ax)

    fig.colorbar(
        im,
        ax=ax_list,
        label="Vorticity [s^-1]",
        shrink=0.8,
        orientation="horizontal",
        pad=0.05,
    )
    fig.suptitle(f"Vorticity on the Globe (t={t_idx})", fontsize=14, fontweight="bold")
    plt.show()


def plot_globe_fields(ds):
    lon, lat = ds.lon.values, ds.lat.values
    pc = ccrs.PlateCarree()
    t_idx = len(ds.time) // 2
    proj = ccrs.Orthographic(-30, 30)

    fields = [
        (
            "Wind Speed",
            np.sqrt(
                ds.ucomp.isel(time=t_idx).values ** 2
                + ds.vcomp.isel(time=t_idx).values ** 2
            ),
            "magma",
            None,
            "m/s",
        ),
        (
            "Time-Mean Zonal Wind",
            ds.ucomp.mean(dim="time").values,
            "RdBu_r",
            "symmetric",
            "m/s",
        ),
        (
            "Streamfunction",
            ds.stream.isel(time=t_idx).values,
            "RdBu_r",
            "symmetric",
            "m^2 s^-1",
        ),
    ]

    fig = plt.figure(figsize=(18, 5))
    for i, (title, data, cmap, mode, units) in enumerate(fields):
        ax = fig.add_subplot(1, 3, i + 1, projection=proj)
        if mode == "symmetric":
            vlim = np.percentile(np.abs(data), 98)
            kwargs = {"vmin": -vlim, "vmax": vlim}
        else:
            kwargs = {"vmin": 0, "vmax": np.percentile(data, 95)}
        im = ax.pcolormesh(
            lon, lat, data, cmap=cmap, shading="auto", transform=pc, **kwargs
        )
        ax.set_global()
        ax.gridlines(alpha=0.3)
        ax.set_title(title)
        fig.colorbar(im, ax=ax, label=units, shrink=0.7)

    fig.suptitle("Globe Projections", fontsize=14, fontweight="bold")
    plt.show()


def plot_globe_evolution(ds):
    pc = ccrs.PlateCarree()
    lon, lat = ds.lon.values, ds.lat.values
    num_snaps = 6
    total = len(ds.time)
    indices = np.linspace(0, total - 1, num_snaps).astype(int)

    vor_all = ds.vor.values
    vlim = np.percentile(np.abs(vor_all), 98)
    proj = ccrs.Orthographic(-30, 45)

    fig = plt.figure(figsize=(18, 6))
    ax_list = []
    for i, idx in enumerate(indices):
        ax = fig.add_subplot(1, num_snaps, i + 1, projection=proj)
        im = ax.pcolormesh(
            lon,
            lat,
            vor_all[idx],
            cmap="RdBu_r",
            vmin=-vlim,
            vmax=vlim,
            shading="auto",
            transform=pc,
        )
        ax.set_global()
        ax.gridlines(alpha=0.3)
        ax.set_title(f"t={idx}")
        ax_list.append(ax)

    fig.colorbar(
        im,
        ax=ax_list,
        label="Vorticity [s^-1]",
        shrink=0.6,
        orientation="horizontal",
        pad=0.05,
    )
    fig.suptitle("Vorticity Evolution on the Globe", fontsize=14, fontweight="bold")
    plt.show()
