"""Known Fourier-mode check for the public latitude-weighted spectrum helper."""

import numpy as np

from ml.diagnostics.spectra import lat_weighted_zonal_power_spectrum


def test_weighted_single_mode_and_batch_scaling():
    longitude = np.arange(8) * (2 * np.pi / 8)
    amplitudes = np.array([1.0, 2.0, 3.0])
    field = amplitudes[:, None] * np.cos(2 * longitude)[None, :]
    latitudes = np.array([-60.0, 0.0, 60.0])

    # Mode 2 has FFT amplitude 4*a. Cosine row weights are 1/2, 1, 1/2,
    # so the weighted power is 16 * (1/2 + 4 + 9/2) / 2 = 72.
    expected = np.zeros(5)
    expected[2] = 72.0
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
