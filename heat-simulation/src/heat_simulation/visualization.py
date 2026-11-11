"""Snapshot and animation views for the heat demonstration."""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def plot_snapshots(snapshots, snapshot_times, source_temp):
    _, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    times = [0] + snapshot_times

    for ax, snapshot, time in zip(axes, snapshots, times):
        im = ax.imshow(snapshot, cmap="hot", origin="lower", vmin=0, vmax=source_temp)
        ax.set_title(f"Time step: {time}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        plt.colorbar(im, ax=ax, label="Temperature")

    plt.tight_layout()
    plt.show()


def animate_frames(frames, source_temp, frame_interval):
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(frames[0], cmap="hot", origin="lower", vmin=0, vmax=source_temp)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    plt.colorbar(im, ax=ax, label="Temperature")
    title = ax.set_title("Time step: 0")

    def update(frame_idx):
        im.set_array(frames[frame_idx])
        title.set_text(f"Time step: {frame_idx * frame_interval}")
        return [im, title]

    anim = FuncAnimation(fig, update, frames=len(frames), interval=50, blit=True)
    plt.close()

    return anim
