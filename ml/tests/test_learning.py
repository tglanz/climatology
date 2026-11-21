"""Controlled cases distinguish collapse, association, and baseline leakage."""

from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pytest

from ml.data.climatology import diagnostic_for
from ml.data.sweep_file import SweepFile
from ml.diagnostics.learning import learning_diagnostics
from ml.usecases.evaluation_results import (
    ProfileCase,
    TargetEvaluation,
    baseline_predictions,
)


def _target():
    nodes = np.polynomial.legendre.leggauss(8)[0]
    lat = np.rad2deg(np.arcsin(nodes))
    cases = [
        ProfileCase(
            Path(f"{split}{i}-0"),
            f"{split}{i}",
            split,
            2 + value * nodes,
            2 + value * nodes,
        )
        for split in ("train", "test")
        for i, value in enumerate(range(1, 7))
    ]
    target = TargetEvaluation(diagnostic_for("time_mean_zonal_mean_ucomp"), lat, cases)
    target.predictors, _ = baseline_predictions(cases, None)
    return target


def test_perfect_and_collapsed_predictions_are_distinguished():
    target = _target()
    perfect = learning_diagnostics(target)
    row = perfect["splits"]["test"]
    assert row["skill_over_train_mean"] == 1
    assert row["configuration_variance_ratio"] == pytest.approx(1)
    assert row["configuration_anomaly_correlation"] == pytest.approx(1)
    assert row["configuration_anomaly_slope"] == pytest.approx(1)
    assert row["permutation_p"] < 0.05
    assert perfect["paired_test_skill"]["train mean"]["ci95"][0] > 0
    assert perfect["truncation_rmse"]["2"] < 1e-12
    mean = np.mean([c.truth for c in target.cases if c.split == "train"], axis=0)
    target.cases = [replace(c, prediction=mean) for c in target.cases]
    target.predictors, _ = baseline_predictions(target.cases, None)
    collapsed = learning_diagnostics(target)["splits"]["test"]
    assert collapsed["skill_over_train_mean"] == pytest.approx(0)
    assert collapsed["configuration_variance_ratio"] == pytest.approx(0, abs=1e-28)
    assert collapsed["permutation_p"] == 1


def test_configuration_bootstrap_does_not_treat_replicas_as_independent():
    target = _target()
    first = learning_diagnostics(target)["paired_test_skill"]["train mean"]
    target.cases = [
        replace(c, sim_dir=Path(f"{c.code}-{replica}"))
        for c in target.cases
        for replica in range(3)
    ]
    target.predictors, _ = baseline_predictions(target.cases, None)
    second = learning_diagnostics(target)["paired_test_skill"]["train mean"]
    assert first["configurations"] == second["configurations"]
    assert first["skill"] == pytest.approx(second["skill"])
    assert first["mse_improvement"] == pytest.approx(second["mse_improvement"])
    np.testing.assert_allclose(first["ci95"], second["ci95"], rtol=1e-14)


def test_parameter_fit_uses_only_training_targets(tmp_path):
    target = _target()
    sweep_path = tmp_path / "sweep.json"
    sweep_path.write_text(
        json.dumps({c.code: {"forcing": float(c.truth[-1])} for c in target.cases})
    )
    first, _ = baseline_predictions(target.cases, SweepFile(sweep_path))
    changed = [
        replace(c, truth=c.truth * 100) if c.split == "test" else c
        for c in target.cases
    ]
    second, _ = baseline_predictions(changed, SweepFile(sweep_path))
    a = next(p for p in first if p.name == "parameter ridge")
    b = next(p for p in second if p.name == "parameter ridge")
    np.testing.assert_array_equal(a.profiles, b.profiles)
    np.testing.assert_allclose(
        a.profiles, np.stack([c.truth for c in target.test_cases]), atol=1e-6
    )


def test_constant_truth_and_single_configuration_have_no_false_evidence():
    target = _target()
    target.cases = [replace(target.cases[0], truth=np.ones(8), prediction=np.ones(8))]
    target.predictors, _ = baseline_predictions(target.cases, None)
    row = learning_diagnostics(target)["splits"]["train"]
    assert row["skill_over_train_mean"] is None
    assert row["configuration_variance_ratio"] is None
    assert row["configuration_anomaly_correlation"] is None
    assert row["permutation_p"] is None
