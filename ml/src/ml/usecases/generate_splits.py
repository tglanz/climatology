import logging
from pathlib import Path

from ml.config import load as load_config
from ml.data.isca_preprocessing import list_simulation_dirs
from ml.data.splits import generate
from ml.data.sweep_file import SweepFile

log = logging.getLogger(__name__)


def run(config_path: Path, name: str, description: str) -> Path:
    cfg = load_config(config_path)
    data_cfg = cfg.data
    split_config = data_cfg.split

    sim_dirs = list_simulation_dirs(data_cfg)

    sweep = None
    if split_config.test_hold_out is not None:
        sweep = SweepFile.from_experiment_dir(data_cfg.experiment_dir)

    splits = generate(split_config, sim_dirs, sweep)

    log.info(
        "generated split %r: train=%d, val=%d, test=%d",
        name, len(splits.train), len(splits.validation), len(splits.test),
    )

    return splits.save(cfg.paths.splits_dir, name, description, split_config)
