"""Verify source/output separation through the public experiment stages."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil

from click.testing import CliRunner
import h5py
import matplotlib.pyplot as plt
import pytest
import tomli_w

from ml.cmd.cli import cli
from ml.config import (
    ConvergenceConfig,
    SimulationsConfig,
    SpinupConfig,
    SplitConfig,
    load,
    load_data,
    read_raw,
    save,
)
from ml.data.prepared import verify
from ml.data.metadata import DataMetadata
from ml.data.simulation_data import read_simulation
from ml.data.splits import Splits
from ml.services.simulations import list_simulation_dirs, summarize_simulations
from ml.usecases.experiment_example import create
from ml.usecases.evaluate_by_code import find_replicates
from ml.visualization.replicas import plot_replicate_variability


def invoke(*args):
    result = CliRunner().invoke(cli, list(args))
    assert result.exit_code == 0, result.output + repr(result.exception)
    return result


def snapshot(directory):
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in directory.rglob("*")
        if path.is_file()
    }


@pytest.fixture(name="external_source")
def _external_source(tmp_path):
    experiment = tmp_path / "experiment"
    create(experiment)
    recipe = experiment / "prepare.toml"
    cfg = load_data(recipe)
    archive = tmp_path / "archive"
    batch = archive / "batch"
    batch.mkdir(parents=True)
    for directory in cfg.simulations.dir.iterdir():
        chunks = directory / "chunks" / "chunk-0001"
        chunks.mkdir(parents=True)
        (directory / "atmos_daily.nc").rename(chunks / "fields.nc")
        directory.rename(batch / directory.name)
    cfg.simulations.dir.rmdir()
    # This source subtree and the old experiment-local layout must be ignored.
    (archive / "other" / "ignored-0").mkdir(parents=True)
    (experiment / "simulations" / "ignored-0").mkdir(parents=True)
    cfg = replace(
        cfg,
        simulations=SimulationsConfig(archive, "batch/*-0", "chunks/*/fields.nc"),
        data=replace(
            cfg.data,
            windows=replace(cfg.data.windows, start_at="spinup"),
            spinup=SpinupConfig(100, 2, 2),
            convergence=ConvergenceConfig(100, 1),
            split=SplitConfig(0.2, test_hold_out={"stirring_lat0": [30.0]}),
        ),
    )
    save(cfg, recipe)
    return experiment, recipe, cfg


@pytest.mark.parametrize("workers", [0, 1])
def test_external_source_full_flow(external_source, workers):
    experiment, recipe, cfg = external_source
    original = snapshot(cfg.simulations.dir)
    invoke(
        "preprocess",
        "create-sweep-file",
        "-c",
        str(recipe),
        "--key",
        "stirring_lat0=stirring_nml.lat0",
    )
    sweep = experiment / "sweep.json"
    assert len(json.loads(sweep.read_text(encoding="utf-8"))) == 3
    assert not (cfg.simulations.dir / "sweep.json").exists()
    result = invoke(
        "util", "summarize-simulations", "-c", str(recipe), "--segments", "1"
    )
    assert "sims done:   3/3" in result.output
    assert "codes done:  3/3" in result.output
    assert str(cfg.simulations.dir) in result.output
    invoke(
        "preprocess",
        "validate-simulations",
        "-c",
        str(recipe),
        "--validate-spinup",
        "--validate-convergence",
        "--validate-climatology",
        "--workers",
        str(workers),
    )
    invoke("data", "climatology-analysis", "-c", str(recipe), "--workers", "0")
    invoke("preprocess", "generate-splits", "-c", str(recipe), "--name", "external")
    split_path = experiment / "splits/external.json"
    splits = Splits.load(split_path)
    assigned = splits.train + splits.validation + splits.test
    assert set(assigned) == set(list_simulation_dirs(cfg.simulations))
    assert all(not path.is_relative_to(experiment) for path in assigned)
    invoke(
        "preprocess",
        "training-data",
        "-c",
        str(recipe),
        "--split",
        str(split_path),
        "--workers",
        str(workers),
    )
    prepared = cfg.paths.preprocessed_dir
    manifest = verify(prepared)
    assert (prepared / "sweep.json").read_bytes() == sweep.read_bytes()
    for name in ("train", "val", "test"):
        with h5py.File(prepared / f"{name}.h5", "r") as handle:
            assert handle.attrs["simulations_requested"] == 1
            assert handle.attrs["simulations_loaded"] == 1
            assert json.loads(handle.attrs["exclusions"]) == []
    assert snapshot(cfg.simulations.dir) == original
    # Later stages must use saved data and index even when live sources disappear.
    cfg.simulations.dir.rename(cfg.simulations.dir.with_name("moved-archive"))
    sweep.unlink()
    invoke("train", "-c", str(experiment / "run.toml"), "--device", "cpu")
    invoke(
        "evaluate",
        "model",
        "--training-dir",
        str(experiment / "run"),
        "--device",
        "cpu",
        "--n-workers",
        "0",
        "--batch-size",
        "2",
    )
    assert verify(prepared) == manifest
    assert (experiment / "run/evaluation/scores.json").is_file()


def test_stale_split_source_is_rejected(external_source):
    experiment, recipe, cfg = external_source
    result = CliRunner().invoke(
        cli,
        [
            "preprocess",
            "training-data",
            "-c",
            str(recipe),
            "--split",
            str(experiment / "splits/fixed.json"),
        ],
    )
    assert result.exit_code != 0
    assert "configured simulations source" in str(result.exception)
    assert not cfg.paths.preprocessed_dir.exists()


def test_config_roundtrip_and_data_config_inheritance(external_source):
    experiment, recipe, cfg = external_source
    restored = load_data(recipe)
    inherited = load(experiment / "run.toml")
    assert restored.simulations == cfg.simulations == inherited.simulations
    assert inherited.paths.experiment_dir == experiment
    assert inherited.simulations.dir != experiment
    assert not hasattr(inherited.data, "simulation_pattern")
    assert not hasattr(inherited.data, "segment_pattern")


@pytest.mark.parametrize(
    "field,value",
    [
        ("dir", ""),
        ("dir", None),
        ("pattern", ""),
        ("pattern", "/absolute/*"),
        ("pattern", "../*"),
        ("segment_pattern", ""),
        ("segment_pattern", "/absolute/*.nc"),
    ],
)
def test_invalid_source_configuration_is_rejected(field, value, tmp_path):
    values = {"dir": tmp_path, "pattern": "*", "segment_pattern": "run*/*.nc"}
    values[field] = value
    with pytest.raises(ValueError, match="simulations"):
        SimulationsConfig(**values)


@pytest.mark.parametrize("legacy", [False, True])
def test_source_is_required_and_legacy_fields_are_not_silent(external_source, legacy):
    _, recipe, _ = external_source
    raw = read_raw(recipe)
    if legacy:
        raw["data"]["simulation_pattern"] = "simulations/*"
    else:
        del raw["simulations"]
    recipe.write_text(tomli_w.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="simulations"):
        load_data(recipe)


def test_summary_uses_matching_files_not_segment_directories(tmp_path):
    source = tmp_path / "raw"
    (source / "group" / "aaa-0" / "run0001").mkdir(parents=True)
    (source / "group" / "bbb-0" / "run0001").mkdir(parents=True)
    (source / "group" / "aaa-0" / "run0001" / "fields.nc").touch()
    (source / "group" / "bbb-0" / "run9999").mkdir()
    (source / "other" / "ccc-0").mkdir(parents=True)
    cfg = SimulationsConfig(source, "group/*", "run*/fields.nc")
    sweep = tmp_path / "experiment" / "sweep.json"
    summary = summarize_simulations(cfg, 1, sweep)
    assert summary["total_sims"] == 2
    assert summary["done_sims"] == 1
    assert summary["total_codes"] is None
    assert summary["not_started"] is None
    sweep.parent.mkdir()
    sweep.write_text(json.dumps({"aaa": {}, "bbb": {}, "ddd": {}}), encoding="utf-8")
    summary = summarize_simulations(cfg, 1, sweep)
    assert summary["total_codes"] == 3
    assert summary["not_started"] == 1
    with pytest.raises(ValueError, match="segments"):
        summarize_simulations(cfg, 0, sweep)


def test_conflicting_replicas_do_not_publish_an_index(external_source):
    experiment, recipe, cfg = external_source
    source = cfg.simulations.dir / "batch"
    replica = source / "train-1"
    shutil.copytree(source / "train-0", replica)
    (replica / "namelist.json").write_text(
        json.dumps({"stirring_nml": {"lat0": 99}}), encoding="utf-8"
    )
    cfg = replace(cfg, simulations=replace(cfg.simulations, pattern="batch/*"))
    save(cfg, recipe)
    result = CliRunner().invoke(
        cli,
        [
            "preprocess",
            "create-sweep-file",
            "-c",
            str(recipe),
            "--key",
            "stirring_lat0=stirring_nml.lat0",
        ],
    )
    assert result.exit_code != 0
    assert "conflicting sweep" in str(result.exception)
    assert not (experiment / "sweep.json").exists()


def test_shipped_configs_have_independent_sources():
    for path in Path("ml/configs").rglob("*.toml"):
        cfg = load(path)
        assert cfg.simulations.dir.parent == Path("output/simulations")
        assert cfg.simulations.pattern == "*"
        assert not cfg.paths.experiment_dir.is_relative_to(cfg.simulations.dir)


def test_relative_source_is_independent_of_experiment(external_source, monkeypatch):
    experiment, recipe, cfg = external_source
    raw = read_raw(recipe)
    raw["simulations"]["dir"] = "archive"
    recipe.write_text(tomli_w.dumps(raw), encoding="utf-8")
    monkeypatch.chdir(experiment.parent)
    restored = load_data(recipe)
    assert {p.resolve() for p in list_simulation_dirs(restored.simulations)} == {
        p.resolve() for p in list_simulation_dirs(cfg.simulations)
    }


def test_raw_replica_plot_uses_configured_source(external_source, monkeypatch):
    experiment, recipe, cfg = external_source
    invoke(
        "preprocess",
        "create-sweep-file",
        "-c",
        str(recipe),
        "--key",
        "stirring_lat0=stirring_nml.lat0",
    )
    assert find_replicates("train", cfg.simulations) == [
        cfg.simulations.dir / "batch/train-0"
    ]
    monkeypatch.setattr(plt, "show", lambda: None)
    try:
        plot_replicate_variability(["train"], cfg)
        assert plt.get_fignums()
        assert "10.0" in plt.gcf().axes[0].get_title()
        plt.gcf().canvas.draw()
    finally:
        plt.close("all")
    assert not (cfg.simulations.dir / "sweep.json").exists()
    assert (experiment / "sweep.json").is_file()


def test_legacy_metadata_layout_is_not_numerical_identity(simulation):
    paths, _, cfg = simulation
    current = read_simulation(
        paths[0].parent.parent, cfg.data, cfg.simulations.segment_pattern
    ).metadata
    legacy = current.to_dict()
    legacy["data_config"] = dict(legacy["data_config"]) | {
        "simulation_pattern": "simulations/*",
        "segment_pattern": "old-layout/*.nc",
    }
    restored = DataMetadata.from_dict(legacy)
    assert restored.matches(current)
    restored.validate_config(cfg.data)
    with pytest.raises(ValueError, match="settings differ"):
        restored.validate_config(
            replace(cfg.data, windows=replace(cfg.data.windows, length=5))
        )
