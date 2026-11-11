"""Normalization, model geometry, checkpoint identity, and optimizer guards."""

from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest
import torch
from torch.utils.data import DataLoader, TensorDataset

from ml.config import TrainingConfig
from ml.data.metadata import DataMetadata
from ml.diagnostics.grid import GaussianGrid
from ml.inference import load_checkpoint, predict_windows
from ml.training.model import build_model, GaussianSphericalConv
from ml.training.normalization import RunningMoments, Normalization
from ml.training.trainer import Trainer


def test_population_moments_independent_of_partition():
    values = torch.arange(1.0, 25.0).reshape(4, 2, 3)
    fitted = []
    for chunks in ((values,), (values[:1], values[1:3], values[3:])):
        moments = RunningMoments()
        for chunk in chunks:
            moments.update(chunk)
        norm = moments.normalizer()
        fitted.append(norm)
        torch.testing.assert_close(norm.mean, values.mean((0, 2), keepdim=True))
        torch.testing.assert_close(
            norm.std, values.std((0, 2), correction=0, keepdim=True)
        )
        torch.testing.assert_close(
            norm.inverse_transform(norm.transform(values)), values
        )
    torch.testing.assert_close(fitted[0].std, fitted[1].std, rtol=0, atol=0)


def test_gaussian_model_uses_real_coordinates_and_orientation(simulation):
    _, _, cfg = simulation
    nodes = np.polynomial.legendre.leggauss(4)[0]
    grid = GaussianGrid(np.rad2deg(np.arcsin(nodes)), np.arange(12) * 30)
    model = build_model(cfg.model, grid)
    conv = model.model.fno_blocks.convs[0]
    assert isinstance(conv, GaussianSphericalConv)
    assert conv.sht_grids == ["legendre-gauss", "legendre-gauss"]
    x = torch.randn(2, 6, 4, 12)
    embedded = model.model.positional_embedding(x)
    torch.testing.assert_close(
        embedded[0, 6, :, 0], torch.tensor(grid.latitudes / 90, dtype=x.dtype)
    )
    manual = conv.sht_handle.sht(
        torch.tensor(np.broadcast_to(nodes[:, None], (4, 12)).copy()).flip(-2),
        s=(4, 2),
        grid="legendre-gauss",
    )
    assert manual[1, 0].real.item() == pytest.approx(np.sqrt(4 * np.pi / 3), rel=1e-6)
    model(x).square().mean().backward()
    assert all(
        p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters()
    )


def test_checkpoint_restores_physical_predictions_for_all_targets(simulation, tmp_path):
    _, _, cfg = simulation
    grid = GaussianGrid(
        np.rad2deg(np.arcsin(np.polynomial.legendre.leggauss(4)[0])), np.arange(12) * 30
    )
    torch.manual_seed(17)
    model = build_model(cfg.model, grid).eval()
    x = torch.randn(5, 6, 4, 12) * 1e-7
    y = torch.randn(5, 2, 4)
    xm, ym = RunningMoments(), RunningMoments()
    xm.update(x)
    ym.update(y)
    norm = Normalization(
        xm.normalizer(), ym.normalizer(), DataMetadata.from_config(grid, cfg.data)
    )
    with torch.no_grad():
        expected = norm.y.inverse_transform(model(norm.x.transform(x))).numpy()
    torch.save(model.state_dict(), tmp_path / "parameters.pt")
    torch.save(norm.to_dict(), tmp_path / "normalization.pt")
    checkpoint = load_checkpoint(cfg, tmp_path)
    actual = predict_windows(
        checkpoint.model, checkpoint.normalization, x.numpy(), torch.device("cpu"), 2
    )
    np.testing.assert_allclose(actual, expected, rtol=2e-6, atol=2e-6)
    assert actual.shape == (5, 2, 4)
    with pytest.raises(ValueError, match="unversioned"):
        Normalization.from_dict({"x_mean": torch.tensor(0.0)})


def _bare_trainer():
    trainer = Trainer.__new__(Trainer)
    trainer.device = torch.device("cpu")
    trainer.model = torch.nn.Linear(1, 1, bias=False)
    with torch.no_grad():
        trainer.model.weight.fill_(1)
    trainer.normalizer_x = trainer.normalizer_y = SimpleNamespace(transform=lambda x: x)
    trainer.loss_fn = torch.nn.MSELoss()
    trainer.optimizer = torch.optim.SGD(trainer.model.parameters(), lr=0.1)
    trainer.grad_clip = None
    return trainer


def test_validation_is_sample_weighted():
    trainer = _bare_trainer()
    ds = TensorDataset(torch.tensor([[0.0], [0.0], [3.0]]), torch.zeros(3, 1))
    assert trainer.evaluate(DataLoader(ds, batch_size=2)) == 3
    assert trainer.evaluate(DataLoader(ds, batch_size=3)) == 3


@pytest.mark.parametrize("failure", ["loss", "gradient"])
def test_nonfinite_values_stop_before_updating_weights(failure):
    trainer = _bare_trainer()
    before = trainer.model.weight.detach().clone()
    if failure == "loss":
        trainer.loss_fn = lambda p, y: p.sum() * float("nan")
    else:
        trainer.model.weight.register_hook(lambda gradient: gradient * float("nan"))
    ds = TensorDataset(torch.ones(1, 1), torch.zeros(1, 1))
    with pytest.raises(FloatingPointError, match="not updated"):
        trainer.train_epoch(DataLoader(ds, batch_size=1))
    torch.testing.assert_close(trainer.model.weight, before, rtol=0, atol=0)


@pytest.mark.parametrize(
    "settings",
    [
        {"epochs": 0, "batch_size": 1},
        {"epochs": 1, "batch_size": 0},
        {"epochs": 1, "batch_size": 1, "learning_rate": float("nan")},
        {"epochs": 1, "batch_size": 1, "grad_clip": -1},
    ],
)
def test_invalid_training_settings_fail_before_execution(settings):
    with pytest.raises(ValueError):
        TrainingConfig(**settings)


def test_unweighted_relative_loss_ignores_supplied_quadrature():
    from ml.training.loss import create_loss_fn

    prediction = torch.tensor([[[2.0, 1.0]]])
    truth = torch.ones_like(prediction)
    weights = torch.tensor([0.1, 0.9])
    unweighted = create_loss_fn("relative_l2", weights)(prediction, truth)
    weighted = create_loss_fn("lat_weighted_relative_l2", weights)(prediction, truth)
    assert unweighted.item() == pytest.approx(np.sqrt(0.5))
    assert weighted.item() == pytest.approx(np.sqrt(0.1))
