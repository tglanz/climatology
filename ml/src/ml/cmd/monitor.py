import os
import time
from pathlib import Path

import click
import numpy as np
import plotext as plt
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ml.config import Config, load as load_config
from ml.common.monitor import MonitorState, Section, RunSeries


INFO_RATIO = 1
CHART_RATIO = 3
PANEL_OVERHEAD = 4  # borders + padding


# --- generic renderers (no business logic) ---

def _info_panel(title: str, sections: list[Section]) -> Panel:
    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold dim")
    table.add_column()
    table.add_row(f"[bold]{title}[/bold]", "")
    for section in sections:
        table.add_row("", "")
        table.add_row(f"[bold]{section.name}[/bold]", "")
        for key, value in section.items:
            table.add_row(f"  {key}", value)
    return Panel(table, title="Experiment")


def _sections_to_text(title: str, sections: list[Section]) -> str:
    lines = [title]
    for section in sections:
        lines.append("")
        lines.append(section.name)
        for key, value in section.items:
            lines.append(f"  {key:<12} {value}")
    return "\n".join(lines)


def _sections_to_two_columns(title: str, sections: list[Section]) -> tuple[str, str]:
    mid = len(sections) // 2
    def _render(secs: list[Section]) -> str:
        lines = []
        for section in secs:
            lines.append(section.name)
            for key, value in section.items:
                lines.append(f"  {key:<12} {value}")
            lines.append("")
        return "\n".join(lines)
    return title, _render(sections[:mid]), _render(sections[mid:])


def _chart_panel(series: list[RunSeries], term_width: int, term_height: int) -> Panel:
    if not series:
        return Panel(Text("Waiting for metrics..."), title="Loss")

    chart_w = int(term_width * CHART_RATIO / (INFO_RATIO + CHART_RATIO)) - PANEL_OVERHEAD
    chart_h = term_height - PANEL_OVERHEAD

    plt.clear_figure()
    plt.theme("dark")
    plt.plot_size(chart_w, chart_h)
    plt.xlabel("epoch")
    plt.ylabel("loss")

    all_epochs: list[int] = []
    for s in series:
        prefix = f"{s.label} " if s.label else ""
        all_epochs.extend(s.epochs)
        plt.plot(s.epochs, s.train_losses, label=f"{prefix}train")
        plt.plot(s.epochs, s.val_losses,   label=f"{prefix}val")

    if all_epochs:
        unique = sorted(set(all_epochs))
        step = max(1, len(unique) // 15)
        ticks = unique[::step]
        if unique[-1] not in ticks:
            ticks.append(unique[-1])
        plt.xticks(ticks)

    return Panel(Text.from_ansi(plt.build()), title="Loss")


# --- terminal UI ---

def _run_terminal(state: MonitorState, interval: float) -> None:
    console = Console()
    with Live(console=console, screen=True, refresh_per_second=1) as live:
        while True:
            state.update()
            size = os.get_terminal_size()
            layout = Layout()
            layout.split_row(
                Layout(_info_panel(state.title, state.sections), name="info", ratio=INFO_RATIO),
                Layout(_chart_panel(state.series, size.columns, size.lines), name="chart", ratio=CHART_RATIO),
            )
            live.update(layout)
            time.sleep(interval)


# --- GUI ---

def _run_gui(state: MonitorState, interval: float) -> None:
    import matplotlib.pyplot as mpl
    import matplotlib.ticker as ticker

    mpl.ion()
    fig = mpl.figure(figsize=(14, 8))
    gs = fig.add_gridspec(3, 3)
    ax_info    = fig.add_subplot(gs[0, 0])
    ax_chart   = fig.add_subplot(gs[0, 1:])
    ax_spatial = fig.add_subplot(gs[1, :2])
    ax_zonal   = fig.add_subplot(gs[1, 2])
    ax_power   = fig.add_subplot(gs[2, :])

    ax_info.axis("off")
    info_title = ax_info.text(
        0.05, 0.99, "", transform=ax_info.transAxes,
        verticalalignment="top", fontfamily="monospace", fontsize=9, fontweight="bold",
    )
    info_left = ax_info.text(
        0.05, 0.88, "", transform=ax_info.transAxes,
        verticalalignment="top", fontfamily="monospace", fontsize=9,
    )
    info_right = ax_info.text(
        0.52, 0.88, "", transform=ax_info.transAxes,
        verticalalignment="top", fontfamily="monospace", fontsize=9,
    )

    ax_chart.set_yscale("linear")
    fig.subplots_adjust(left=0.05, right=0.97, top=0.96, bottom=0.06, hspace=0.45, wspace=0.3)
    ax_chart.set_title("loss per epoch")
    ax_chart.set_xlabel("epoch")
    ax_chart.set_ylabel("loss")
    ax_chart.grid(True, alpha=0.3)
    ax_chart.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    if state.target_loss is not None:
        ax_chart.axhline(
            state.target_loss, color="red", linestyle=":", linewidth=1,
            label=f"target ({state.target_loss})",
        )

    ax_spatial.set_title("spatial mean error", fontsize=9, pad=3)
    ax_spatial.set_xlabel("lon")
    ax_spatial.set_ylabel("lat")
    spatial_im = ax_spatial.imshow(
        [[0]], aspect="auto", origin="lower", cmap="viridis",
        extent=[0, 360, -90, 90],
    )
    fig.colorbar(spatial_im, ax=ax_spatial, fraction=0.02, pad=0.01)

    ax_zonal.set_title("zonal mean error")
    ax_zonal.set_xlabel("error")
    ax_zonal.set_ylabel("lat")
    ax_zonal.set_ylim(-90, 90)
    n_hist = MonitorState._ZONAL_HISTORY_LEN
    zonal_lines = [
        ax_zonal.plot([], [], color="tab:blue" if k == 0 else "gray", alpha=1.0 if k == 0 else max(0.08, 1 - k / (n_hist - 1)))[0]
        for k in range(n_hist - 1, -1, -1)
    ]
    zonal_lines.reverse()  # index 0 = latest

    ax_power.set_title("power spectrum", fontsize=9, pad=3)
    ax_power.set_xlabel("zonal wavenumber")
    ax_power.set_ylabel("power")
    ax_power.set_yscale("log")
    ax_power.set_xscale("log")
    error_power_line,  = ax_power.plot([], [], label="error",  color="tab:red")
    signal_power_line, = ax_power.plot([], [], label="signal", color="tab:blue")
    cutoff = state._cfg.model.active_sub_config().n_modes[0]
    ax_power.axvline(cutoff, color="gray", linestyle=":", linewidth=1, label=f"n_modes={cutoff}")
    ax_power.legend(fontsize=8)

    lines: dict[str, mpl.Line2D] = {}

    while mpl.fignum_exists(fig.number):
        state.update()
        title, left, right = _sections_to_two_columns(state.title, state.sections)
        info_title.set_text(title)
        info_left.set_text(left)
        info_right.set_text(right)

        for s in state.series:
            prefix = f"{s.label} " if s.label else ""
            train_key = f"{s.run_id}_train"
            val_key = f"{s.run_id}_val"
            if train_key not in lines:
                (lines[train_key],) = ax_chart.plot(s.epochs, s.train_losses, label=f"{prefix}train")
                (lines[val_key],)   = ax_chart.plot(s.epochs, s.val_losses,   label=f"{prefix}val", linestyle="--")
                ax_chart.legend()
            else:
                lines[train_key].set_data(s.epochs, s.train_losses)
                lines[val_key].set_data(s.epochs, s.val_losses)

        ax_chart.relim()
        ax_chart.autoscale_view()

        if state.spatial_error is not None:
            spatial_im.set_data(state.spatial_error)
            spatial_im.set_clim(vmin=0, vmax=state.spatial_error.max())

        if state.zonal_mean_history:
            lats = np.linspace(-90, 90, len(state.zonal_mean_history[0]))
            history = state.zonal_mean_history
            for k, line in enumerate(zonal_lines):
                idx = len(history) - 1 - k
                if idx >= 0:
                    line.set_data(history[idx], lats)
                else:
                    line.set_data([], [])
            ax_zonal.relim()
            ax_zonal.autoscale_view(scaley=False)

        if state.error_power is not None and state.signal_power is not None:
            wavenumbers = np.arange(1, len(state.error_power) + 1)  # start at 1 for log scale
            error_power_line.set_data(wavenumbers, state.error_power)
            signal_power_line.set_data(wavenumbers, state.signal_power)
            ax_power.relim()
            ax_power.autoscale_view()

        fig.canvas.draw()
        fig.canvas.flush_events()
        mpl.pause(interval)


# --- CLI ---

@click.group()
def monitor():
    """Monitor ML processes."""
    pass


@monitor.command()
@click.option("-c", "--config", "config_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--interval", default=2.0, show_default=True, help="Poll interval in seconds.")
@click.option("--gui", is_flag=True, default=False, help="Use a matplotlib window instead of terminal UI.")
def training(config_path: Path, interval: float, gui: bool):
    """Monitor training metrics in real-time."""
    cfg = load_config(config_path)
    state = MonitorState(cfg)
    if gui:
        _run_gui(state, interval)
    else:
        _run_terminal(state, interval)
