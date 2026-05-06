import csv
import os
import time
from pathlib import Path

import click
import plotext as plt
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ml.config import Config, load as load_config


EPOCH_METRICS_FILE = "epoch-metrics.csv"
INFO_RATIO = 1
CHART_RATIO = 3
PANEL_OVERHEAD = 4  # borders + padding


def _read_metrics(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _info_panel(cfg: Config, rows: list[dict]) -> Panel:
    t = cfg.training
    exp_name = cfg.data.experiment_dir.name

    table = Table.grid(padding=(0, 1))
    table.add_column(style="dim")
    table.add_column()

    table.add_row("experiment", exp_name)
    table.add_row("loss", t.loss)
    table.add_row("optimizer", t.optimizer)
    table.add_row("epochs", str(t.epochs))
    table.add_row("batch_size", str(t.batch_size))
    table.add_row("lr_init", str(t.learning_rate))
    table.add_row("lr_decay", f"{t.lr_decay_factor} / {t.lr_decay_every} ep")
    if t.target_loss is not None:
        table.add_row("target_loss", str(t.target_loss))

    if rows:
        by_run: dict[str, list[dict]] = {}
        for r in rows:
            by_run.setdefault(r["run_id"], []).append(r)

        table.add_row("", "")
        for run_id, run_rows in by_run.items():
            last = run_rows[-1]
            best_row = min(run_rows, key=lambda r: float(r["val_loss"]))
            table.add_row("run", run_id)
            table.add_row("epoch", f"{last['epoch']} / {t.epochs}")
            table.add_row("val_loss", f"{float(last['val_loss']):.6f}")
            table.add_row("train_loss", f"{float(last['train_loss']):.6f}")
            table.add_row("best_val", f"{float(best_row['val_loss']):.6f} @ ep {best_row['epoch']}")
            table.add_row("lr", last["learning_rate"])
            table.add_row("", "")

    return Panel(table, title="Experiment")


def _chart_panel(rows: list[dict], term_width: int, term_height: int) -> Panel:
    if not rows:
        return Panel(Text("Waiting for metrics..."), title="Loss")

    total_ratio = INFO_RATIO + CHART_RATIO
    chart_w = int(term_width * CHART_RATIO / total_ratio) - PANEL_OVERHEAD
    chart_h = term_height - PANEL_OVERHEAD

    by_run: dict[str, list[dict]] = {}
    for r in rows:
        by_run.setdefault(r["run_id"], []).append(r)

    plt.clear_figure()
    plt.theme("dark")
    plt.plot_size(chart_w, chart_h)
    plt.xlabel("epoch")
    plt.ylabel("loss")

    all_epochs: list[int] = []
    for run_id, run_rows in by_run.items():
        short_id = run_id[-8:]
        epochs = [int(r["epoch"]) for r in run_rows]
        all_epochs.extend(epochs)
        plt.plot(epochs, [float(r["train_loss"]) for r in run_rows], label=f"{short_id} train")
        plt.plot(epochs, [float(r["val_loss"]) for r in run_rows], label=f"{short_id} val")

    if all_epochs:
        unique = sorted(set(all_epochs))
        max_ticks = 15
        step = max(1, len(unique) // max_ticks)
        ticks = unique[::step]
        if unique[-1] not in ticks:
            ticks.append(unique[-1])
        plt.xticks(ticks)

    chart = plt.build()
    return Panel(Text.from_ansi(chart), title="Loss")


def _build_layout(cfg: Config, rows: list[dict], term_width: int, term_height: int) -> Layout:
    layout = Layout()
    layout.split_row(
        Layout(_info_panel(cfg, rows), name="info", ratio=INFO_RATIO),
        Layout(_chart_panel(rows, term_width, term_height), name="chart", ratio=CHART_RATIO),
    )
    return layout


@click.group()
def monitor():
    """Monitor ML processes."""
    pass


@monitor.command()
@click.option(
    "-c", "--config", "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option("--interval", default=2.0, show_default=True, help="Poll interval in seconds.")
@click.option("--gui", is_flag=True, default=False, help="Use a matplotlib window instead of terminal UI.")
def training(config_path: Path, interval: float, gui: bool):
    """Monitor training metrics in real-time."""
    cfg = load_config(config_path)
    metrics_file = cfg.paths.training_dir / EPOCH_METRICS_FILE

    if gui:
        _run_gui(cfg, metrics_file, interval)
    else:
        _run_terminal(cfg, metrics_file, interval)


def _run_terminal(cfg: Config, metrics_file: Path, interval: float) -> None:
    console = Console()
    with Live(console=console, screen=True, refresh_per_second=1) as live:
        while True:
            rows = _read_metrics(metrics_file)
            size = os.get_terminal_size()
            live.update(_build_layout(cfg, rows, size.columns, size.lines))
            time.sleep(interval)


def _gui_info_text(cfg: Config, rows: list[dict]) -> str:
    t = cfg.training
    lines = [
        cfg.data.experiment_dir.name,
        "",
        f"loss:       {t.loss}",
        f"optimizer:  {t.optimizer}",
        f"epochs:     {t.epochs}",
        f"batch_size: {t.batch_size}",
        f"lr_init:    {t.learning_rate}",
        f"lr_decay:   {t.lr_decay_factor} / {t.lr_decay_every} ep",
    ]
    if t.target_loss is not None:
        lines.append(f"target_loss:{t.target_loss}")

    if rows:
        by_run: dict[str, list[dict]] = {}
        for r in rows:
            by_run.setdefault(r["run_id"], []).append(r)

        for run_rows in by_run.values():
            last = run_rows[-1]
            best = min(run_rows, key=lambda r: float(r["val_loss"]))
            lines += [
                "",
                f"epoch:      {last['epoch']} / {t.epochs}",
                f"val_loss:   {float(last['val_loss']):.6f}",
                f"train_loss: {float(last['train_loss']):.6f}",
                f"best_val:   {float(best['val_loss']):.6f} @ ep {best['epoch']}",
                f"lr:         {last['learning_rate']}",
            ]

    return "\n".join(lines)


def _run_gui(cfg: Config, metrics_file: Path, interval: float) -> None:
    import matplotlib.pyplot as mpl
    import matplotlib.ticker as ticker
    from matplotlib.widgets import RadioButtons

    mpl.ion()
    fig = mpl.figure(figsize=(13, 5))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 3])
    ax_info = fig.add_subplot(gs[0])
    ax_chart = fig.add_subplot(gs[1])

    ax_info.axis("off")
    info_text = ax_info.text(
        0.05, 0.95, "", transform=ax_info.transAxes,
        verticalalignment="top", fontfamily="monospace", fontsize=9,
    )

    # radio buttons in the bottom quarter of the info column
    info_pos = ax_info.get_position()
    ax_radio = fig.add_axes([
        info_pos.x0 + 0.02,
        info_pos.y0,
        info_pos.width * 0.6,
        info_pos.height * 0.15,
    ])
    radio = RadioButtons(ax_radio, ("log", "linear"), active=0)

    def _on_scale(label: str) -> None:
        ax_chart.set_yscale(label)
        ax_chart.relim()
        ax_chart.autoscale_view()
        fig.canvas.draw()

    radio.on_clicked(_on_scale)
    ax_chart.set_yscale("log")

    fig.tight_layout(pad=2.0)

    ax_chart.set_xlabel("epoch")
    ax_chart.set_ylabel("loss")
    ax_chart.grid(True, alpha=0.3)
    ax_chart.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    if cfg.training.target_loss is not None:
        ax_chart.axhline(cfg.training.target_loss, color="red", linestyle=":", linewidth=1, label=f"target ({cfg.training.target_loss})")

    lines: dict[str, mpl.Line2D] = {}

    while mpl.fignum_exists(fig.number):
        rows = _read_metrics(metrics_file)

        info_text.set_text(_gui_info_text(cfg, rows))

        if rows:
            by_run: dict[str, list[dict]] = {}
            for r in rows:
                by_run.setdefault(r["run_id"], []).append(r)

            run_ids = list(by_run.keys())
            for run_id, run_rows in by_run.items():
                epochs = [int(r["epoch"]) for r in run_rows]
                train_losses = [float(r["train_loss"]) for r in run_rows]
                val_losses = [float(r["val_loss"]) for r in run_rows]

                # only prefix with run index when there are multiple runs
                prefix = f"run{run_ids.index(run_id) + 1} " if len(run_ids) > 1 else ""
                train_key = f"{run_id}_train"
                val_key = f"{run_id}_val"

                if train_key not in lines:
                    (lines[train_key],) = ax_chart.plot(epochs, train_losses, label=f"{prefix}train")
                    (lines[val_key],) = ax_chart.plot(epochs, val_losses, label=f"{prefix}val", linestyle="--")
                    ax_chart.legend()
                else:
                    lines[train_key].set_data(epochs, train_losses)
                    lines[val_key].set_data(epochs, val_losses)

            ax_chart.relim()
            ax_chart.autoscale_view()

        fig.canvas.draw()
        fig.canvas.flush_events()
        mpl.pause(interval)
