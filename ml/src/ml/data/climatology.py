"""
Climatology window resolution and computation.

Resolves symbolic anchor names to concrete snapshot indices, then
computes requested climatology diagnostics over [a, b), delegating
physical reductions to ml.diagnostics.
"""

from __future__ import annotations

import numpy as np

from ml.config import ClimatologyConfig
from ml.diagnostics.convergence import compute_time_mean_zonal_mean

# Maps diagnostic name -> underlying NC variable name.
# All entries here share the same reduction (time-mean zonal-mean);
# add new entries as new climatology diagnostics are needed.
_REGISTRY: dict[str, str] = {
    "time_mean_zonal_mean_ucomp": "ucomp",
    "time_mean_zonal_mean_vor": "vor",
    "time_mean_zonal_mean_vcomp": "vcomp",
}


def is_climatology_var(name: str) -> bool:
    return name in _REGISTRY


def nc_var_for(diagnostic: str) -> str:
    assert diagnostic in _REGISTRY, (
        f"unknown climatology diagnostic: {diagnostic!r} (known: {sorted(_REGISTRY)})"
    )
    return _REGISTRY[diagnostic]


def resolve_window(
    cfg: ClimatologyConfig,
    t_s: int | None,
    t_c: int | None,
    t_n: int,
) -> tuple[int, int]:
    """Resolve symbolic anchors in cfg to concrete snapshot indices [a, b)."""

    def anchor(name: str) -> int:
        if name == "spinup":
            assert t_s is not None, "climatology anchor 'spinup' requires t_s"
            return t_s
        if name == "convergence":
            assert t_c is not None, "climatology anchor 'convergence' requires t_c"
            return t_c
        if name == "end":
            return t_n
        raise ValueError(f"unknown anchor: {name!r}")

    if cfg.start_at is not None and cfg.end_at is not None:
        a = anchor(cfg.start_at)
        b = anchor(cfg.end_at)
    elif cfg.start_at is not None and cfg.length is not None:
        a = anchor(cfg.start_at)
        b = a + cfg.length
    else:
        b = anchor(cfg.end_at)
        a = b - cfg.length

    assert 0 <= a < b, f"climatology window [{a}, {b}) is invalid"
    assert b <= t_n, f"climatology window end {b} exceeds trajectory length {t_n}"

    return a, b


def compute_climatology(
    diagnostic: str,
    field: np.ndarray,
    a: int,
    b: int,
) -> np.ndarray:
    """Compute a single climatology diagnostic over snapshots [a, b).

    Returns shape (H,) -- time-mean zonal-mean of the field.
    """
    assert diagnostic in _REGISTRY, (
        f"unknown climatology diagnostic: {diagnostic!r}"
    )
    return compute_time_mean_zonal_mean(field, a, b)
