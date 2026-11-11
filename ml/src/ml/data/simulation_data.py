"""Shared mechanics for chronological, time-major simulation inputs."""

from pathlib import Path
import numpy as np
from ml.data.isca_segment import SegmentsCache, read_segment

CONVERGENCE_DIAGNOSTIC_VAR = "ucomp"


def build_timeline(paths: list[Path], lengths: list[int]) -> list[tuple[Path, int]]:
    return [
        (path, t)
        for path, length in zip(paths, lengths, strict=True)
        for t in range(length)
    ]


def stack_input_windows(
    timeline: list[tuple[Path, int]],
    starts: list[int],
    length: int,
    variables: list[str],
    cache: SegmentsCache,
) -> np.ndarray:
    """Stack channels in time order, then configured variable order."""
    windows = []
    for start in starts:
        channels = []
        for offset in range(length):
            path, index = timeline[start + offset]
            ds = read_segment(path, cache)
            for variable in variables:
                channels.append(ds[variable].isel(time=index).values)
        windows.append(np.stack(channels, axis=0))
    return np.stack(windows, axis=0)


def extract_windows(vor_full: np.ndarray, t_s: int, K: int, stride: int) -> np.ndarray:
    T = vor_full.shape[0]
    windows = [vor_full[t : t + K] for t in range(t_s, T - K + 1, stride)]
    if not windows:
        return np.empty((0, K, *vor_full.shape[1:]), dtype=vor_full.dtype)
    return np.stack(windows, axis=0)
