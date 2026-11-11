"""Analytical Fourier mode with a known spherical latitude integral."""

import numpy as np
from ml.diagnostics.spectra import lat_weighted_zonal_power_spectrum


def test_weighted_single_mode_and_batch_scaling():
    longitude = np.arange(8) * 2 * np.pi / 8
    nodes, _ = np.polynomial.legendre.leggauss(3)
    latitudes = np.rad2deg(np.arcsin(nodes))
    field = np.sqrt(1 + nodes[:, None] ** 2) * np.cos(2 * longitude)
    # Raw FFT amplitude is 4*a; the Gaussian area mean of 1+sin(lat)^2 is 4/3.
    expected = np.zeros(5)
    expected[2] = 64 / 3
    np.testing.assert_allclose(
        lat_weighted_zonal_power_spectrum(field, latitudes),
        expected,
        rtol=1e-14,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        lat_weighted_zonal_power_spectrum(np.stack([field, 2 * field]), latitudes),
        np.stack([expected, 4 * expected]),
        rtol=1e-14,
        atol=1e-12,
    )
