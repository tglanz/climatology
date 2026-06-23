"""
Reader for the sweep.json file produced by sim/scanner.py.

sweep.json maps 6-character config codes to their stirring parameter dicts:
  {"<code>": {"stirring_lat0": 45.0, "stirring_amplitude": 1e-10, ...}, ...}
"""
import json
from pathlib import Path


class SweepFile:
    def __init__(self, path: Path):
        self._path = path
        self._data: dict[str, dict] = json.loads(path.read_text())

    @classmethod
    def from_experiment_dir(cls, experiment_dir: Path) -> "SweepFile":
        return cls(experiment_dir / "sweep.json")

    def params_for(self, code: str) -> dict | None:
        return self._data.get(code)

    def codes(self) -> list[str]:
        return list(self._data.keys())

    def varying_keys(self) -> list[str]:
        """Returns parameter keys whose values differ across configs."""
        all_params = list(self._data.values())
        if len(all_params) <= 1:
            return list(all_params[0].keys()) if all_params else []
        return [
            k for k in all_params[0]
            if len({p[k] for p in all_params}) > 1
        ]

    def describe(self, code: str) -> str:
        """Short human-readable description showing only the varying params."""
        params = self._data.get(code)
        if params is None:
            return code
        keys = self.varying_keys() or list(params.keys())
        parts = [f"{k.removeprefix('stirring_')}={params[k]}" for k in keys]
        return ", ".join(parts)
