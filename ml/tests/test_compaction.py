"""Behavior checks for code moved during compaction; scientific corrections are separate."""

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch
import xarray as xr

from ml.config import load, WindowsConfig, ClimatologyConfig, ConvergenceConfig
from ml.data import evaluation, isca_preprocessing
from ml.data.simulation_data import build_timeline, stack_input_windows, extract_windows
from ml.data.window_selector import build_selector
from ml.diagnostics.errors import profile_rel_l2, profile_rmse, notebook_profile_rel_l2
from ml.diagnostics.errors import lat_weighted_relative_l2_torch
from ml.inference import load_model, predict_windows
from ml.training.model import build_model


@pytest.fixture
def simulation(tmp_path):
    lat = np.array([-65.0, -20.0, 20.0, 65.0])
    lon = np.arange(12) * 30.0
    values = np.arange(12 * 4 * 12, dtype=np.float32).reshape(12, 4, 12)
    paths = []
    for segment, start in enumerate((0, 6), 1):
        path = tmp_path / "code-0" / f"run{segment:04d}" / "atmos_daily.nc"
        path.parent.mkdir(parents=True)
        xr.Dataset(
            {
                name: (("time", "lat", "lon"), values[start : start + 6] + offset)
                for name, offset in [("vor", 0), ("ucomp", 2), ("vcomp", 4)]
            },
            coords={"time": np.arange(start, start + 6), "lat": lat, "lon": lon},
        ).to_netcdf(path)
        paths.append(path)
    cfg = replace(
        load(Path("ml/configs/default.toml")).data,
        spinup=None,
        convergence=None,
        x_vars=["vor", "vcomp"],
        windows=WindowsConfig("beginning", "end", 3, 2, 4),
        climatology=ClimatologyConfig(end_at="end", length=2),
    )
    return paths, values, cfg


def test_windows_cross_segments_in_time_then_variable_order(simulation):
    paths, values, _ = simulation
    timeline = build_timeline(paths, [6, 6])
    windows = stack_input_windows(timeline, [4], 3, ["vor", "vcomp"], {})
    assert windows.shape == (1, 6, 4, 12)
    assert windows.dtype == np.float32
    for k in range(3):
        np.testing.assert_array_equal(windows[0, 2 * k], values[4 + k])
        np.testing.assert_array_equal(windows[0, 2 * k + 1], values[4 + k] + 4)


def test_callers_keep_distinct_target_layouts(simulation, monkeypatch):
    paths, values, cfg = simulation
    cfg = replace(
        cfg, y_vars=["time_mean_zonal_mean_ucomp", "time_mean_zonal_mean_vor"]
    )
    monkeypatch.setattr(
        isca_preprocessing, "load_config", lambda _: SimpleNamespace(data=cfg)
    )
    x, y = isca_preprocessing.process_one_sim(paths[0].parent.parent, Path("unused"))
    result = evaluation._load_one_sim(paths[0].parent.parent, cfg)
    np.testing.assert_array_equal(x, result.x_windows)
    assert y.shape == (4, 2, 4)
    assert result.y_windows.shape == (4, 1, 4)
    np.testing.assert_array_equal(y[:, :1], result.y_windows)
    expected = (values[-2:] + 2).mean(axis=-1).mean(axis=0)
    np.testing.assert_array_equal(y[0, 0], expected)


def test_nonconvergence_keeps_preparation_rejection_and_evaluation_fallback(
    simulation, monkeypatch
):
    paths, _, cfg = simulation
    cfg = replace(
        cfg,
        convergence=ConvergenceConfig(0.01, 3),
        climatology=ClimatologyConfig(start_at="convergence", end_at="end"),
    )
    monkeypatch.setattr(
        isca_preprocessing, "load_config", lambda _: SimpleNamespace(data=cfg)
    )
    for module in (isca_preprocessing, evaluation):
        monkeypatch.setattr(
            module, "find_zonal_mean_convergence_time", lambda *a, **kw: None
        )
    with pytest.raises(ValueError, match="convergence not reached"):
        isca_preprocessing.process_one_sim(paths[0].parent.parent, Path("unused"))
    assert evaluation._load_one_sim(paths[0].parent.parent, cfg) is not None


def test_short_input_and_current_window_policies(simulation):
    _, values, cfg = simulation
    selector = build_selector(cfg.windows)
    assert selector.select(2) == []
    assert selector.select(12) == [0, 2, 4, 6]
    # The by-code notebook intentionally keeps its separate full-final-window rule.
    windows = extract_windows(values, 0, 3, 1)
    assert len(windows) == 10
    np.testing.assert_array_equal(windows[-1], values[-3:])


def test_profile_metrics_have_known_values_and_keep_epsilon_difference():
    lat = np.array([-60.0, 0.0, 60.0])
    truth = np.array([1.0, 2.0, 1.0])
    pred = np.array([2.0, 4.0, 2.0])
    assert profile_rmse(pred, truth, lat) == pytest.approx(np.sqrt(2.5))
    assert notebook_profile_rel_l2(pred, truth, lat) == 1.0
    assert profile_rel_l2(pred, truth, lat) < 1.0
    assert profile_rel_l2(np.zeros(3), np.zeros(3), lat) == 0.0


def test_batched_prediction_keeps_normalization_and_sample_axis():
    class FirstLongitude(torch.nn.Module):
        def forward(self, x):
            return x[:, :1, :, 0] * 2

    x = np.arange(5 * 2 * 3 * 4, dtype=np.float32).reshape(5, 2, 3, 4)
    norm = {
        key: torch.tensor(value)
        for key, value in [
            ("x_mean", 0.5),
            ("x_std", 2.0),
            ("y_mean", -1.0),
            ("y_std", 3.0),
        ]
    }
    result = predict_windows(FirstLongitude(), norm, x, torch.device("cpu"), 2)
    expected = ((x[:, 0, :, 0] - 0.5) / 2.0) * 2.0 * 3.0 - 1.0
    np.testing.assert_array_equal(result, expected)
    assert result.shape == (5, 3)


def test_checkpoint_reload_retains_tiny_model_predictions(tmp_path):
    torch.manual_seed(17)
    cfg = load(Path("ml/configs/default.toml"))
    fno = replace(
        cfg.model.fno,
        n_modes=(2, 3),
        hidden_channels=4,
        n_layers=1,
        in_channels=10,
        out_channels=1,
    )
    cfg = replace(cfg, model=replace(cfg.model, architecture="fno", fno=fno))
    model = build_model(cfg.model).eval()
    x = torch.randn(2, 10, 4, 8)
    with torch.no_grad():
        expected = model(x)
    torch.save(model.state_dict(), tmp_path / "parameters.pt")
    reloaded = load_model(cfg, tmp_path)
    with torch.no_grad():
        torch.testing.assert_close(reloaded(x), expected, rtol=0, atol=0)


def test_moved_training_metric_retains_weighted_gradient():
    pred = torch.full((1, 1, 2, 3), 2.0, requires_grad=True)
    truth = torch.ones_like(pred)
    weights = torch.tensor([1.0, 2.0])
    loss = lat_weighted_relative_l2_torch(pred, truth, weights)
    assert loss.item() == 1.0
    loss.backward()
    expected = weights.view(1, 1, 2, 1).expand_as(pred) / 9.0
    torch.testing.assert_close(pred.grad, expected, rtol=1e-7, atol=0)
