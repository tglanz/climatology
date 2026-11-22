"""Config migration reaches shell entry points without executing their jobs."""

import json
import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
VARIANTS = {"default", "lat-extra-hi-hold-out", "lat-intra-hold-out"}


@pytest.fixture(name="fake_commands")
def _fake_commands(tmp_path):
    folder = tmp_path / "bin"
    folder.mkdir()
    code = (
        "#!/usr/bin/env python3\n"
        "import json, os, pathlib, sys\n"
        "args = sys.argv[1:]\n"
        "print(json.dumps({'command': pathlib.Path(sys.argv[0]).name, "
        "'args': args, 'cwd': os.getcwd()}))\n"
        "if os.environ.get('FAIL_COMMAND') in args: sys.exit(2)\n"
    )
    for name in ("uv", "sbatch"):
        path = folder / name
        path.write_text(code, encoding="utf-8")
        path.chmod(0o755)
    return dict(os.environ, PATH=str(folder) + os.pathsep + os.environ["PATH"])


def launch(script, directory, env, *args):
    result = subprocess.run(
        ["bash", str(ROOT / script), *args],
        cwd=directory,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    records = [
        json.loads(line) for line in result.stdout.splitlines() if line.startswith("{")
    ]
    return result, records


@pytest.mark.parametrize("pool", ["bvet42", "bvet85"])
@pytest.mark.parametrize("stage", ["preprocess", "train", "evaluate"])
def test_slurm_wrappers_select_all_pool_variants(tmp_path, fake_commands, pool, stage):
    result, records = launch(f"slurm/{stage}.sh", tmp_path, fake_commands, pool)
    assert result.returncode == 0, result.stderr
    assert len(records) == 3
    selected = set()
    for record in records:
        assert record["command"] == "sbatch"
        assert record["cwd"] == str(ROOT / "slurm")
        job, config, *extra = record["args"]
        assert job == f"./{stage}.slurm"
        path = Path(config)
        assert path.parent == ROOT / "ml/configs" / pool
        assert path.is_file()
        selected.add(path.stem)
        assert extra == ([path.stem] if stage == "preprocess" else [])
    assert selected == VARIANTS


@pytest.mark.parametrize("stage", ["preprocess", "train", "evaluate"])
def test_slurm_wrapper_defaults_and_invalid_pool(tmp_path, fake_commands, stage):
    result, records = launch(f"slurm/{stage}.sh", tmp_path, fake_commands)
    assert result.returncode == 0, result.stderr
    assert all(Path(record["args"][1]).parent.name == "bvet85" for record in records)
    result, records = launch(f"slurm/{stage}.sh", tmp_path, fake_commands, "unknown")
    assert result.returncode == 2
    assert not records


@pytest.mark.parametrize("pool", ["bvet42", "bvet85"])
def test_slurm_check_selects_intra_holdout(tmp_path, fake_commands, pool):
    result, records = launch("slurm/check.sh", tmp_path, fake_commands, pool)
    assert result.returncode == 0, result.stderr
    assert len(records) == 1
    assert records[0]["cwd"] == str(ROOT / "slurm")
    assert records[0]["args"] == [
        "./preprocess.slurm",
        str(ROOT / "ml/configs" / pool / "lat-intra-hold-out.toml"),
        "lat-intra-hold-out",
    ]


@pytest.mark.parametrize("pool", ["bvet42", "bvet85"])
@pytest.mark.parametrize("variant", sorted(VARIANTS))
def test_local_preprocessing_uses_one_config(tmp_path, fake_commands, pool, variant):
    config = str(ROOT / "ml/configs" / pool / f"{variant}.toml")
    result, records = launch("scripts/preprocess.sh", tmp_path, fake_commands, config)
    assert result.returncode == 0, result.stderr
    stages = []
    for record in records:
        assert record["command"] == "uv"
        assert record["cwd"] == str(ROOT)
        args = record["args"]
        assert args[:6] == [
            "run",
            "--project",
            "ml",
            "--all-groups",
            "ml",
            "preprocess",
        ]
        stages.append(args[6])
        assert args[args.index("-c") + 1] == config
        assert "--experiment-dir" not in args
    assert stages == ["validate-simulations", "create-sweep-file", "generate-splits"]
    assert "--validate-spinup" in records[0]["args"]
    assert "--validate-convergence" in records[0]["args"]
    assert "--validate-climatology" in records[0]["args"]
    assert records[2]["args"][-2:] == ["--name", "fixed"]


def test_failed_validation_stops_local_preprocessing(tmp_path, fake_commands):
    config = str(ROOT / "ml/configs/bvet42/default.toml")
    result, records = launch(
        "scripts/preprocess.sh",
        tmp_path,
        dict(fake_commands, FAIL_COMMAND="validate-simulations"),
        config,
    )
    assert result.returncode == 2
    assert len(records) == 1
    assert "validate-simulations" in records[0]["args"]


@pytest.mark.parametrize("script", ["preprocess", "create-sweep-file"])
def test_local_wrappers_require_an_existing_config(tmp_path, fake_commands, script):
    result, records = launch(f"scripts/{script}.sh", tmp_path, fake_commands)
    assert result.returncode == 2
    assert not records
    result, records = launch(
        f"scripts/{script}.sh", tmp_path, fake_commands, "missing.toml"
    )
    assert result.returncode == 1
    assert not records
