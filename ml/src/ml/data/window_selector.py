"""
Window selector: pick which (input, target) windows to extract from a
single simulation's flat timeline.

The selector is parameterized on two orthogonal axes:

- `mode` controls the stride between selected windows:
    - "tumbling": disjoint windows, stride = input_length + 1. Each
                  snapshot is in at most one (input, target) pair.
    - "rolling":  adjacent overlapping windows, stride = 1. Each
                  snapshot can appear as input in many pairs and as
                  target in one.
- `anchor` controls which end of the valid range the selection is
  anchored to. Only "latest" is currently supported: the latest
  selected window's target is at the very end of the valid range
  (n_valid - 1); earlier windows step back by `stride`.
- `max_per_simulation` optionally caps the number of selected windows
  per simulation. With `None`, all valid windows for the chosen anchor
  and mode are kept.

`select(n_valid)` returns a sorted list of indices into the
`valid_target_indices` array (already filtered by spinup elsewhere).
"""

from __future__ import annotations

import numpy as np

from ml.config import WindowsConfig


class WindowSelector:
    """Picks valid window indices from a simulation timeline."""

    def __init__(
        self,
        input_length: int,
        anchor: str,
        mode: str,
        count: int | None,
    ):
        self.input_length = input_length
        self.anchor = anchor
        self.mode = mode
        self.count = count

    def select(self, n_valid: int) -> list[int]:
        if n_valid <= 0:
            return []

        stride = 1 if self.mode == "rolling" else self.input_length + 1

        # Latest-anchored: the last selected index is n_valid - 1, and
        # earlier ones step back by `stride`. We build the list backward
        # then reverse to ascending order, which is what the caller
        # expects.
        indices = list(range(n_valid - 1, -1, -stride))
        indices.reverse()

        if self.count is None:
            return indices
        # `count` is a cap, not a requirement: silently take fewer if
        # the trajectory does not have enough valid windows.
        return indices[-self.count :]


def build_selector(cfg: WindowsConfig) -> WindowSelector:
    """Construct a `WindowSelector` from a `WindowsConfig`."""
    return WindowSelector(
        input_length=cfg.input_length,
        anchor=cfg.anchor,
        mode=cfg.mode,
        count=cfg.max_per_simulation,
    )
