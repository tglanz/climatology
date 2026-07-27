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
from ml.visualization.meridional_profile import setup_meridional_profile_axes, update_meridional_profile


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

def _run_gui_climatology(state: MonitorState, interval: float) -> None:
    import matplotlib.pyplot as mpl
    import matplotlib.ticker as ticker

    mpl.ion()
    fig = mpl.figure(figsize=(14, 6))
    gs = fig.add_gridspec(2, 3)
    ax_info    = fig.add_subplot(gs[0, :2])
    ax_chart   = fig.add_subplot(gs[1, :2])
    ax_profile = fig.add_subplot(gs[:, 2])

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
    fig.subplots_adjust(left=0.07, right=0.97, top=0.95, bottom=0.08, hspace=0.35, wspace=0.35)
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

    pred_lines, truth_line = setup_meridional_profile_axes(
        ax_profile,
        title="zonal mean u(lat): predicted vs truth",
        xlabel="u (m/s)",
        n_history=MonitorState._PROFILE_HISTORY_LEN,
    )

    loss_lines: dict[str, mpl.Line2D] = {}

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
            if train_key not in loss_lines:
                (loss_lines[train_key],) = ax_chart.plot(s.epochs, s.train_losses, label=f"{prefix}train")
                (loss_lines[val_key],)   = ax_chart.plot(s.epochs, s.val_losses,   label=f"{prefix}val", linestyle="--")
                ax_chart.legend()
            else:
                loss_lines[train_key].set_data(s.epochs, s.train_losses)
                loss_lines[val_key].set_data(s.epochs, s.val_losses)
        ax_chart.relim()
        ax_chart.autoscale_view()

        update_meridional_profile(
            ax_profile, pred_lines, truth_line,
            state.profile_pred_history, state.profile_truth,
            pred_std=state.profile_pred_std,
        )

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
        _run_gui_climatology(state, interval)
    else:
        _run_terminal(state, interval)
