from pathlib import Path

import numpy as np
import xarray as xr

type SegmentsCache = dict[Path, xr.Dataset]

# I don't know :(
# Without this the ds is unreadable
def fix_time_units(ds: xr.Dataset) -> xr.Dataset:
    for v in ds.variables:
        if "units" in ds[v].attrs and "0000-00-00" in ds[v].attrs["units"]:
            ds[v].attrs["units"] = (
                ds[v].attrs["units"].replace("0000-00-00", "0001-01-01")
            )
        if ds[v].attrs.get("calendar") == "NO_CALENDAR":
            ds[v].attrs["calendar"] = "360_day"
    return ds

def read_segment(nc_path: Path, cache: SegmentsCache | None = None) -> xr.Dataset:
    if cache and nc_path in cache:
        return cache[nc_path]
    ds = xr.open_dataset(nc_path, decode_times=False)
    ds = fix_time_units(ds)
    if cache:
        cache[nc_path] = ds
    return ds

def aggregated_read_field(nc_paths: list[Path], field_name: str, cache: SegmentsCache | None = None):
    arrays = [read_segment(nc_path, cache)[field_name] for nc_path in nc_paths]
    return np.concatenate(arrays, axis=0)

def validate_segment_dataset(ds: xr.Dataset, x_vars: list[str], y_vars: list[str]):
    all_vars = list(dict.fromkeys(x_vars + y_vars))
    for var in all_vars:
        assert var in ds, f"variable '{var}' not in dataset"
        assert (
            "time" in ds[var].dims
        ), f"variable '{var}' has no time dimension in dataset"

    if "average_DT" in ds:
        dt = ds["average_DT"].values
        assert np.allclose(dt, dt[0], rtol=1e-3), f"inconsistent time steps in dataset"

    num_samples = ds.sizes["time"]
    spatial_shape = (ds.sizes["lat"], ds.sizes["lon"])
    ds.close()
    return num_samples, spatial_shape

def validate_segment(
    nc_path: Path, x_vars: list[str], y_vars: list[str], cache: SegmentsCache | None = None
) -> tuple[int, tuple]:
    ds = read_segment(nc_path, cache)
    return validate_segment_dataset(ds, x_vars, y_vars)