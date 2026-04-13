"""
Barotropic Vorticity Equation: Visualization Guide

Demonstrates standard visualization techniques for atmospheric model output.
Data is synthetic -- the visualizations apply directly to real simulator output.

Parts:
  1. BVE-specific diagnostics
  2. Fluid dynamics general
  3. PDE general
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.ndimage import gaussian_filter

plt.rcParams["figure.dpi"] = 100

# =============================================================================
# Setup: Synthetic Data
# =============================================================================

NLAT  = 64
NLON  = 128
NTIME = 12

lat     = np.linspace(-87.5, 87.5, NLAT)
lon     = np.linspace(0.0, 360.0 - 360.0 / NLON, NLON)
lat_rad = np.deg2rad(lat)
lon_rad = np.deg2rad(lon)
LON, LAT = np.meshgrid(lon_rad, lat_rad)

EARTH_RADIUS = 6.371e6   # m
OMEGA        = 7.292e-5  # rad/s
CORIOLIS     = 2.0 * OMEGA * np.sin(LAT)

dlat    = lat_rad[1] - lat_rad[0]
dlon    = lon_rad[1] - lon_rad[0]
cos_lat = np.cos(LAT).clip(1e-6)

rng = np.random.default_rng(42)

# --- Background zonal jet (symmetric about equator) ---
JET_LAT   = np.deg2rad(45.0)
JET_WIDTH = np.deg2rad(15.0)
JET_SPEED = 25.0  # m/s

U_MEAN = JET_SPEED * (
    np.exp(-((LAT - JET_LAT) ** 2) / (2.0 * JET_WIDTH ** 2)) +
    np.exp(-((LAT + JET_LAT) ** 2) / (2.0 * JET_WIDTH ** 2))
)

# --- Broadband vorticity via 2D isotropic spectrum ---
# Generate in 2D Fourier space so features are coherent in both lat and lon.
# E(k) ~ k^{-3}  =>  amplitude ~ k^{-2} in 2D (since E(k) = 2*pi*k * |A(k)|^2).
# Taper above total wavenumber ~15 for large, visible eddies.
nk = NLON // 2 + 1

def make_broadband_vorticity(seed, scale=8e-6):
    r = np.random.default_rng(seed)
    # 2D wavenumber grid (dimensionless integer wavenumbers)
    kx = np.fft.rfftfreq(NLON, d=1.0 / NLON)  # 0, 1, 2, ..., NLON/2
    ky = np.fft.fftfreq(NLAT, d=1.0 / NLAT)    # 0, 1, ..., N/2, -N/2+1, ..., -1
    KX, KY = np.meshgrid(kx, ky)
    K_MAG = np.sqrt(KX ** 2 + KY ** 2)
    K_MAG[0, 0] = 1.0  # avoid division by zero

    amplitude = K_MAG ** (-2.0)
    amplitude[0, 0] = 0.0  # zero mean
    amplitude[K_MAG > 15] *= np.exp(-((K_MAG[K_MAG > 15] - 15) / 5) ** 2)

    noise = r.standard_normal((NLAT, nk)) + 1j * r.standard_normal((NLAT, nk))
    vor_hat = noise * amplitude
    vor = np.fft.irfft2(vor_hat, s=(NLAT, NLON))
    return vor * scale / (vor.std() + 1e-20)

# --- Streamfunction from vorticity: solve nabla^2 psi = zeta spectrally ---
DX = EARTH_RADIUS * dlon
DY = EARTH_RADIUS * dlat

kx_phys = np.fft.rfftfreq(NLON) * (2.0 * np.pi / DX)
ky_phys = np.fft.fftfreq(NLAT)  * (2.0 * np.pi / DY)
KX_PHYS, KY_PHYS = np.meshgrid(kx_phys, ky_phys)
K2_PHYS          = KX_PHYS ** 2 + KY_PHYS ** 2
K2_PHYS[0, 0]    = 1.0

def invert_for_psi(vor):
    vor_hat        = np.fft.rfft2(vor)
    psi_hat        = -vor_hat / K2_PHYS[:, :nk]
    psi_hat[0, 0]  = 0.0
    return np.fft.irfft2(psi_hat, s=(NLAT, NLON))

def winds_from_psi(psi):
    u = -np.gradient(psi, dlat, axis=0) / EARTH_RADIUS
    v =  np.gradient(psi, dlon, axis=1) / (EARTH_RADIUS * cos_lat)
    return u, v

# --- Time series: pure eastward phase shift (no integration, no CFL) ---
# Each step shifts the vorticity field east by a fixed angle.
# This mimics wave propagation and gives visible time evolution.
PHASE_SHIFT_DEG = 15.0  # degrees east per snapshot
phase_shift_rad = np.deg2rad(PHASE_SHIFT_DEG)

VOR_0  = make_broadband_vorticity(seed=0)
PSI_0  = invert_for_psi(VOR_0)
U_PERT_0, V_0 = winds_from_psi(PSI_0)

def shift_field_east(field, shift_rad):
    """Shift a 2D (lat, lon) field eastward by shift_rad using spectral phase shift."""
    field_hat   = np.fft.rfft(field, axis=1)
    k           = np.arange(field_hat.shape[1])
    phase       = np.exp(1j * k * shift_rad / dlon)
    return np.fft.irfft(field_hat * phase[None, :], n=NLON, axis=1)

VOR_list = [VOR_0.copy()]
for t in range(1, NTIME):
    VOR_list.append(shift_field_east(VOR_0, t * phase_shift_rad))

VOR  = np.array(VOR_list)   # (NTIME, NLAT, NLON)
PSI  = np.array([invert_for_psi(VOR[t]) for t in range(NTIME)])
U_TS = np.array([U_MEAN + winds_from_psi(PSI[t])[0] for t in range(NTIME)])
V_TS = np.array([winds_from_psi(PSI[t])[1] for t in range(NTIME)])

PSI_0  = PSI[0]
U_FULL = U_TS[0]
V_0    = V_TS[0]

# --- Synthetic prediction: mimics over-smoothed learned operator output ---
VOR_TRUE = VOR_0.copy()
VOR_PRED = gaussian_filter(VOR_0, sigma=1.5) + 0.08 * rng.standard_normal((NLAT, NLON)) * VOR_0.std()

# --- Area weighting ---
cos_lat_2d = np.cos(LAT).clip(0)
area_norm  = cos_lat_2d.sum()

def area_mean(field):
    return (field * cos_lat_2d).sum() / area_norm

days = np.arange(NTIME) * 7

print(f"Grid:            {NLAT} x {NLON}, {NTIME} snapshots")
print(f"Vorticity range: {VOR_0.min():.2e} to {VOR_0.max():.2e} s^-1")
print(f"Zonal wind:      {U_FULL.min():.1f} to {U_FULL.max():.1f} m/s")

# =============================================================================
# Part 1: BVE-Specific Diagnostics
# =============================================================================

# --- 1.1 Vorticity Evolution (multi-panel snapshots) ---
SNAP_INDICES = list(range(NTIME))  # every snapshot (7-day intervals)
vlim = np.percentile(np.abs(VOR), 98)

NCOLS = 4
NROWS = int(np.ceil(len(SNAP_INDICES) / NCOLS))
fig, axes = plt.subplots(NROWS, NCOLS, figsize=(16, 3.5 * NROWS), sharey=True)
for i, t in enumerate(SNAP_INDICES):
    ax = axes.flat[i]
    im = ax.pcolormesh(lon, lat, VOR[t], cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto")
    ax.set_title(f"Day {days[t]}")
    ax.set_xlabel("Longitude [deg]")
    if i % NCOLS == 0:
        ax.set_ylabel("Latitude [deg]")
for j in range(len(SNAP_INDICES), NROWS * NCOLS):
    axes.flat[j].set_visible(False)
fig.colorbar(im, ax=axes, label="Vorticity [s^-1]", shrink=0.8)
fig.suptitle("1.1 Vorticity Evolution", y=1.02)
plt.tight_layout()
plt.savefig("notebooks/out_1_1_vorticity.png", bbox_inches="tight")
plt.close()
print("Saved 1.1")

# --- 1.2 Streamfunction ---
fig, ax = plt.subplots(figsize=(10, 4))
vlim = np.percentile(np.abs(PSI_0), 98)
im   = ax.pcolormesh(lon, lat, PSI_0, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto")
fig.colorbar(im, ax=ax, label="Streamfunction [m^2 s^-1]")
ax.contour(lon, lat, PSI_0, levels=12, colors="k", linewidths=0.5, alpha=0.4)
ax.set_title("1.2 Streamfunction")
ax.set_xlabel("Longitude [deg]")
ax.set_ylabel("Latitude [deg]")
plt.tight_layout()
plt.savefig("notebooks/out_1_2_streamfunction.png")
plt.close()
print("Saved 1.2")

# --- 1.3 Zonal Mean Zonal Wind (time evolution) ---
fig, ax = plt.subplots(figsize=(5, 6))
cmap   = plt.cm.viridis
colors = cmap(np.linspace(0, 1, NTIME))
for t in range(NTIME):
    u_zonal = U_TS[t].mean(axis=1)  # mean over lon
    ax.plot(u_zonal, lat, color=colors[t], alpha=0.7)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, (NTIME - 1) * 7))
sm.set_array([])
fig.colorbar(sm, ax=ax, label="Day")
ax.axvline(0, color="k", linewidth=0.5)
ax.set_xlabel("Zonal Mean U [m/s]")
ax.set_ylabel("Latitude [deg]")
ax.set_title("1.3 Zonal Mean Zonal Wind")
plt.tight_layout()
plt.savefig("notebooks/out_1_3_zonal_wind.png")
plt.close()
print("Saved 1.3")

# --- 1.4 Hovmoller Diagram ---
# Show vorticity at a fixed latitude vs. longitude and time.
# This reveals eastward wave propagation as diagonal bands.
HOVMOLLER_LAT_IDX = np.argmin(np.abs(lat - 45.0))  # track the 45N jet region
VOR_AT_LAT = VOR[:, HOVMOLLER_LAT_IDX, :]  # (NTIME, NLON)

fig, ax = plt.subplots(figsize=(9, 5))
vlim = np.percentile(np.abs(VOR_AT_LAT), 98)
im   = ax.pcolormesh(lon, days, VOR_AT_LAT, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto")
fig.colorbar(im, ax=ax, label="Vorticity [s^-1]")
ax.set_xlabel("Longitude [deg]")
ax.set_ylabel("Day")
ax.set_title(f"1.4 Hovmoller: Vorticity at {lat[HOVMOLLER_LAT_IDX]:.1f}N")
plt.tight_layout()
plt.savefig("notebooks/out_1_4_hovmoller.png")
plt.close()
print("Saved 1.4")

# --- 1.5 Enstrophy (should be conserved for shifted field) ---
enstrophy = np.array([area_mean(0.5 * VOR[t] ** 2) for t in range(NTIME)])

fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(days, enstrophy / enstrophy[0], marker="o")
ax.axhline(1.0, color="k", linestyle="--", linewidth=0.8, label="Exact conservation")
ax.set_xlabel("Day")
ax.set_ylabel("Enstrophy / E_0")
ax.set_title("1.5 Enstrophy Conservation")
ax.legend()
plt.tight_layout()
plt.savefig("notebooks/out_1_5_enstrophy.png")
plt.close()
print("Saved 1.5")

# =============================================================================
# Part 2: Fluid Dynamics General
# =============================================================================

# --- 2.1 Wind Vectors (Quiver) ---
# Convert winds from m/s to degrees/day so arrows are physically meaningful
# on a lat-lon axes (1 deg longitude ~ 111 km * cos(lat), 1 deg latitude ~ 111 km).
DEG_PER_M = 180.0 / (np.pi * EARTH_RADIUS)  # ~8.99e-6 deg/m
SECS_PER_DAY = 86400.0

U_DEG = U_FULL * DEG_PER_M / cos_lat * SECS_PER_DAY   # deg longitude / day
V_DEG = V_0    * DEG_PER_M             * SECS_PER_DAY  # deg latitude  / day

# Clip to 70S-70N to avoid pole singularity in 1/cos(lat)
LAT_CLIP = 70.0
lat_mask = np.abs(lat) <= LAT_CLIP
lat_q    = lat[lat_mask]
SKIP = 4

fig, ax = plt.subplots(figsize=(10, 4))
vlim = np.percentile(np.abs(VOR_0), 98)
ax.pcolormesh(lon, lat, VOR_0, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto", alpha=0.6)
ax.quiver(
    lon[::SKIP], lat_q[::SKIP],
    U_DEG[lat_mask, :][::SKIP, ::SKIP], V_DEG[lat_mask, :][::SKIP, ::SKIP],
)
ax.set_title("2.1 Wind Vectors on Vorticity (arrows: deg/day)")
ax.set_xlabel("Longitude [deg]")
ax.set_ylabel("Latitude [deg]")
plt.tight_layout()
plt.savefig("notebooks/out_2_1_quiver.png")
plt.close()
print("Saved 2.1")

# --- 2.2 Kinetic Energy Spectrum ---
def zonal_energy_spectrum(u, weights):
    """Area-weighted zonal kinetic energy spectrum E(k). weights: (NLAT,)"""
    u_hat = np.fft.rfft(u, axis=1)           # (NLAT, nk)
    power = (np.abs(u_hat) ** 2) * weights[:, None]  # (NLAT, nk)
    return power.sum(axis=0) / weights.sum()

cos_weights = np.cos(lat_rad).clip(0)
E_k = zonal_energy_spectrum(U_FULL, cos_weights)
k   = np.arange(len(E_k))
k[0] = 1

fig, ax = plt.subplots(figsize=(6, 4))
ax.loglog(k[1:], E_k[1:], label="KE spectrum")
k_ref = np.array([2, 15])
ax.loglog(k_ref, E_k[2] * (k_ref / 2.0) ** (-3), "k--", label="k^{-3}")
ax.set_xlabel("Zonal wavenumber k")
ax.set_ylabel("Energy")
ax.set_title("2.2 Kinetic Energy Spectrum")
ax.legend()
plt.tight_layout()
plt.savefig("notebooks/out_2_2_spectrum.png")
plt.close()
print("Saved 2.2")

# --- 2.3 Kinetic Energy Conservation ---
energy = np.array([area_mean(0.5 * U_TS[t] ** 2) for t in range(NTIME)])

fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(days, energy / energy[0], marker="o")
ax.axhline(1.0, color="k", linestyle="--", linewidth=0.8)
ax.set_xlabel("Day")
ax.set_ylabel("KE / KE_0")
ax.set_title("2.3 Kinetic Energy Conservation")
plt.tight_layout()
plt.savefig("notebooks/out_2_3_energy.png")
plt.close()
print("Saved 2.3")

# =============================================================================
# Part 3: PDE General
# =============================================================================

# --- 3.1 Error Maps ---
abs_error    = np.abs(VOR_PRED - VOR_TRUE)
signed_error = VOR_PRED - VOR_TRUE
rel_error    = abs_error / (np.abs(VOR_TRUE) + 1e-10 * VOR_TRUE.std())

fig, axes = plt.subplots(1, 3, figsize=(15, 3))

vlim = np.percentile(abs_error, 98)
im0  = axes[0].pcolormesh(lon, lat, abs_error, cmap="Reds", vmin=0, vmax=vlim, shading="auto")
fig.colorbar(im0, ax=axes[0], label="|error| [s^-1]")
axes[0].set_title("Absolute Error")

vlim = np.percentile(np.abs(signed_error), 98)
im1  = axes[1].pcolormesh(lon, lat, signed_error, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto")
fig.colorbar(im1, ax=axes[1], label="Signed error [s^-1]")
axes[1].set_title("Signed Error")

vlim = np.percentile(rel_error, 95)
im2  = axes[2].pcolormesh(lon, lat, rel_error, cmap="YlOrRd", vmin=0, vmax=vlim, shading="auto")
fig.colorbar(im2, ax=axes[2], label="Relative error")
axes[2].set_title("Relative Error")

for ax in axes:
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")

plt.suptitle("3.1 Error Maps", y=1.02)
plt.tight_layout()
plt.savefig("notebooks/out_3_1_error_maps.png", bbox_inches="tight")
plt.close()
print("Saved 3.1")

# --- 3.2 Power Spectrum Comparison ---
def power_spectrum(field, weights):
    """weights: (NLAT,)"""
    f_hat = np.fft.rfft(field, axis=1)
    power = (np.abs(f_hat) ** 2) * weights[:, None]
    return power.sum(axis=0) / weights.sum()

P_true = power_spectrum(VOR_TRUE, cos_weights)
P_pred = power_spectrum(VOR_PRED, cos_weights)
k_ps   = np.arange(len(P_true))
k_ps[0] = 1

# Only compare up to wavenumber ~20 where true spectrum has real signal.
# Beyond that the true field has near-zero power and the ratio is meaningless.
K_MAX_COMPARE = 20

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].loglog(k_ps[1:K_MAX_COMPARE], P_true[1:K_MAX_COMPARE], label="True")
axes[0].loglog(k_ps[1:K_MAX_COMPARE], P_pred[1:K_MAX_COMPARE], label="Prediction", linestyle="--")
axes[0].set_xlabel("Zonal wavenumber k")
axes[0].set_ylabel("Power")
axes[0].set_title("Power Spectra")
axes[0].legend()

ratio = P_pred[1:K_MAX_COMPARE] / (P_true[1:K_MAX_COMPARE] + 1e-40)
axes[1].semilogx(k_ps[1:K_MAX_COMPARE], ratio)
axes[1].axhline(1.0, color="k", linestyle="--", linewidth=0.8)
axes[1].set_xlabel("Zonal wavenumber k")
axes[1].set_ylabel("Pred / True power ratio")
axes[1].set_title("Spectral Ratio")
axes[1].set_ylim(0, 2)

plt.suptitle("3.2 Power Spectrum Comparison")
plt.tight_layout()
plt.savefig("notebooks/out_3_2_power_spectrum.png")
plt.close()
print("Saved 3.2")

# --- 3.3 PDE Residual Map ---
# Residual: dzeta/dt estimated from two snapshots vs. spatial advection term
DT = 7.0 * 86400.0  # seconds between snapshots

dvdt     = (VOR[1] - VOR[0]) / DT
dvor_dx  = np.gradient(VOR[0], dlon, axis=1) / (EARTH_RADIUS * cos_lat)
dvor_dy  = np.gradient(VOR[0], dlat, axis=0) / EARTH_RADIUS
advection = U_FULL * dvor_dx + V_0 * dvor_dy
residual  = dvdt + advection  # should be near zero for a good model

fig, ax = plt.subplots(figsize=(10, 4))
vlim = np.percentile(np.abs(residual), 97)
im   = ax.pcolormesh(lon, lat, residual, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto")
fig.colorbar(im, ax=ax, label="Residual [s^-2]")
ax.set_title("3.3 PDE Residual: d(zeta)/dt + u.grad(zeta)")
ax.set_xlabel("Longitude [deg]")
ax.set_ylabel("Latitude [deg]")
plt.tight_layout()
plt.savefig("notebooks/out_3_3_residual.png")
plt.close()
print("Saved 3.3")

print("\nDone.")
