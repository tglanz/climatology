"""Build an experiment index from its configured simulation source."""

from pathlib import Path

from ml.config import load_data
from ml.services.simulations import list_simulation_dirs, write_sweep_index


def run(config_path: Path, key_specs: list[tuple[str, list[str]]]) -> None:
    cfg = load_data(config_path)
    directories = list_simulation_dirs(cfg.simulations)
    output = cfg.paths.experiment_dir / "sweep.json"
    count = write_sweep_index(directories, output, key_specs)
    print(f"wrote {count} codes to {output}")
