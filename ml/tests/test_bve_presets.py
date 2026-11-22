"""ML presets accept their simulation grids and keep configuration replicas grouped."""

from dataclasses import replace
from itertools import product
import json
from pathlib import Path

import numpy as np
import pytest
import torch

from ml.config import load
from ml.data.splits import generate
from ml.data.sweep_file import SweepFile
from ml.diagnostics.grid import GaussianGrid
from ml.training.model import build_model


@pytest.mark.parametrize("harmonics,nlat,nlon", [(42, 64, 128), (85, 128, 256)])
def test_bve_preset_model_accepts_its_grid(harmonics, nlat, nlon):
    cfg = load(Path(f"ml/configs/bvet{harmonics}/default.toml"))
    assert cfg.simulations.dir == Path(
        f"output/simulations/barotropic_stirring-T{harmonics}"
    )
    assert cfg.paths.experiment_dir == Path(
        f"output/experiments/bvet{harmonics}/default"
    )
    assert cfg.paths.preprocessed_dir == cfg.paths.experiment_dir / "data"
    assert cfg.paths.training_dir == cfg.paths.experiment_dir / "training"
    assert cfg.paths.splits_dir == cfg.paths.experiment_dir / "splits"
    grid = GaussianGrid(
        np.rad2deg(np.arcsin(np.polynomial.legendre.leggauss(nlat)[0])),
        np.arange(nlon) * (360 / nlon),
    )
    with torch.random.fork_rng():
        torch.manual_seed(17)
        model = build_model(cfg.model, grid).eval()
        with torch.no_grad():
            output = model(
                torch.zeros(1, cfg.model.active_sub_config().in_channels, nlat, nlon)
            )
    assert output.shape == (1, len(cfg.data.y_vars), nlat)
    assert torch.isfinite(output).all()


VARIANTS = ("default", "lat-extra-hi-hold-out", "lat-intra-hold-out")
POOLS = [
    (42, [0, 30, 60, 70], [8, 16], [1.5e-11, 1e-10, 1.25e-10], 2),
    (85, [-10, 0, 30, 40, 50, 60, 70], [8, 12, 16], [7.5e-11, 1e-10, 1.25e-10], 4),
]


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("pool", POOLS)
def test_bve_preset_splits_keep_replicas_together(tmp_path, monkeypatch, pool, variant):
    harmonics, latitudes, widths, amplitudes, replicas = pool
    cfg = load(Path(f"ml/configs/bvet{harmonics}/{variant}.toml"))
    monkeypatch.chdir(tmp_path)
    sweep = {}
    paths = []
    for index, (latitude, width, amplitude) in enumerate(
        product(latitudes, widths, amplitudes)
    ):
        code = f"{index:06x}"
        sweep[code] = {
            "stirring_lat0": latitude,
            "stirring_widthy": width,
            "stirring_amplitude": amplitude,
        }
        paths.extend(
            cfg.simulations.dir / f"{code}-{replica}" for replica in range(replicas)
        )
    sweep_path = tmp_path / "sweep.json"
    sweep_path.write_text(json.dumps(sweep), encoding="utf-8")
    split_cfg = cfg.data.split
    index = SweepFile(sweep_path) if split_cfg.test_hold_out is not None else None
    splits = generate(split_cfg, paths, index)
    splits.validate()
    counts = tuple(map(len, (splits.train, splits.validation, splits.test)))
    if variant == "default":
        assert split_cfg.test_ratio == 0.2
        assert split_cfg.test_hold_out is None
        assert counts == ((36, 2, 10) if harmonics == 42 else (188, 12, 52))
    else:
        latitude = (
            70
            if variant == "lat-extra-hi-hold-out"
            else (60 if harmonics == 42 else 40)
        )
        assert split_cfg.test_ratio is None
        assert split_cfg.test_hold_out == {"stirring_lat0": [float(latitude)]}
        assert all(
            sweep[path.name.rsplit("-", 1)[0]]["stirring_lat0"] == latitude
            for path in splits.test
        )
        assert all(
            sweep[path.name.rsplit("-", 1)[0]]["stirring_lat0"] != latitude
            for path in splits.train + splits.validation
        )
        assert counts == ((34, 2, 12) if harmonics == 42 else (204, 12, 36))
    assert split_cfg.validation_ratio == 0.05
    assert not cfg.paths.experiment_dir.exists()


def test_config_layout_and_output_isolation():
    root = Path("ml/configs")
    expected = {
        root / pool / f"{variant}.toml"
        for pool in ("bvet42", "bvet85")
        for variant in VARIANTS
    }
    assert set(root.rglob("*.toml")) == expected
    outputs = set()
    for pool in ("bvet42", "bvet85"):
        base = load(root / pool / "default.toml")
        for variant in VARIANTS:
            cfg = load(root / pool / f"{variant}.toml")
            assert cfg.model == base.model
            assert cfg.training == base.training
            assert replace(cfg.data, split=base.data.split) == base.data
            assert cfg.simulations == base.simulations
            assert (
                cfg.paths.experiment_dir == Path("output/experiments") / pool / variant
            )
            outputs.add(cfg.paths.experiment_dir)
    assert len(outputs) == 6
