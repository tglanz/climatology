"""One owner for simulation validation, selection, inputs, and all target profiles."""

from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ml.config import IscaDataConfig
from ml.data.climatology import compute_climatology, nc_var_for, resolve_window
from ml.data.isca_segment import (
    SegmentReader,
    SegmentsCache,
    read_segment,
    validate_segment_dataset,
    field_units,
)
from ml.data.metadata import DataMetadata
from ml.data.window_selector import build_selector
from ml.diagnostics.convergence import find_zonal_mean_convergence_time
from ml.diagnostics.enstrophy import mean_enstrophy
from ml.diagnostics.grid import GaussianGrid
from ml.diagnostics.spinup import find_spinup_time

CONVERGENCE_DIAGNOSTIC_VAR = "ucomp"


@dataclass
class SimulationSamples:
    sim_dir: Path
    metadata: DataMetadata
    x_windows: np.ndarray
    y_windows: np.ndarray
    starts: tuple[int, ...]
    t_s: int | None
    t_c: int | None
    target_interval: tuple[int, int]
    timeline_length: int
    predictions: np.ndarray | None = None

    @property
    def pred_profile(self) -> np.ndarray | None:
        return None if self.predictions is None else self.predictions.mean(axis=0)

    @property
    def code(self) -> str:
        return self.sim_dir.name.rsplit("-", 1)[0]

    @property
    def lat(self) -> np.ndarray:
        return self.metadata.grid.latitudes

    @property
    def truth_profile(self) -> np.ndarray:
        return self.y_windows[0]


@dataclass
class SimulationOutcome:
    sim_dir: Path
    samples: SimulationSamples | None
    reason: str = ""


@dataclass
class SimulationSource:
    paths: list[Path]
    lengths: list[int]
    grid: GaussianGrid
    reader: SegmentReader
    input_units: tuple[str, ...]
    fields: dict[str, np.ndarray] = field(default_factory=dict)

    @property
    def length(self) -> int:
        return sum(self.lengths)

    def read_field(self, name: str) -> np.ndarray:
        if name not in self.fields:
            self.fields[name] = np.concatenate(
                [self.reader.read(p)[name].values for p in self.paths], axis=0
            )
        return self.fields[name]


def list_segment_files(sim_dir: Path, cfg: IscaDataConfig) -> list[Path]:
    return sorted(sim_dir.glob(cfg.segment_pattern))


@contextmanager
def open_simulation(sim_dir: Path, cfg: IscaDataConfig):
    paths = list_segment_files(sim_dir, cfg)
    if not paths:
        raise ValueError("no segments matching segment_pattern")
    variables = list(
        dict.fromkeys(
            cfg.x_vars
            + [nc_var_for(v) for v in cfg.y_vars]
            + (["vor"] if cfg.spinup is not None else [])
            + ([CONVERGENCE_DIAGNOSTIC_VAR] if cfg.convergence is not None else [])
        )
    )
    with SegmentReader() as reader:
        grid = None
        times, lengths, averaging_intervals = [], [], []
        time_metadata = None
        unit_contract = None
        for path in paths:
            ds = reader.read(path)
            length, _ = validate_segment_dataset(ds, variables, [])
            units = {var: field_units(ds, var) for var in variables}
            if unit_contract is not None and units != unit_contract:
                raise ValueError("field units changed across segments")
            unit_contract = units
            current = GaussianGrid(ds.lat.values, ds.lon.values)
            if grid is not None and not grid.matches(current):
                raise ValueError(f"grid changed across segments: {path}")
            grid = current
            for coordinate, allowed in (
                ("lat", {"degrees_N", "degrees_north", "degree_north"}),
                ("lon", {"degrees_E", "degrees_east", "degree_east"}),
            ):
                if ds[coordinate].attrs.get("units") not in allowed:
                    raise ValueError(f"{coordinate} must have degree units")
            attrs = ds.time.attrs
            current_time_metadata = (attrs.get("units"), attrs.get("calendar"))
            if (
                not current_time_metadata[0]
                or " since " not in current_time_metadata[0]
            ):
                raise ValueError("time coordinate needs declared units and an epoch")
            if time_metadata is not None and time_metadata != current_time_metadata:
                raise ValueError("time units or calendar changed across segments")
            time_metadata = current_time_metadata
            times.append(np.asarray(ds.time.values, dtype=np.float64))
            lengths.append(length)
            if "average_DT" in ds:
                averaging_intervals.extend(ds.average_DT.values.ravel().tolist())
        delta = np.diff(np.concatenate(times))
        if delta.size and (
            np.any(delta <= 0) or not np.allclose(delta, delta[0], rtol=1e-6, atol=1e-9)
        ):
            raise ValueError(
                "timeline must be chronological and uniformly spaced without gaps or duplicates"
            )
        if averaging_intervals and not np.allclose(
            averaging_intervals, averaging_intervals[0], rtol=1e-6
        ):
            raise ValueError("time averaging interval changed across segments")
        yield SimulationSource(
            paths,
            lengths,
            grid,
            reader,
            tuple(unit_contract[var] for var in cfg.x_vars),
        )


def build_timeline(paths: list[Path], lengths: list[int]) -> list[tuple[Path, int]]:
    return [
        (path, index)
        for path, length in zip(paths, lengths, strict=True)
        for index in range(length)
    ]


def stack_input_windows(
    timeline: list[tuple[Path, int]],
    starts: list[int],
    length: int,
    variables: list[str],
    cache: SegmentsCache,
) -> np.ndarray:
    windows = []
    for start in starts:
        if start < 0 or start + length > len(timeline):
            raise ValueError("input window exceeds the simulation timeline")
        channels = [
            read_segment(path, cache)[variable].isel(time=index).values
            for path, index in timeline[start : start + length]
            for variable in variables
        ]
        windows.append(np.stack(channels))
    if not windows:
        raise ValueError("no valid input windows")
    return np.stack(windows).astype(np.float32)


def select_samples(source: SimulationSource, cfg: IscaDataConfig):
    t_s = t_c = None
    if cfg.spinup is not None:
        t_s = find_spinup_time(
            mean_enstrophy(source.read_field("vor"), source.grid.latitudes),
            **cfg.spinup.to_kwargs(),
        )
        if t_s is None:
            raise ValueError("spinup stability criterion not reached")
    if cfg.convergence is not None:
        t_c = find_zonal_mean_convergence_time(
            source.read_field(CONVERGENCE_DIAGNOSTIC_VAR),
            source.grid.latitudes,
            t_s if t_s is not None else 0,
            **cfg.convergence.to_kwargs(),
        )
        if t_c is None:
            raise ValueError("convergence criterion not reached")
    interval = resolve_window(cfg.climatology, t_s, t_c, source.length)
    starts = build_selector(cfg.windows).select(source.length, t_s, t_c)
    if not starts:
        raise ValueError("no valid input windows")
    return starts, interval, t_s, t_c


def read_simulation(sim_dir: Path, cfg: IscaDataConfig) -> SimulationSamples:
    with open_simulation(sim_dir, cfg) as source:
        starts, (a, b), t_s, t_c = select_samples(source, cfg)
        target = np.stack(
            [
                compute_climatology(name, source.read_field(nc_var_for(name)), a, b)
                for name in cfg.y_vars
            ]
        ).astype(np.float32)
        xs = stack_input_windows(
            build_timeline(source.paths, source.lengths),
            starts,
            cfg.windows.length,
            cfg.x_vars,
            source.reader.cache,
        )
        ys = np.repeat(target[None], len(starts), axis=0)
        return SimulationSamples(
            sim_dir.resolve(),
            DataMetadata.from_config(source.grid, cfg, source.input_units),
            xs,
            ys,
            tuple(starts),
            t_s,
            t_c,
            (a, b),
            source.length,
        )


def try_read_simulation(sim_dir: Path, cfg: IscaDataConfig) -> SimulationOutcome:
    try:
        return SimulationOutcome(sim_dir.resolve(), read_simulation(sim_dir, cfg))
    except (ValueError, OSError, KeyError) as exc:
        return SimulationOutcome(sim_dir.resolve(), None, str(exc))


def extract_windows(vor_full: np.ndarray, t_s: int, K: int, stride: int) -> np.ndarray:
    if K < 1 or stride < 1 or t_s < 0:
        raise ValueError("invalid input-window settings")
    windows = [vor_full[t : t + K] for t in range(t_s, len(vor_full) - K + 1, stride)]
    return (
        np.stack(windows)
        if windows
        else np.empty((0, K, *vor_full.shape[1:]), dtype=vor_full.dtype)
    )
