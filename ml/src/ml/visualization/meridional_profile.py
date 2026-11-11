import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D


def setup_meridional_profile_axes(
    ax: Axes,
    title: str,
    xlabel: str,
    n_history: int = 10,
) -> tuple[list[Line2D], Line2D]:
    """
    Configure ax for a meridional profile (lat on y-axis) and create
    the line artists.

    Returns (pred_lines, truth_line) where pred_lines[0] is the latest
    prediction (solid, full opacity) and pred_lines[-1] is the oldest
    (faded gray). Callers update data via line.set_data(values, lats).
    """
    ax.set_title(title, fontsize=9, pad=3)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("latitude")
    ax.set_ylim(-90, 90)
    ax.grid(True, alpha=0.3)

    pred_lines = [
        ax.plot(
            [],
            [],
            color="tab:blue" if k == 0 else "gray",
            alpha=1.0 if k == 0 else max(0.08, 1.0 - k / max(n_history - 1, 1)),
            label="pred" if k == 0 else None,
        )[0]
        for k in range(n_history - 1, -1, -1)
    ]
    pred_lines.reverse()  # index 0 = latest

    (truth_line,) = ax.plot([], [], color="tab:orange", linestyle="--", label="truth")
    ax.legend(fontsize=8)

    return pred_lines, truth_line


def update_meridional_profile(
    ax: Axes,
    pred_lines: list[Line2D],
    truth_line: Line2D,
    pred_history: list[np.ndarray],
    truth: np.ndarray | None,
    pred_std: np.ndarray | None = None,
    latitudes: np.ndarray | None = None,
) -> None:
    # remove previous std band if any
    for coll in list(ax.collections):
        coll.remove()

    if pred_history:
        if latitudes is None or len(latitudes) != len(pred_history[0]):
            raise ValueError("profile coordinates are missing or incompatible")
        lats = latitudes
        for k, line in enumerate(pred_lines):
            idx = len(pred_history) - 1 - k
            if idx >= 0:
                line.set_data(pred_history[idx], lats)
            else:
                line.set_data([], [])
        if pred_std is not None:
            latest = pred_history[-1]
            ax.fill_betweenx(
                lats, latest - pred_std, latest + pred_std, alpha=0.2, color="tab:blue"
            )
        ax.relim()
        ax.autoscale_view(scaley=False)

    if truth is not None:
        if latitudes is None or len(latitudes) != len(truth):
            raise ValueError("truth coordinates are missing or incompatible")
        lats = latitudes
        truth_line.set_data(truth, lats)
        ax.relim()
        ax.autoscale_view(scaley=False)
