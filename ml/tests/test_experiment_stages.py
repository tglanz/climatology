"""Artifact reuse, raw-data independence, relocation, and explicit stage commands."""

import json
import shutil

from click.testing import CliRunner
import pytest

from ml.cmd.cli import cli
from ml.config import load, load_data, save
from ml.data.prepared import verify
from ml.usecases.experiment_example import create
from ml.usecases.evaluate import run as evaluate


def invoke(*args):
    result = CliRunner().invoke(cli, list(args))
    assert result.exit_code == 0, result.output + repr(result.exception)
    return result


def test_prepared_reuse_raw_removal_and_relocation(tmp_path):
    directory = tmp_path / "smoke"
    create(directory)
    prepare = directory / "prepare.toml"
    assert not hasattr(load_data(prepare), "model")
    invoke(
        "preprocess",
        "training-data",
        "-c",
        str(prepare),
        "--split",
        str(directory / "splits/fixed.json"),
    )
    original = verify(directory / "prepared")
    # No later stage may rely on raw trajectories or the input recipe.
    shutil.rmtree(directory / "simulations")
    for name in ("run", "run-wide"):
        invoke("train", "-c", str(directory / f"{name}.toml"), "--device", "cpu")
        invoke(
            "evaluate",
            "model",
            "--training-dir",
            str(directory / name),
            "--device",
            "cpu",
            "--n-workers",
            "0",
            "--batch-size",
            "2",
        )
        assert verify(directory / "prepared") == original
    run = directory / "run"
    first = json.loads((run / "evaluation/scores.json").read_text())
    moved = directory / "moved-run"
    run.rename(moved)
    prepare.unlink()
    evaluate(moved, n_workers=0, device="cpu", batch_size=2)
    assert json.loads((moved / "evaluation/scores.json").read_text()) == first
    # The entire prepared directory can move if its saved hashes still agree.
    relocated = directory / "moved-prepared"
    (directory / "prepared").rename(relocated)
    evaluate(moved, n_workers=0, device="cpu", batch_size=2, prepared_dir=relocated)
    assert json.loads((moved / "evaluation/scores.json").read_text()) == first
    with (relocated / "test.h5").open("ab") as handle:
        handle.write(b"changed")
    with pytest.raises(ValueError, match="changed"):
        evaluate(moved, n_workers=0, device="cpu", prepared_dir=relocated)


def test_reruns_preserve_completed_artifacts(tmp_path):
    directory = tmp_path / "smoke"
    create(directory)
    args = (
        "preprocess",
        "training-data",
        "-c",
        str(directory / "prepare.toml"),
        "--split",
        str(directory / "splits/fixed.json"),
    )
    invoke(*args)
    before = verify(directory / "prepared")
    result = CliRunner().invoke(cli, list(args))
    assert result.exit_code != 0
    assert verify(directory / "prepared") == before
    invoke("train", "-c", str(directory / "run.toml"), "--device", "cpu")
    weights = (directory / "run/parameters.pt").read_bytes()
    result = CliRunner().invoke(
        cli, ["train", "-c", str(directory / "run.toml"), "--device", "cpu"]
    )
    assert result.exit_code != 0
    assert (directory / "run/parameters.pt").read_bytes() == weights
    assert not (directory / "run/evaluation").exists()


def test_saved_configuration_is_standalone_and_paths_are_resolved(simulation, tmp_path):
    _, _, cfg = simulation
    snapshot = tmp_path / "saved.toml"
    save(cfg, snapshot)
    restored = load(snapshot)
    assert restored.data == cfg.data
    assert restored.model == cfg.model
    assert restored.paths.preprocessed_dir.is_absolute()


def test_failed_preparation_does_not_publish_partial_data(tmp_path):
    import tomli_w
    from ml.config import read_raw

    directory = tmp_path / "smoke"
    create(directory)
    config = directory / "prepare.toml"
    raw = read_raw(config)
    raw["data"]["windows"]["length"] = 100
    config.write_text(tomli_w.dumps(raw))
    result = CliRunner().invoke(
        cli,
        [
            "preprocess",
            "training-data",
            "-c",
            str(config),
            "--split",
            str(directory / "splits/fixed.json"),
        ],
    )
    assert result.exit_code != 0
    assert "no usable training samples" in str(result.exception)
    assert not (directory / "prepared").exists()
    assert not list(directory.glob(".prepared-*"))
    assert (directory / "simulations/train-0/atmos_daily.nc").exists()


def test_excluded_validation_is_saved_and_evaluated_without_raw_reads(tmp_path):
    directory = tmp_path / "smoke"
    create(directory)
    (directory / "simulations/validation-0/atmos_daily.nc").unlink()
    invoke(
        "preprocess",
        "training-data",
        "-c",
        str(directory / "prepare.toml"),
        "--split",
        str(directory / "splits/fixed.json"),
    )
    shutil.rmtree(directory / "simulations")
    invoke("train", "-c", str(directory / "run.toml"), "--device", "cpu")
    invoke(
        "evaluate",
        "model",
        "--training-dir",
        str(directory / "run"),
        "--device",
        "cpu",
        "--n-workers",
        "0",
    )
    scores = json.loads((directory / "run/evaluation/scores.json").read_text())
    assert len(scores["excluded"]) == 1
    assert "validation-0" in scores["excluded"][0]["simulation"]


def test_stage_commands_are_the_public_workflow():
    result = invoke("--help")
    assert "pipeline" not in result.output
    for command in ("preprocess", "train", "evaluate"):
        assert command in result.output
