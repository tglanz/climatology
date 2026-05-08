from pathlib import Path

import click

from ml.config import load as load_config
from ml.common.logging import setup_logging
from ml.isca_dataset import validate_segment
from ml.isca_preprocessing import IscaDataPreprocessor


@click.group()
def preprocess():
    pass


@preprocess.command("training-data")
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def preprocess_training_data(config_path: Path):
    cfg = load_config(config_path)
    setup_logging(cfg.logging)
    IscaDataPreprocessor(cfg).run()


@preprocess.command("validate-training-data")
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def validate_training_data(config_path: Path):
    """Walk all sims and report any that cannot be used for preprocessing."""
    cfg = load_config(config_path)
    setup_logging(cfg.logging)

    sim_dirs = sorted(cfg.data.experiment_dir.glob(cfg.data.simulation_pattern))
    if not sim_dirs:
        print(
            f"no simulations matched "
            f"{cfg.data.experiment_dir}/{cfg.data.simulation_pattern}"
        )
        raise SystemExit(1)

    K = cfg.data.lag_steps
    invalid: list[tuple[Path, str]] = []

    for sim_dir in sim_dirs:
        nc_files = sorted(sim_dir.glob(cfg.data.segment_pattern))
        if not nc_files:
            invalid.append((sim_dir, "no segments matching segment_pattern"))
            continue

        total_T = 0
        bad = False
        for nc in nc_files:
            try:
                T, _ = validate_segment(nc, cfg.data.x_vars, cfg.data.y_vars)
            except (AssertionError, OSError, ValueError) as e:
                invalid.append((sim_dir, f"{nc.name}: {e}"))
                bad = True
                break
            total_T += T
        if bad:
            continue

        # Need at least K input steps + 1 target.
        if total_T < K + 1:
            invalid.append(
                (sim_dir, f"timeline too short: {total_T} timesteps, need >= {K + 1}")
            )

    n = len(sim_dirs)
    if invalid:
        print(f"invalid simulations: {len(invalid)} of {n}")
        for sim_dir, reason in invalid:
            print(f"  {sim_dir}  -  {reason}")
        raise SystemExit(2)

    print(f"all {n} simulations valid (lag_steps={K})")
