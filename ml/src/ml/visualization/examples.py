"""Plots for the exploratory prediction and advection examples."""

import numpy as np
import matplotlib.pyplot as plt
from ml.diagnostics.errors import absolute_error, signed_error, relative_error
from ml.diagnostics.spectra import lat_weighted_zonal_power_spectrum
from ml.diagnostics.examples import advection_residual


def plot_error_maps(VOR_PRED, VOR_TRUE, lon, lat):
    abs_err = absolute_error(VOR_PRED, VOR_TRUE)
    sgn_err = signed_error(VOR_PRED, VOR_TRUE)
    rel_err = relative_error(VOR_PRED, VOR_TRUE, eps=1e-10 * VOR_TRUE.std())

    fig, axes = plt.subplots(1, 3, figsize=(16, 4))

    vlim = np.percentile(abs_err, 98)
    im0 = axes[0].pcolormesh(
        lon, lat, abs_err, cmap="Reds", vmin=0, vmax=vlim, shading="auto"
    )
    fig.colorbar(im0, ax=axes[0], label="|error| [s^-1]")
    axes[0].set_title("Absolute Error")

    vlim = np.percentile(np.abs(sgn_err), 98)
    im1 = axes[1].pcolormesh(
        lon, lat, sgn_err, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto"
    )
    fig.colorbar(im1, ax=axes[1], label="Signed error [s^-1]")
    axes[1].set_title("Signed Error")

    vlim = np.percentile(rel_err, 95)
    im2 = axes[2].pcolormesh(
        lon, lat, rel_err, cmap="YlOrRd", vmin=0, vmax=vlim, shading="auto"
    )
    fig.colorbar(im2, ax=axes[2], label="Relative error")
    axes[2].set_title("Relative Error")

    for ax in axes:
        ax.set_xlabel("Longitude [deg]")
        ax.set_ylabel("Latitude [deg]")

    plt.suptitle("Error Maps: Prediction vs Truth", y=1.02)
    plt.tight_layout()
    plt.show()


def plot_spectrum_comparison(VOR_PRED, VOR_TRUE, lat):
    P_true = lat_weighted_zonal_power_spectrum(VOR_TRUE, lat)
    P_pred = lat_weighted_zonal_power_spectrum(VOR_PRED, lat)
    k = np.arange(len(P_true))
    k[0] = 1
    K_MAX = 40

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].loglog(k[1:K_MAX], P_true[1:K_MAX], label="True")
    axes[0].loglog(k[1:K_MAX], P_pred[1:K_MAX], label="Prediction", linestyle="--")
    axes[0].set_xlabel("Zonal wavenumber k")
    axes[0].set_ylabel("Power")
    axes[0].set_title("Power Spectra")
    axes[0].legend()

    ratio = P_pred[1:K_MAX] / (P_true[1:K_MAX] + 1e-40)
    axes[1].semilogx(k[1:K_MAX], ratio)
    axes[1].axhline(1.0, color="k", linestyle="--", linewidth=0.8)
    axes[1].set_xlabel("Zonal wavenumber k")
    axes[1].set_ylabel("Pred / True power ratio")
    axes[1].set_title("Spectral Ratio")
    axes[1].set_ylim(0, 2)

    plt.suptitle("Power Spectrum Comparison")
    plt.tight_layout()
    plt.show()


def plot_advection_residual(ds):
    lon, lat = ds.lon.values, ds.lat.values
    residual = advection_residual(ds)
    fig, ax = plt.subplots(figsize=(12, 5))
    vlim = np.percentile(np.abs(residual), 97)
    im = ax.pcolormesh(
        lon, lat, residual, cmap="RdBu_r", vmin=-vlim, vmax=vlim, shading="auto"
    )
    fig.colorbar(im, ax=ax, label="Residual [s^-2]")
    ax.set_title("PDE Residual: d(zeta)/dt + u.grad(zeta)")
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
    plt.tight_layout()
    plt.show()
