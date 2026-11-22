"""Filesystem operations for standalone simulation outputs."""

from dataclasses import dataclass
import json
from pathlib import Path
import shutil


@dataclass(frozen=True)
class SimulationOutput:
    path: Path
    size_bytes: int


def find_simulations(
    output_dir: Path, latitudes: tuple[float, ...] = ()
) -> list[SimulationOutput]:
    if not output_dir.is_dir():
        raise FileNotFoundError(f"simulation output directory not found: {output_dir}")
    target_lats = set(latitudes) if latitudes else None
    simulations = []
    for namelist_path in sorted(output_dir.glob("*/namelist.json")):
        namelist = json.loads(namelist_path.read_text(encoding="utf-8"))
        if (
            target_lats is not None
            and namelist["stirring_nml"]["lat0"] not in target_lats
        ):
            continue
        directory = namelist_path.parent
        size_bytes = sum(f.stat().st_size for f in directory.rglob("*") if f.is_file())
        simulations.append(SimulationOutput(directory, size_bytes))
    return simulations


def delete_simulation(simulation: SimulationOutput) -> None:
    shutil.rmtree(simulation.path)
