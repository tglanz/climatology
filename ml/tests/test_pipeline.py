"""Artifact reuse, raw-data independence, relocation, and scheduler failures."""

import json
import os
from pathlib import Path
import shutil
import subprocess

from click.testing import CliRunner
import pytest

from ml.cmd.cli import cli
from ml.config import load, load_data, save
from ml.data.prepared import verify
from ml.usecases.pipeline_example import create
from ml.usecases.evaluate import run as evaluate


def invoke(*args):
    result = CliRunner().invoke(cli, list(args))
    assert result.exit_code == 0, result.output + repr(result.exception)
    return result


def test_prepared_reuse_raw_removal_and_relocation(tmp_path, monkeypatch):
    directory = tmp_path / "smoke"
    create(directory)
    prepare = directory / "prepare.toml"
    assert not hasattr(load_data(prepare), "model")
    invoke(
        "pipeline",
        "prepare",
        "-c",
        str(prepare),
        "--split",
        str(directory / "splits/fixed.json"),
    )
    original = verify(directory / "prepared")
    # No later stage may rely on raw trajectories or the input recipe.
    shutil.rmtree(directory / "simulations")
    for name in ("run", "run-wide"):
        invoke(
            "pipeline", "run", "-c", str(directory / f"{name}.toml"), "--device", "cpu"
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
        "pipeline",
        "prepare",
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
        cli, ["pipeline", "run", "-c", str(directory / "run.toml"), "--device", "cpu"]
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


def test_slurm_dependency_and_failure_handling(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    calls = tmp_path / "calls"
    stub = bin_dir / "sbatch"
    stub.write_text(
        '#!/bin/bash\nprintf "%s\\n" "$*" >> "$CALLS"\nif [[ "$*" == *--parsable* ]]; then echo "123;cluster"; exit "${PREP_FAIL:-0}"; fi\n'
    )
    stub.chmod(0o755)
    env = os.environ | {"PATH": f"{bin_dir}:{os.environ['PATH']}", "CALLS": str(calls)}
    script = [
        "bash",
        "scripts/submit-pipeline.sh",
        "prepare config.toml",
        "run config.toml",
        "split file.json",
    ]
    subprocess.run(script, env=env, check=True, capture_output=True)
    lines = calls.read_text().splitlines()
    assert len(lines) == 2
    assert "afterok:123" in lines[1]
    assert "prepare config.toml" in lines[0] and "split file.json" in lines[0]
    calls.unlink()
    result = subprocess.run(script, env=env | {"PREP_FAIL": "7"}, capture_output=True)
    assert result.returncode == 7
    assert len(calls.read_text().splitlines()) == 1
    # Local stage failures propagate through the exact Slurm entry point.
    uv = bin_dir / "uv"
    uv.write_text("#!/bin/bash\nexit 9\n")
    uv.chmod(0o755)
    result = subprocess.run(
        ["bash", "slurm/pipeline.slurm", "run", "-c", "missing"],
        env=env | {"SLURM_SUBMIT_DIR": str(Path.cwd())},
        capture_output=True,
    )
    assert result.returncode == 9


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
            "pipeline",
            "prepare",
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
        "pipeline",
        "prepare",
        "-c",
        str(directory / "prepare.toml"),
        "--split",
        str(directory / "splits/fixed.json"),
    )
    shutil.rmtree(directory / "simulations")
    invoke("pipeline", "run", "-c", str(directory / "run.toml"), "--device", "cpu")
    scores = json.loads((directory / "run/evaluation/scores.json").read_text())
    assert len(scores["excluded"]) == 1
    assert "validation-0" in scores["excluded"][0]["simulation"]
