"""Simulation cleanup is an explicit ML utility with preview and confirmation."""

import json

import pytest
from click.testing import CliRunner

from ml.cmd.cli import cli


@pytest.fixture(name="simulation_outputs")
def _simulation_outputs(tmp_path):
    paths = []
    for code, latitude in (("abc123-0", 30), ("def456-0", 40)):
        path = tmp_path / code
        path.mkdir()
        (path / "namelist.json").write_text(
            json.dumps({"stirring_nml": {"lat0": latitude}}), encoding="utf-8"
        )
        paths.append(path)
    (tmp_path / "crashed-sims.txt").touch()
    return tmp_path, paths


@pytest.mark.parametrize("dry_run", [True, False])
def test_filter_and_confirm(simulation_outputs, dry_run):
    root, (selected, retained) = simulation_outputs
    args = ["util", "purge-simulations", "--output-dir", str(root), "--lat0", "30"]
    if dry_run:
        args.append("--dry-run")
    result = CliRunner().invoke(cli, args, input="y\n")
    assert result.exit_code == 0, result.output
    assert selected.name in result.output
    assert retained.name not in result.output
    assert selected.exists() == dry_run
    assert retained.is_dir()
    assert (root / "crashed-sims.txt").exists()
    assert ("Delete 1 directories?" in result.output) != dry_run


def test_declining_confirmation_preserves_simulations(simulation_outputs):
    root, paths = simulation_outputs
    result = CliRunner().invoke(
        cli, ["util", "purge-simulations", "--output-dir", str(root)], input="n\n"
    )
    assert result.exit_code == 0, result.output
    assert "Aborted." in result.output
    assert all(path.is_dir() for path in paths)


def test_multiple_latitudes_and_no_filter(simulation_outputs):
    root, paths = simulation_outputs
    for filters in ([], ["--lat0", "30", "--lat0", "40"]):
        result = CliRunner().invoke(
            cli,
            [
                "util",
                "purge-simulations",
                "--output-dir",
                str(root),
                "--dry-run",
                *filters,
            ],
        )
        assert result.exit_code == 0, result.output
        assert "Targeting 2 dirs" in result.output
        assert all(path.is_dir() for path in paths)


def test_no_matches_preserves_simulations(simulation_outputs):
    root, paths = simulation_outputs
    result = CliRunner().invoke(
        cli, ["util", "purge-simulations", "--output-dir", str(root), "--lat0", "80"]
    )
    assert result.exit_code == 0, result.output
    assert "No matching simulation directories" in result.output
    assert all(path.is_dir() for path in paths)
