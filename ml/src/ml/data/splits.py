import json
import logging
import os
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from ml.config import SplitConfig

if TYPE_CHECKING:
    from ml.data.sweep_file import SweepFile

log = logging.getLogger(__name__)


class Splits:
    def __init__(self, test: list[Path], validation: list[Path], train: list[Path]):
        self.test = test
        self.validation = validation
        self.train = train

    def save(self, splits_dir: Path, name: str, description: str, split_config: SplitConfig) -> Path:
        splits_dir.mkdir(parents=True, exist_ok=True)
        path = splits_dir / f"{name}.json"
        base = path.parent
        with open(path, "w") as f:
            json.dump({
                "meta": {
                    "description": description,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "config": asdict(split_config),
                },
                "test": [os.path.relpath(p, start=base) for p in self.test],
                "validation": [os.path.relpath(p, start=base) for p in self.validation],
                "train": [os.path.relpath(p, start=base) for p in self.train],
            }, f, indent=2)
        log.info("saved split %r to %s", name, path)
        return path

    def has_test(self, path: Path) -> bool:
        return path in self.test

    @staticmethod
    def load(path: Path) -> "Splits":
        assert path.exists(), f"split file not found: {path}"
        with open(path) as f:
            data = json.load(f)
        base = path.parent
        return Splits(
            test=_make_paths(base, data.get("test", [])),
            validation=_make_paths(base, data.get("validation", [])),
            train=_make_paths(base, data.get("train", [])),
        )


def generate(
    config: SplitConfig,
    sim_dirs: list[Path],
    sweep: "SweepFile | None" = None,
) -> Splits:
    if config.test_ratio is not None:
        return _ratio_split(sim_dirs, config.test_ratio, config.validation_ratio)
    return _hold_out_matrix_split(sim_dirs, config.test_hold_out, config.validation_ratio, sweep)


def _config_key(sim_dir: Path) -> str:
    name = sim_dir.name
    return name.rsplit("-", 1)[0] if "-" in name else ""


def _make_paths(root: Path, relatives: list[str]) -> list[Path]:
    return [(root / r).resolve() for r in relatives]


def _ratio_split(sim_dirs: list[Path], test_ratio: float, val_ratio: float) -> Splits:
    groups: dict[str, list[Path]] = defaultdict(list)
    for d in sim_dirs:
        groups[_config_key(d)].append(d)

    codes = sorted(groups.keys())
    n = len(codes)
    n_test = max(1, round(n * test_ratio))
    n_val = max(1, round(n * val_ratio))

    test_codes = codes[:n_test]
    val_codes = codes[n_test:n_test + n_val]
    train_codes = codes[n_test + n_val:]

    return Splits(
        test=[d for c in test_codes for d in groups[c]],
        validation=[d for c in val_codes for d in groups[c]],
        train=[d for c in train_codes for d in groups[c]],
    )


def _hold_out_matrix_split(
    sim_dirs: list[Path],
    matrix: dict[str, list],
    val_ratio: float,
    sweep: "SweepFile",
) -> Splits:
    assert sweep is not None, "sweep file is required for hold_out_matrix split"

    groups: dict[str, list[Path]] = defaultdict(list)
    for d in sim_dirs:
        groups[_config_key(d)].append(d)

    test_dirs: list[Path] = []
    remaining_codes: list[str] = []

    for code in sorted(groups.keys()):
        params = sweep.params_for(code)
        assert params is not None, f"code {code!r} not found in sweep file"
        if all(params.get(param) in values for param, values in matrix.items()):
            test_dirs.extend(groups[code])
        else:
            remaining_codes.append(code)

    n_val = max(1, round(len(remaining_codes) * val_ratio))
    val_codes = remaining_codes[:n_val]
    train_codes = remaining_codes[n_val:]

    return Splits(
        test=test_dirs,
        validation=[d for c in val_codes for d in groups[c]],
        train=[d for c in train_codes for d in groups[c]],
    )
