"""Analytical oracles for the actual spherical grid and profile errors."""

import numpy as np
import pytest
import torch

from ml.diagnostics.grid import GaussianGrid, gaussian_latitude_weights
from ml.diagnostics.errors import profile_rel_l2, profile_rmse
from ml.diagnostics.errors import lat_weighted_relative_l2_torch
from ml.diagnostics.spatial import area_mean


def test_gaussian_quadrature_moments_and_order():
    nodes, weights = np.polynomial.legendre.leggauss(8)
    lat = np.rad2deg(np.arcsin(nodes))
    for coordinates in (lat, lat[::-1]):
        w = gaussian_latitude_weights(coordinates)
        for degree in range(16):
            expected = 0 if degree % 2 else 1 / (degree + 1)
            assert np.sum(
                w * np.sin(np.deg2rad(coordinates)) ** degree
            ) == pytest.approx(expected, abs=2e-14)
    np.testing.assert_allclose(gaussian_latitude_weights(lat), weights / 2)


def test_grid_rejects_relabeling_and_duplicate_longitude():
    lat = np.rad2deg(np.arcsin(np.polynomial.legendre.leggauss(4)[0]))
    with pytest.raises(ValueError, match="Gaussian"):
        GaussianGrid(np.linspace(-90, 90, 4), np.arange(8) * 45)
    with pytest.raises(ValueError, match="longitude"):
        GaussianGrid(lat, np.linspace(0, 360, 8))
    grid = GaussianGrid(lat, np.arange(8) * 45)
    with pytest.raises(ValueError):
        grid.latitudes[0] = 0


def test_area_and_profile_errors_use_actual_quadrature():
    nodes, _ = np.polynomial.legendre.leggauss(4)
    lat = np.rad2deg(np.arcsin(nodes))
    field = np.broadcast_to(nodes[:, None] ** 2, (4, 8))
    assert area_mean(field, lat) == pytest.approx(1 / 3)
    truth = np.ones(4)
    pred = truth + nodes
    assert profile_rmse(pred, truth, lat) == pytest.approx(np.sqrt(1 / 3))
    assert profile_rel_l2(pred, truth, lat) == pytest.approx(np.sqrt(1 / 3))
    assert np.isnan(profile_rel_l2(truth, np.zeros(4), lat))
    with pytest.raises(ValueError, match="shape"):
        profile_rel_l2(pred[:, None], truth, lat)


def test_weighted_loss_has_zero_subgradient_at_perfect_prediction():
    pred = torch.ones(2, 2, 4, requires_grad=True)
    loss = lat_weighted_relative_l2_torch(pred, pred.detach(), torch.ones(4))
    loss.backward()
    assert loss.item() == 0
    torch.testing.assert_close(pred.grad, torch.zeros_like(pred))
    with pytest.raises(ValueError, match="zero"):
        lat_weighted_relative_l2_torch(pred, torch.zeros_like(pred), torch.ones(4))


def test_weighted_loss_keeps_targets_separate():
    pred = torch.tensor([[[2.0, 2.0], [4.0, 4.0]]])
    truth = torch.tensor([[[1.0, 1.0], [4.0, 4.0]]])
    assert lat_weighted_relative_l2_torch(pred, truth, torch.ones(2)) == 0.5


def test_convergence_figure_uses_prefix_length_coordinates(monkeypatch):
    import matplotlib.pyplot as plt
    from ml.config import ConvergenceConfig
    from ml.visualization.convergence import plot_convergence

    monkeypatch.setattr(plt, "show", lambda: None)
    plot_convergence(
        np.arange(1, 10), np.linspace(1, 0, 9), 4, 7, 14, ConvergenceConfig(0.1, 2)
    )
    ax = plt.gcf().axes[0]
    assert ax.lines[2].get_xdata() == [0, 0]
    assert ax.lines[3].get_xdata() == [3, 3]
    assert "D(t_s, M)" in ax.get_ylabel()
    plt.close("all")
