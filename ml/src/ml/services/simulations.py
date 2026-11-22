"""Filesystem operations for standalone simulation outputs."""

from dataclasses import dataclass
import json
from pathlib import Path
import shutil

from ml.config import SimulationsConfig


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


def list_simulation_dirs(
    cfg: SimulationsConfig, *, allow_empty: bool = False
) -> list[Path]:
    directories = sorted(p for p in cfg.dir.glob(cfg.pattern) if p.is_dir())
    if not directories and not allow_empty:
        raise ValueError(f"no simulations found: {cfg.dir}/{cfg.pattern}")
    return directories


def list_segment_files(sim_dir: Path, segment_pattern: str) -> list[Path]:
    return sorted(p for p in sim_dir.glob(segment_pattern) if p.is_file())


def write_sweep_index(
    simulations: list[Path],
    output: Path,
    key_specs: list[tuple[str, list[str]]],
) -> int:
    sweep = {}
    for directory in simulations:
        code = directory.name.rsplit("-", 1)[0]
        namelist_path = directory / "namelist.json"
        namelist = json.loads(namelist_path.read_text(encoding="utf-8"))
        entry = {}
        for alias, path in key_specs:
            node = namelist
            for part in path:
                if not isinstance(node, dict) or part not in node:
                    raise KeyError(
                        f"{namelist_path}: path '{'.'.join(path)}' not found"
                    )
                node = node[part]
            entry[alias] = node
        if code in sweep and sweep[code] != entry:
            raise ValueError(f"conflicting sweep parameters for configuration {code}")
        sweep[code] = entry
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(sweep, indent=2), encoding="utf-8")
    return len(sweep)


def summarize_simulations(
    cfg: SimulationsConfig, segments: int, sweep_path: Path
) -> dict:
    if segments < 1:
        raise ValueError("segments must be positive")
    if not cfg.dir.is_dir():
        return {"exists": False, "sim_dir": cfg.dir}
    expected_codes = (
        set(json.loads(sweep_path.read_text(encoding="utf-8")))
        if sweep_path.is_file()
        else None
    )
    by_code = {}
    in_progress = []
    for directory in list_simulation_dirs(cfg, allow_empty=True):
        parts = directory.name.rsplit("-", 1)
        if len(parts) != 2:
            continue
        code, _ = parts
        runs = list_segment_files(directory, cfg.segment_pattern)
        done = len(runs) >= segments
        by_code.setdefault(code, []).append(done)
        if not done:
            last = str(runs[-1].relative_to(directory)) if runs else "none"
            in_progress.append((directory.name, last, len(runs) / segments * 100))
    return {
        "exists": True,
        "sim_dir": cfg.dir,
        "total_codes": len(expected_codes) if expected_codes is not None else None,
        "total_sims": sum(len(done) for done in by_code.values()),
        "done_sims": sum(sum(done) for done in by_code.values()),
        "complete_codes": sum(all(done) for done in by_code.values()),
        "in_progress": sorted(in_progress, key=lambda item: item[2]),
        "not_started": (
            len(expected_codes - by_code.keys()) if expected_codes is not None else None
        ),
    }
