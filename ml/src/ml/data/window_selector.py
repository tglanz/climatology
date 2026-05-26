"""
Window selector: choose the input-window start indices `t_0` to
materialize from a single simulation's flat timeline.

A window is `length` (= K) consecutive snapshots starting at `t_0`;
the next-step target sits at `t_0 + K`. The selector emits a strictly
increasing list of `t_0` values in [t_0_min, t_0_max], stepping by
`stride`, optionally capped to the first `limit` values.

Bounds:
    t_0_min = 0   if start_at == "beginning"
    t_0_min = t_s if start_at == "spinup"     (caller supplies t_s)
    t_0_max = M - K - 1            if end_at == "end"
    t_0_max = min(t_c, M - K - 1)  if end_at == "convergence" (caller supplies t_c)

`M - K - 1` is the largest `t_0` such that the next-step target
`t_0 + K` is still a valid timeline index in [0, M - 1].

See docs/pre-processing.md for the formal semantics and validation
rules across the spinup, convergence, and windows sections.
"""

from __future__ import annotations

from ml.config import WindowsConfig


class WindowSelector:
    """Picks input-window start indices for one simulation."""

    def __init__(self, cfg: WindowsConfig):
        self.cfg = cfg

    def select(
        self,
        timeline_length: int,
        t_s: int | None = None,
        t_c: int | None = None,
    ) -> list[int]:
        K = self.cfg.length
        M = timeline_length

        if self.cfg.start_at == "beginning":
            t0_min = 0
        else:
            assert t_s is not None, (
                "start_at='spinup' requires t_s to be supplied by the caller"
            )
            t0_min = t_s

        natural_max = M - K - 1
        if self.cfg.end_at == "end":
            t0_max = natural_max
        else:
            assert t_c is not None, (
                "end_at='convergence' requires t_c to be supplied by the caller"
            )
            t0_max = min(t_c, natural_max)

        if t0_min > t0_max:
            return []

        indices = list(range(t0_min, t0_max + 1, self.cfg.stride))
        if self.cfg.limit is not None:
            indices = indices[: self.cfg.limit]
        return indices


def build_selector(cfg: WindowsConfig) -> WindowSelector:
    """Construct a `WindowSelector` from a `WindowsConfig`."""
    return WindowSelector(cfg)
