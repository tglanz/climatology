import json
import logging

from dataclasses import dataclass
from pathlib import Path

from ml.config import PathsConfig

SPLITS_FILE_NAME = "splits.json"
KEY_VALIDATION = "validation"
KEY_TRAIN = "train"
KEY_TEST = "test"

log = logging.getLogger(__name__)

@dataclass
class Splits:
    """
    The splits file is a json file named "splits.json" located in the "data" dir.
    
    "test" are the simulations that are not seen during training at all.
    "validation" are the simulations used to compute the loss against during training for stopping.
    "train" are the simulations used to compute and backpropogate the gradients with.
    """

    test: list[Path]
    validation: list[Path]
    train: list[Path]

    def save(self, cfg: PathsConfig):
        splits_path = cfg.preprocessed_dir / SPLITS_FILE_NAME
        assert cfg.preprocessed_dir.exists(), f"{cfg.preprocessed_dir} not found"

        log.info(f"saving splits to {splits_path}")
        with open(splits_path, "w") as f:
            json.dump({
                KEY_TEST: [path.relative_to(splits_path) for path in self.test],
                KEY_VALIDATION: [path.relative_to(splits_path) for path in self.validations],
                KEY_TRAIN: [path.relative_to(splits_path) for path in self.trains],
            }, f)

    def has_test(self, path: Path) -> bool:
        return path in self.test

    @staticmethod
    def from_config(cfg: PathsConfig):
        splits_path = cfg.preprocessed_dir / SPLITS_FILE_NAME
        assert splits_path.exists(), f"{splits_path.name} not found: {splits_path} - run preprocess first"

        with open(splits_path) as f:
            splits_json = json.load(f)

        return Splits(
            test=Splits.make_paths(splits_path, splits_json.get(KEY_TEST, [])),
            validation=Splits.make_paths(splits_path, splits_json.get(KEY_VALIDATION, [])),
            train=Splits.make_paths(splits_path, splits_json.get(KEY_TRAIN, [])),
        )

    @staticmethod
    def make_paths(root: Path, relatives: list[str | Path]) -> Path:
        return [(root / relative).resolve() for relative in relatives]