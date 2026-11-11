import numpy as np
from matplotlib.axes import Axes


def plot_loss_curve(
    ax: Axes,
    epochs: list[int],
    train_losses: list[float],
    val_losses: list[float],
    threshold: float | None = None,
) -> None:
    ax.plot(epochs, train_losses, label="train")
    val_arr = np.array(val_losses)
    if not np.all(np.isnan(val_arr)):
        ax.plot(epochs, val_arr, label="val")
    if threshold is not None:
        ax.axhline(
            threshold,
            color="gray",
            linestyle=":",
            linewidth=1,
            label=f"threshold ({threshold})",
        )
    ax.set_xlabel("epoch")
    ax.set_ylabel("normalized-target loss")
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_notebook_training_curve(csv_path):
    """Notebook objective curve without an invented stopping threshold."""
    import csv
    import matplotlib.pyplot as plt

    epochs, train_losses, val_losses = [], [], []
    with open(csv_path) as stream:
        for row in csv.DictReader(stream):
            epochs.append(int(row["epoch"]))
            train_losses.append(float(row["train_loss"]))
            value = row.get("val_loss", "")
            val_losses.append(float(value) if value else float("nan"))
    fig, ax = plt.subplots(figsize=(7, 3.5))
    plot_loss_curve(ax, epochs, train_losses, val_losses)
    ax.set_title("Training loss curve")
    plt.tight_layout()
    return fig
