"""Coordinates and quadrature for the full Gaussian grids produced by Isca."""

from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np


@lru_cache(maxsize=32)
def _gaussian_rule(size: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(size)
    latitudes = np.rad2deg(np.arcsin(nodes))
    latitudes.setflags(write=False)
    weights.setflags(write=False)
    return latitudes, weights / 2


def gaussian_latitude_weights(latitudes: np.ndarray) -> np.ndarray:
    """Return normalized area weights in the supplied latitude order."""
    lat = np.asarray(latitudes, dtype=np.float64)
    if lat.ndim != 1 or len(lat) < 2 or not np.isfinite(lat).all():
        raise ValueError("Gaussian latitude coordinates must be a finite 1D array")
    expected, weights = _gaussian_rule(len(lat))
    if np.allclose(lat, expected, rtol=0, atol=5e-5):
        return weights.copy()
    if np.allclose(lat, expected[::-1], rtol=0, atol=5e-5):
        return weights[::-1].copy()
    raise ValueError("latitude coordinates do not match a Gaussian grid")


@dataclass(frozen=True, eq=False)
class GaussianGrid:
    """Validated coordinates; array rows retain their original orientation."""

    latitudes: np.ndarray
    longitudes: np.ndarray
    weights: np.ndarray = field(init=False, repr=False)

    def __post_init__(self):
        lat = np.array(self.latitudes, dtype=np.float64, copy=True)
        lon = np.array(self.longitudes, dtype=np.float64, copy=True)
        weights = gaussian_latitude_weights(lat)
        if lon.ndim != 1 or len(lon) < 4 or not np.isfinite(lon).all():
            raise ValueError("longitude coordinates must be a finite 1D array")
        step = 360 / len(lon)
        if not np.allclose(np.diff(lon), step, rtol=0, atol=5e-5):
            raise ValueError(
                "longitude coordinates must be uniform and periodic without a duplicate endpoint"
            )
        for name, values in (
            ("latitudes", lat),
            ("longitudes", lon),
            ("weights", weights),
        ):
            values.setflags(write=False)
            object.__setattr__(self, name, values)

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.latitudes), len(self.longitudes)

    @property
    def south_to_north(self) -> bool:
        return bool(self.latitudes[0] < self.latitudes[-1])

    def matches(self, other: "GaussianGrid") -> bool:
        return (
            self.shape == other.shape
            and np.allclose(self.latitudes, other.latitudes, rtol=0, atol=5e-5)
            and np.allclose(self.longitudes, other.longitudes, rtol=0, atol=5e-5)
        )

    def to_dict(self) -> dict:
        return {
            "kind": "legendre-gauss",
            "latitudes": self.latitudes.tolist(),
            "longitudes": self.longitudes.tolist(),
        }

    @classmethod
    def from_dict(cls, values: dict) -> "GaussianGrid":
        if values.get("kind") != "legendre-gauss":
            raise ValueError("unsupported saved grid; regenerate the experiment")
        return cls(values["latitudes"], values["longitudes"])
