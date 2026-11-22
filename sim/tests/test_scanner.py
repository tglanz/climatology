"""Scanner output routing without compilation or numerical integration."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from sim import scanner


@pytest.fixture
def simulation(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    instance = Mock()
    monkeypatch.setattr(scanner, "BarotropicStirring", Mock(return_value=instance))
    return instance


def invoke(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["sim.scanner", *args])
    scanner.main()


@pytest.mark.parametrize("harmonics", [85, 42])
def test_default_output_uses_harmonics(monkeypatch, simulation, harmonics):
    invoke(monkeypatch, "--fourier-harmonics", str(harmonics))
    execution = simulation.execute.call_args.args[0]
    assert execution.simulations_dir == Path(
        f"output/simulations/barotropic_stirring-T{harmonics}"
    )


@pytest.mark.parametrize("absolute", [False, True])
def test_custom_output_is_used_directly(monkeypatch, tmp_path, simulation, absolute):
    destination = tmp_path / "custom" if absolute else Path("custom")
    invoke(monkeypatch, "--output-dir", str(destination), "--index", "4")
    execution = simulation.execute.call_args.args[0]
    assert execution.simulations_dir == destination
    assert execution.sim_name.endswith("-4")


def test_skip_and_auto_index_use_custom_output(monkeypatch, simulation):
    invoke(monkeypatch, "--output-dir", "custom", "--index", "0")
    execution = simulation.execute.call_args.args[0]
    last = execution.simulations_dir / execution.sim_name / "run0020/atmos_daily.nc"
    last.parent.mkdir(parents=True)
    last.touch()
    simulation.execute.reset_mock()
    invoke(monkeypatch, "--output-dir", "custom", "--index", "0")
    simulation.execute.assert_not_called()
    invoke(monkeypatch, "--output-dir", "custom")
    assert simulation.execute.call_args.args[0].sim_name.endswith("-1")


def test_failure_cleanup_and_log_use_custom_output(monkeypatch, simulation, tmp_path):
    work = tmp_path / "work"
    simulation.work_dir.return_value = work

    def fail(execution):
        raw = execution.simulations_dir / execution.sim_name
        raw.mkdir(parents=True)
        (raw / "partial.nc").touch()
        work.mkdir()
        raise scanner.FailedRunError()

    simulation.execute.side_effect = fail
    invoke(monkeypatch, "--output-dir", "custom", "--max-retries", "2")
    execution = simulation.execute.call_args.args[0]
    raw = execution.simulations_dir / execution.sim_name
    assert simulation.execute.call_count == 2
    assert not raw.exists()
    assert not work.exists()
    assert Path("custom/crashed-sims.txt").read_text(encoding="utf-8").splitlines() == [
        str(raw.resolve()),
        str(work),
    ]
    assert not Path("output").exists()


def test_compile_does_not_create_output(monkeypatch, simulation):
    invoke(monkeypatch, "--compile", "--output-dir", "custom")
    simulation.compile.assert_called_once()
    simulation.execute.assert_not_called()
    assert not Path("custom").exists()


@pytest.mark.parametrize("option", ["--experiment-name", "--experiment-dir"])
def test_experiment_options_are_rejected(monkeypatch, simulation, option):
    with pytest.raises(SystemExit) as error:
        invoke(monkeypatch, option, "old")
    assert error.value.code == 2
    simulation.execute.assert_not_called()
