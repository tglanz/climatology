"""Baseline isolation, explicit undefined scores, and a complete two-target experiment."""

from dataclasses import replace
import json
from pathlib import Path

from click.testing import CliRunner
import numpy as np
import pytest
import torch

from conftest import write_simulation
from ml.cmd.train import train
from ml.data.splits import Splits
from ml.data.sweep_file import SweepFile
from ml.diagnostics.errors import ScoreSummary
from ml.inference import load_checkpoint, predict_windows
from ml.usecases import preprocess, evaluate, evaluate_samples
from ml.usecases.evaluation_results import (
    ProfileCase,
    baseline_predictions,
    score_predictor,
)
from ml.visualization.model_samples import plot_sample_profiles


def _write_config(cfg, path):
    from dataclasses import asdict

    lines = []

    def table(name, values):
        lines.append(f"[{name}]")
        for key, value in values.items():
            if value is not None and not isinstance(value, dict):
                lines.append(f"{key} = {json.dumps(value,default=str)}")
        lines.append("")
        for key, value in values.items():
            if isinstance(value, dict):
                table(f"{name}.{key}", value)

    for name, values in asdict(cfg).items():
        table(name, values)
    path.write_text("\n".join(lines) + "\n")


def test_training_baselines_are_independent_of_test_truth(tmp_path):
    lat = np.rad2deg(np.arcsin(np.polynomial.legendre.leggauss(4)[0]))
    cases = [
        ProfileCase(
            tmp_path / "train-0", "train", "train", np.arange(4.0) + 1, np.ones(4)
        ),
        ProfileCase(
            tmp_path / "test-0", "test", "test", np.arange(4.0) + 4, np.ones(4)
        ),
    ]
    sweep_path = tmp_path / "sweep.json"
    sweep_path.write_text(json.dumps({"train": {"p": 0}, "test": {"p": 2}}))
    first, _ = baseline_predictions(cases, SweepFile(sweep_path))
    changed = [cases[0], replace(cases[1], truth=np.ones(4) * 999)]
    second, _ = baseline_predictions(changed, SweepFile(sweep_path))
    for name in ("train mean", "nearest configuration"):
        a = next(p for p in first if p.name == name)
        b = next(p for p in second if p.name == name)
        np.testing.assert_array_equal(a.profiles, b.profiles)
    score = score_predictor(first[0], [cases[1]], lat)
    assert score.relative_l2.mean == 1


def test_missing_training_and_parameters_do_not_create_false_baselines(tmp_path):
    case = ProfileCase(tmp_path / "test-0", "test", "test", np.ones(4), np.zeros(4))
    predictions, _ = baseline_predictions([case], None)
    for predictor in predictions:
        if predictor.name in ("train mean", "nearest configuration"):
            assert predictor.profiles is None
            assert predictor.unavailable_reason
    lat = np.rad2deg(np.arcsin(np.polynomial.legendre.leggauss(4)[0]))
    case = replace(case, truth=np.zeros(4))
    score = score_predictor(predictions[0], [case], lat)
    assert score.relative_l2 == ScoreSummary(None, 0, 1)
    assert score.rmse.mean == 0


def test_complete_two_target_pipeline_and_current_report(
    simulation, gaussian_coordinates, tmp_path, monkeypatch
):
    import matplotlib.pyplot as plt

    paths, _, cfg = simulation
    lat, lon = gaussian_coordinates
    write_simulation(tmp_path / "simulations" / "validation-0", lat, lon, 1.0)
    write_simulation(tmp_path / "simulations" / "test-0", lat, lon, 2.0)
    write_simulation(tmp_path / "simulations" / "test-1", lat, lon, 3.0)
    splits = Splits(
        [tmp_path / "simulations" / "test-0", tmp_path / "simulations" / "test-1"],
        [tmp_path / "simulations" / "validation-0"],
        [paths[0].parent.parent],
    )
    manifest = splits.save(tmp_path / "splits", "fixture", "fixture", cfg.data.split)
    config_path = tmp_path / "config.toml"
    _write_config(cfg, config_path)
    preprocess.run(config_path, manifest, 0)
    invocation = CliRunner().invoke(
        train, ["--config", str(config_path), "--device", "cpu", "--track-metrics"]
    )
    assert invocation.exit_code == 0, (
        invocation.output + "\n" + repr(invocation.exception)
    )
    from ml.cmd.util import baseline_mean

    baseline = CliRunner().invoke(baseline_mean, ["--config", str(config_path)])
    assert baseline.exit_code == 0, baseline.output + repr(baseline.exception)
    baseline_data = json.loads(baseline.output)
    assert baseline_data["mean_predictor_population"] == "training simulations"
    assert len(baseline_data["targets"]) == 2
    assert baseline_data["targets"][1]["score_units"] == "(1/s)^2"
    checkpoint = load_checkpoint(cfg, cfg.paths.training_dir)
    target_results = evaluate.run(
        cfg.paths.training_dir, n_workers=0, batch_size=3, device="cpu"
    )
    assert len(target_results) == 2
    for result in target_results:
        assert (
            next(s for s in result.scores if s.name == "model").relative_l2.count == 2
        )
        assert next(
            s for s in result.scores if s.name == "nearest configuration"
        ).unavailable_reason
    prepared = evaluate_samples.run(cfg.paths.training_dir, batch_size=3, device="cpu")
    assert prepared.predictions.shape == (8, 2, 4)
    assert prepared.truth.shape == (8, 2, 4)
    from ml.usecases.evaluate_by_code import evaluate_sim

    by_code = evaluate_sim(
        tmp_path / "simulations" / "test-0",
        cfg,
        checkpoint.model,
        checkpoint.normalization,
    )
    np.testing.assert_allclose(
        by_code.predictions, prepared.predictions[:4], rtol=1e-6, atol=1e-6
    )
    np.testing.assert_array_equal(by_code.y_windows, prepared.truth[:4])

    np.testing.assert_array_equal(prepared.latitudes, lat)
    import h5py

    with h5py.File(cfg.paths.preprocessed_dir / "test.h5", "r") as handle:
        x = handle["x"][:]
    direct = predict_windows(
        checkpoint.model, checkpoint.normalization, x, torch.device("cpu"), 3
    )
    np.testing.assert_allclose(prepared.predictions, direct, rtol=1e-6, atol=1e-6)
    monkeypatch.setattr(plt, "show", lambda: None)
    figures = plot_sample_profiles(prepared, n_show=1)
    assert len(figures) == 2
    assert "1/s" in figures[1].axes[0].get_xlabel()
    plt.close("all")
    output = cfg.paths.training_dir / "evaluation"
    records = json.loads((output / "scores.json").read_text())
    for name in cfg.data.y_vars:
        assert name in records["targets"]
    relative_files = records["figures"]
    assert all((output / name).exists() for name in relative_files)
    stale = output / "figures" / "old.png"
    stale.write_bytes(b"old figure")
    monkeypatch.setattr(evaluate, "_render_target", lambda *args: None)
    evaluate.run(cfg.paths.training_dir, n_workers=0, batch_size=3, device="cpu")
    report = (output / "report.md").read_text()
    assert "old.png" not in report
    assert "variability.png" not in report
    assert "nearest configuration" in report
    assert "No parameter metadata" in report
    assert stale.read_bytes() == b"old figure"


def test_prepared_mean_uses_one_profile_per_simulation(
    simulation, gaussian_coordinates, tmp_path, monkeypatch
):
    from ml.data.isca_dataset import IscaDataset
    from ml.data.simulation_data import read_simulation
    from ml.training.baselines import score_mean
    from torch.utils.data import DataLoader, TensorDataset
    import xarray as xr

    paths, _, cfg = simulation
    lat, lon = gaussian_coordinates
    second = tmp_path / "simulations" / "other-0"
    write_simulation(second, lat, lon, 10.0)
    with xr.open_dataset(paths[1], decode_times=False) as source:
        shortened = source.isel(time=slice(0, 2)).load()
    shortened.to_netcdf(paths[1], mode="w")
    monkeypatch.setattr(preprocess, "load_config", lambda _: cfg)
    output = tmp_path / "unequal.h5"
    _, count = preprocess._extract_pairs(
        [paths[0].parent.parent, second], Path("unused"), output, 0
    )
    assert count == 7
    dataset = IscaDataset(output)
    assert dataset.simulation_targets.shape == (2, 2, 4)
    expected = torch.from_numpy(
        np.mean(
            [
                read_simulation(paths[0].parent.parent, cfg.data).truth_profile,
                read_simulation(second, cfg.data).truth_profile,
            ],
            axis=0,
        )
    )[None]
    loader = DataLoader(TensorDataset(torch.zeros(1, 1), expected), batch_size=1)
    assert score_mean(dataset.simulation_targets, loader, torch.nn.MSELoss(), 0) == 0


def test_model_info_does_not_require_prepared_data(simulation, tmp_path):
    from ml.cmd.util import model_info

    _, _, cfg = simulation
    config = tmp_path / "model-info.toml"
    _write_config(cfg, config)
    result = CliRunner().invoke(model_info, ["--config", str(config)])
    assert result.exit_code == 0, result.output + repr(result.exception)
    assert "total params:" in result.output
