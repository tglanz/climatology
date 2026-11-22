"""Exercise preset shell commands without compiling or running Isca."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from unittest.mock import Mock

import pytest

from sim import scanner

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.skipif(
    shutil.which("parallel") is None, reason="GNU Parallel is required"
)
PRESETS = [
    (
        "sim-bve-t42-2-narrow.sh",
        42,
        [0, 1],
        [0, 30, 60, 70],
        [8, 16],
        [1.5e-11, 1e-10, 1.25e-10],
        48,
    ),
    (
        "sim-bve-t85-4-standard.sh",
        85,
        [0, 1, 2, 3],
        [-10, 0, 30, 40, 50, 60, 70],
        [8, 12, 16],
        [7.5e-11, 1e-10, 1.25e-10],
        252,
    ),
]


@pytest.fixture(name="fake_conda")
def _fake_conda(tmp_path):
    binary = tmp_path / "bin" / "conda"
    binary.parent.mkdir()
    binary.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        "args = sys.argv[1:]\n"
        "print(json.dumps({'args': args, 'cwd': os.getcwd()}), flush=True)\n"
        "if os.environ.get('FAIL_COMPILE') and '--compile' in args: sys.exit(7)\n"
        "if os.environ.get('FAIL_INDEX') and '--index' in args:\n"
        "    if args[args.index('--index') + 1] == os.environ['FAIL_INDEX']: sys.exit(7)\n",
        encoding="utf-8",
    )
    binary.chmod(0o755)
    return dict(os.environ, PATH=str(binary.parent) + os.pathsep + os.environ["PATH"])


def launch(name, directory, env):
    result = subprocess.run(
        [str(ROOT / "scripts" / name)],
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


@pytest.mark.parametrize("preset", PRESETS, ids=[preset[0] for preset in PRESETS])
def test_presets_match_scanner_cli(tmp_path, monkeypatch, fake_conda, preset):
    name, harmonics, indices, latitudes, widths, amplitudes, total = preset
    result, records = launch(name, tmp_path, fake_conda)
    assert result.returncode == 0, result.stderr
    assert len(records) == 1 + len(indices)
    assert "--compile" in records[0]["args"]
    assert all(record["cwd"] == str(ROOT) for record in records)
    simulation = Mock()
    factory = Mock(return_value=simulation)
    monkeypatch.setattr(scanner, "BarotropicStirring", factory)
    monkeypatch.chdir(tmp_path)
    observed = []
    for record in records:
        args = record["args"]
        assert args[:7] == [
            "run",
            "--no-capture-output",
            "-n",
            "isca_env",
            "python",
            "-m",
            "sim.scanner",
        ]
        options = args[7:]
        if "--index" in options:
            observed.append(int(options[options.index("--index") + 1]))
        monkeypatch.setattr(sys, "argv", ["sim.scanner", *options])
        scanner.main()
    assert sorted(observed) == indices
    simulation.compile.assert_called_once()
    assert simulation.execute.call_count == total
    parameters = [call.args[0] for call in factory.call_args_list[1:]]
    assert {p.fourier_harmonics for p in parameters} == {harmonics}
    assert {p.stirring_lat0 for p in parameters} == set(latitudes)
    assert {p.stirring_widthy for p in parameters} == set(widths)
    assert {p.stirring_amplitude for p in parameters} == set(amplitudes)
    assert all(p.dt_atmos == 600 and p.segment_days == 7 for p in parameters)
    executions = [call.args[0] for call in simulation.execute.call_args_list]
    assert len({e.sim_name for e in executions}) == total
    assert all(
        e.simulations_dir
        == Path(f"output/simulations/barotropic_stirring-T{harmonics}")
        for e in executions
    )
    assert all(e.num_cores == 2 and e.n_segments == 150 for e in executions)
    assert not (tmp_path / "output").exists()


@pytest.mark.parametrize("name", [p[0] for p in PRESETS])
def test_compile_failure_stops_before_sweep(tmp_path, fake_conda, name):
    result, records = launch(name, tmp_path, dict(fake_conda, FAIL_COMPILE="1"))
    assert result.returncode == 7
    assert len(records) == 1
    assert "--compile" in records[0]["args"]


@pytest.mark.parametrize("name", [p[0] for p in PRESETS])
def test_worker_command_failure_propagates(tmp_path, fake_conda, name):
    result, records = launch(name, tmp_path, dict(fake_conda, FAIL_INDEX="1"))
    assert result.returncode != 0
    assert any("--index" in record["args"] for record in records)
