"""NetCDF readers with explicit dataset ownership and cache lifetime."""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import xarray as xr
from ml.data.climatology import known_units

type SegmentsCache = dict[Path, xr.Dataset]

_UNIT_ALIASES = {
    "vor": {"1/s", "s-1", "s^-1"},
    "ucomp": {"m/s", "ms-1", "ms^-1"},
    "vcomp": {"m/s", "ms-1", "ms^-1"},
}


def fix_time_units(ds: xr.Dataset) -> xr.Dataset:
    for name in ds.variables:
        attrs = ds[name].attrs
        if "0000-00-00" in attrs.get("units", ""):
            attrs["units"] = attrs["units"].replace("0000-00-00", "0001-01-01")
        if attrs.get("calendar") == "NO_CALENDAR":
            attrs["calendar"] = "360_day"
    return ds


def read_segment(nc_path: Path, cache: SegmentsCache | None = None) -> xr.Dataset:
    if cache is not None and nc_path in cache:
        return cache[nc_path]
    ds = fix_time_units(xr.open_dataset(nc_path, decode_times=False))
    if cache is not None:
        cache[nc_path] = ds
    return ds


@dataclass
class SegmentReader:
    cache: SegmentsCache = field(default_factory=dict)

    def read(self, path: Path) -> xr.Dataset:
        return read_segment(path, self.cache)

    def __enter__(self) -> "SegmentReader":
        return self

    def __exit__(self, *_):
        for ds in self.cache.values():
            ds.close()
        self.cache.clear()


def aggregated_read_field(
    nc_paths: list[Path], field_name: str, cache: SegmentsCache | None = None
) -> np.ndarray:
    if cache is None:
        with SegmentReader() as reader:
            return aggregated_read_field(nc_paths, field_name, reader.cache)
    return np.concatenate(
        [read_segment(p, cache)[field_name].values for p in nc_paths], axis=0
    )


def field_units(ds: xr.Dataset, variable: str) -> str:
    units = ds[variable].attrs.get("units", "").replace(" ", "").replace("**", "^")
    if not units or (
        variable in _UNIT_ALIASES and units not in _UNIT_ALIASES[variable]
    ):
        raise ValueError(f"incompatible or missing units for {variable}: {units!r}")
    return known_units(variable) or units


def _finite_coordinate(values: np.ndarray, name: str) -> bool:
    if np.issubdtype(values.dtype, np.number):
        return bool(np.isfinite(values).all())
    if np.issubdtype(values.dtype, np.datetime64):
        return bool((~np.isnat(values)).all())
    if name == "time":
        try:
            xr.CFTimeIndex(values)
            return True
        except (TypeError, ValueError):
            return False
    return False


def validate_segment_dataset(ds: xr.Dataset, x_vars: list[str], y_vars: list[str]):
    for coordinate in ("time", "lat", "lon"):
        if coordinate not in ds.coords or ds[coordinate].dims != (coordinate,):
            raise ValueError(f"missing or invalid {coordinate} coordinate")
        if not _finite_coordinate(ds[coordinate].values, coordinate):
            raise ValueError(f"nonfinite {coordinate} coordinate")
    for var in dict.fromkeys(x_vars + y_vars):
        if var not in ds or ds[var].dims != ("time", "lat", "lon"):
            raise ValueError(f"variable {var!r} must have dimensions (time, lat, lon)")
        field_units(ds, var)
        if not np.isfinite(ds[var].values).all():
            raise ValueError(f"nonfinite values in {var}")
    if ds.sizes["time"] == 0:
        raise ValueError("empty segment")
    if "average_DT" in ds:
        dt = np.atleast_1d(ds["average_DT"].values)
        if np.issubdtype(dt.dtype, np.timedelta64):
            dt = dt.astype(np.float64)
        if (
            dt.size == 0
            or not np.isfinite(dt).all()
            or np.any(dt <= 0)
            or not np.allclose(dt, dt[0], rtol=1e-6)
        ):
            raise ValueError("inconsistent time averaging intervals")
    return ds.sizes["time"], (ds.sizes["lat"], ds.sizes["lon"])


def validate_segment(
    nc_path: Path,
    x_vars: list[str],
    y_vars: list[str],
    cache: SegmentsCache | None = None,
) -> tuple[int, tuple]:
    if cache is None:
        with SegmentReader() as reader:
            return validate_segment_dataset(reader.read(nc_path), x_vars, y_vars)
    return validate_segment_dataset(read_segment(nc_path, cache), x_vars, y_vars)


def read_segments(
    paths: str | Path | list[str | Path], decode_time: bool = False
) -> xr.Dataset:
    ds = xr.open_mfdataset(
        paths,
        combine="by_coords",
        data_vars="minimal",
        coords="minimal",
        compat="override",
        decode_times=False,
        preprocess=fix_time_units,
    )
    return _decode_time(ds) if decode_time else ds


def _decode_time(ds: xr.Dataset) -> xr.Dataset:
    return xr.decode_cf(
        ds,
        decode_times=xr.coders.CFDatetimeCoder(use_cftime=True),
        decode_timedelta=True,
    )
