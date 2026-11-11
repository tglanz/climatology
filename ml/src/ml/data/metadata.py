"""The minimal coordinate, channel, unit, and selection identity for artifacts."""

from dataclasses import asdict, dataclass
import json

from ml.config import IscaDataConfig
from ml.data.climatology import known_units
from ml.diagnostics.grid import GaussianGrid

FORMAT_VERSION = 1


@dataclass(frozen=True)
class DataMetadata:
    grid: GaussianGrid
    data_config: dict
    input_units: tuple[str, ...]

    def __post_init__(self):
        if len(self.input_units) != len(self.x_vars) or not all(
            isinstance(unit, str) and unit for unit in self.input_units
        ):
            raise ValueError("every input channel needs a declared unit identity")

    @classmethod
    def from_config(
        cls,
        grid: GaussianGrid,
        cfg: IscaDataConfig,
        input_units: tuple[str, ...] | None = None,
    ) -> "DataMetadata":
        units = (
            tuple(known_units(var) for var in cfg.x_vars)
            if input_units is None
            else input_units
        )
        return cls(grid, asdict(cfg), units)

    @property
    def x_vars(self) -> tuple[str, ...]:
        return tuple(self.data_config["x_vars"])

    @property
    def y_vars(self) -> tuple[str, ...]:
        return tuple(self.data_config["y_vars"])

    @property
    def input_channels(self) -> int:
        return self.data_config["windows"]["length"] * len(self.x_vars)

    def to_dict(self) -> dict:
        return {
            "format_version": FORMAT_VERSION,
            "grid": self.grid.to_dict(),
            "data_config": self.data_config,
            "input_units": list(self.input_units),
        }

    @classmethod
    def from_dict(cls, values: dict) -> "DataMetadata":
        if (
            values.get("format_version") != FORMAT_VERSION
            or "input_units" not in values
        ):
            raise ValueError(
                "incompatible or unversioned data; regenerate with correctness preprocessing"
            )
        return cls(
            GaussianGrid.from_dict(values["grid"]),
            values["data_config"],
            tuple(values["input_units"]),
        )

    def validate_config(self, cfg: IscaDataConfig) -> None:
        if self.data_config != asdict(cfg):
            raise ValueError(
                "prepared data settings differ from the configuration; regenerate or use the original settings"
            )

    def matches(self, other: "DataMetadata") -> bool:
        return (
            self.data_config == other.data_config
            and self.input_units == other.input_units
            and self.grid.matches(other.grid)
        )

    def write_hdf5(self, handle) -> None:
        handle.attrs["metadata"] = json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def read_hdf5(cls, handle) -> "DataMetadata":
        if "metadata" not in handle.attrs:
            raise ValueError(
                "unversioned prepared data; regenerate with correctness preprocessing"
            )
        return cls.from_dict(json.loads(handle.attrs["metadata"]))
