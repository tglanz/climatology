import numpy as np
from matplotlib.axes import Axes


def plot_loss_curve(
    ax: Axes,
    epochs: list[int],
    train_losses: list[float],
    val_losses: list[float],
    threshold: float | None = 0.1,
) -> None:
    ax.plot(epochs, train_losses, label="train")
    val_arr = np.array(val_losses)
    if not np.all(np.isnan(val_arr)):
        ax.plot(epochs, val_arr, label="val")
    if threshold is not None:
        ax.axhline(threshold, color="gray", linestyle=":", linewidth=1, label=f"threshold ({threshold})")
    ax.set_xlabel("epoch")
    ax.set_ylabel("loss")
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)
