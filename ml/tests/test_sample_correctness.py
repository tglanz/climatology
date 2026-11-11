"""Preparation and evaluation must materialize the same scientific samples."""

from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import h5py
import numpy as np
import pytest
import xarray as xr

from ml.config import ConvergenceConfig, ClimatologyConfig, WindowsConfig
from ml.data import isca_preprocessing, simulation_data
from ml.data.evaluation import _load_one_sim
from ml.data.isca_segment import read_segment, validate_segment_dataset, SegmentReader
from ml.data.metadata import DataMetadata
from ml.data.splits import Splits
from ml.data.window_selector import build_selector
from ml.data.simulation_data import read_simulation, try_read_simulation
from ml.usecases import preprocess
from ml.diagnostics.spinup import find_spinup_time


def test_same_windows_targets_and_channel_order(simulation, monkeypatch):
    paths, values, cfg = simulation
    monkeypatch.setattr(isca_preprocessing, "load_config", lambda _: cfg)
    x, y = isca_preprocessing.process_one_sim(paths[0].parent.parent, Path("unused"))
    result = _load_one_sim(paths[0].parent.parent, cfg.data)
    np.testing.assert_array_equal(x, result.x_windows)
    np.testing.assert_array_equal(y, result.y_windows)
    assert y.shape == (4, 2, 4)
    np.testing.assert_allclose(y[0, 0], (values[-2:] + 2).mean(axis=(0, 2)), rtol=1e-6)
    for offset in range(3):
        np.testing.assert_array_equal(x[2, 2 * offset], values[4 + offset])
        np.testing.assert_array_equal(x[2, 2 * offset + 1], values[4 + offset] + 4)


def test_last_complete_window_and_short_trajectory():
    selector = build_selector(WindowsConfig("beginning", "end", 3, 1))
    assert selector.select(2) == []
    assert selector.select(3) == [0]
    assert selector.select(5) == [0, 1, 2]
    selector = build_selector(WindowsConfig("beginning", "convergence", 3, 1))
    assert selector.select(5, t_c=1) == [0, 1]


def test_nonconvergence_has_one_rejection_policy(simulation, monkeypatch):
    paths, _, cfg = simulation
    data = replace(
        cfg.data,
        convergence=ConvergenceConfig(0.01, 3),
        climatology=ClimatologyConfig(start_at="convergence", end_at="end"),
    )
    monkeypatch.setattr(
        simulation_data, "find_zonal_mean_convergence_time", lambda *a, **kw: None
    )
    outcome = try_read_simulation(paths[0].parent.parent, data)
    assert outcome.samples is None
    assert "convergence" in outcome.reason
    assert _load_one_sim(paths[0].parent.parent, data) is None


def test_cache_reuses_and_owner_closes(simulation):
    paths, _, _ = simulation
    with patch("ml.data.isca_segment.xr.open_dataset", wraps=xr.open_dataset) as opened:
        with SegmentReader() as reader:
            first = reader.read(paths[0])
            assert reader.read(paths[0]) is first
            assert opened.call_count == 1
            assert len(reader.cache) == 1
        assert reader.cache == {}
    cache = {}
    first = read_segment(paths[0], cache)
    try:
        assert read_segment(paths[0], cache) is first
        closed = []
        original = first._close
        first.set_close(lambda: closed.append(True))
        validate_segment_dataset(first, ["vor"], [])
        assert closed == []
        first.set_close(original)
    finally:
        first.close()


def test_segment_gap_and_units_are_rejected(simulation):
    paths, _, cfg = simulation
    with xr.open_dataset(paths[1], decode_times=False) as source:
        ds = source.load()
    ds["time"] = ds.time + 1
    ds.time.attrs = {"units": "days since 2000-01-01", "calendar": "360_day"}
    ds.to_netcdf(paths[1], mode="w")
    assert "timeline" in try_read_simulation(paths[0].parent.parent, cfg.data).reason
    with xr.open_dataset(paths[0], decode_times=False) as source:
        ds = source.load()
    ds.vor.attrs["units"] = "m/s"
    ds.to_netcdf(paths[0], mode="w")
    assert "units" in try_read_simulation(paths[0].parent.parent, cfg.data).reason


def test_spinup_is_unit_invariant_and_rounds_hold_up():
    values = np.concatenate([np.tile([1.0, 3.0], 5), np.tile([1.99, 2.01], 10)])
    assert find_spinup_time(values, 10, 10, 2) == find_spinup_time(
        values * 1e-10, 10, 10, 2
    )
    assert find_spinup_time(np.ones(20), 10, 11, 2) is None
    assert find_spinup_time(np.ones(30), 10, 11, 2) == 10


def test_preparation_writes_grid_and_all_targets(simulation, monkeypatch, tmp_path):
    paths, _, cfg = simulation
    monkeypatch.setattr(preprocess, "load_config", lambda _: cfg)
    metadata, count = preprocess._extract_pairs(
        [paths[0].parent.parent], Path("unused"), tmp_path / "pairs.h5", 0
    )
    assert count == 4
    with h5py.File(tmp_path / "pairs.h5", "r") as handle:
        saved = DataMetadata.read_hdf5(handle)
        assert metadata.matches(saved)
        assert handle["x"].shape == (4, 6, 4, 12)
        assert handle["y"].shape == (4, 2, 4)
        assert saved.y_vars == tuple(cfg.data.y_vars)


def test_empty_training_and_cross_split_replicas_rejected(tmp_path):
    with pytest.raises(ValueError, match="training"):
        Splits([], [], []).validate()
    with pytest.raises(ValueError, match="replicas"):
        Splits([tmp_path / "code-1"], [], [tmp_path / "code-0"]).validate()


def test_no_usable_training_fails_explicitly(simulation, monkeypatch, tmp_path):
    paths, _, cfg = simulation
    cfg = replace(
        cfg,
        data=replace(cfg.data, windows=replace(cfg.data.windows, length=100)),
        model=replace(cfg.model, sfno=replace(cfg.model.sfno, in_channels=200)),
    )
    splits = Splits([], [], [paths[0].parent.parent])
    manifest = splits.save(tmp_path / "splits", "test", "test", cfg.data.split)
    monkeypatch.setattr(preprocess, "load_config", lambda _: cfg)
    with pytest.raises(ValueError, match="no usable training"):
        preprocess.run(Path("unused"), manifest)


def test_decoded_cf_time_is_supported_without_taking_ownership(simulation):
    from ml.data.isca_segment import read_segments

    paths, _, _ = simulation
    with read_segments(paths, decode_time=True) as ds:
        assert ds.time.dtype == object
        count, shape = validate_segment_dataset(ds, ["vor"], ["ucomp"])
        assert count == 12
        assert shape == (4, 12)
        assert ds.vor.values.shape == (12, 4, 12)


def test_convergence_plot_uses_the_detector_reference(simulation):
    from ml.config import SpinupConfig
    from ml.usecases.convergence import analyze

    paths, values, _ = simulation
    result = analyze(
        paths[0].parent.parent, SpinupConfig(100, 2, 2), ConvergenceConfig(100, 1), 2
    )
    expected = (values[result["spinup_time"] :] + 2).mean(axis=(0, 2))
    np.testing.assert_allclose(result["diagnostic_reference"], expected, rtol=1e-6)


@pytest.mark.parametrize("second_units", ["degC", ""])
def test_arbitrary_input_units_cannot_change_or_disappear(simulation, second_units):
    paths, _, cfg = simulation
    for index, path in enumerate(paths):
        with xr.open_dataset(path, decode_times=False) as source:
            ds = source.load()
        ds["temp"] = ds.ucomp.copy()
        ds.temp.attrs["units"] = "K" if index == 0 else second_units
        ds.to_netcdf(path, mode="w")
    cfg = replace(cfg.data, x_vars=["temp"])
    outcome = try_read_simulation(paths[0].parent.parent, cfg)
    assert outcome.samples is None
    assert "unit" in outcome.reason


def test_input_units_are_part_of_saved_identity(simulation):
    paths, _, cfg = simulation
    data = replace(cfg.data, x_vars=["temp"])
    metadata = []
    for units in ("K", "degC"):
        for path in paths:
            with xr.open_dataset(path, decode_times=False) as source:
                ds = source.load()
            ds["temp"] = ds.ucomp.copy()
            ds.temp.attrs["units"] = units
            ds.to_netcdf(path, mode="w")
        metadata.append(read_simulation(paths[0].parent.parent, data).metadata)
    assert metadata[0].input_units == ("K",)
    assert not metadata[0].matches(metadata[1])
    assert not DataMetadata.from_dict(metadata[0].to_dict()).matches(metadata[1])
