"""Named target diagnostics and half-open finite-run averaging intervals."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from ml.diagnostics.convergence import compute_time_mean_zonal_mean

if TYPE_CHECKING:
    from ml.config import ClimatologyConfig


@dataclass(frozen=True)
class TargetDiagnostic:
    name: str
    variable: str
    units: str
    label: str


_TARGETS = {
    name: TargetDiagnostic(name, variable, units, label)
    for name, variable, units, label in (
        ("time_mean_zonal_mean_ucomp", "ucomp", "m/s", "zonal wind"),
        ("time_mean_zonal_mean_vor", "vor", "1/s", "relative vorticity"),
        ("time_mean_zonal_mean_vcomp", "vcomp", "m/s", "meridional wind"),
    )
}


def diagnostic_for(name: str) -> TargetDiagnostic:
    try:
        return _TARGETS[name]
    except KeyError as exc:
        raise ValueError(f"unknown climatology diagnostic: {name!r}") from exc


def known_units(variable: str) -> str | None:
    return next(
        (target.units for target in _TARGETS.values() if target.variable == variable),
        None,
    )


def is_climatology_var(name: str) -> bool:
    return name in _TARGETS


def nc_var_for(diagnostic: str) -> str:
    return diagnostic_for(diagnostic).variable


def resolve_window(
    cfg: "ClimatologyConfig", t_s: int | None, t_c: int | None, t_n: int
) -> tuple[int, int]:
    def anchor(name: str) -> int:
        if name == "end":
            return t_n
        value = {"spinup": t_s, "convergence": t_c}.get(name)
        if value is None:
            raise ValueError(f"climatology anchor {name!r} is unavailable")
        return value

    if cfg.start_at is not None and cfg.end_at is not None:
        a, b = anchor(cfg.start_at), anchor(cfg.end_at)
    elif cfg.start_at is not None:
        a = anchor(cfg.start_at)
        b = a + cfg.length
    else:
        b = anchor(cfg.end_at)
        a = b - cfg.length
    if not 0 <= a < b <= t_n:
        raise ValueError(f"invalid climatology interval [{a}, {b}) for {t_n} snapshots")
    return a, b


def compute_climatology(
    diagnostic: str, field: np.ndarray, a: int, b: int
) -> np.ndarray:
    diagnostic_for(diagnostic)
    return compute_time_mean_zonal_mean(field, a, b)
