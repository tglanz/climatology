import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ml.config import Config


@dataclass
class Section:
    name: str
    items: list[tuple[str, str]]


@dataclass
class RunSeries:
    run_id: str
    label: str          # empty string when only one run, else "run1", "run2", ...
    epochs: list[int]
    train_losses: list[float]
    val_losses: list[float]


class MonitorState:
    def __init__(self, cfg: Config):
        self._cfg = cfg
        self.title: str = cfg.data.experiment_dir.name
        self.sections: list[Section] = []
        self.series: list[RunSeries] = []
        self.target_loss: float | None = cfg.training.target_loss
        self.spatial_error: np.ndarray | None = None
        self.zonal_mean_history: list[np.ndarray] = []
        self.error_power: np.ndarray | None = None
        self.signal_power: np.ndarray | None = None

    _ZONAL_HISTORY_LEN = 10

    def update(self) -> None:
        rows = _read_metrics(self._cfg.paths.epoch_metrics_file)
        self.title, self.sections = _build_sections(self._cfg, rows)
        self.series = _build_series(rows)
        if self._cfg.paths.metrics_file.exists():
            import h5py
            with h5py.File(self._cfg.paths.metrics_file, "r") as f:
                self.spatial_error = f["spatial_error"][:]
                self.error_power   = f["error_power"][:]
                self.signal_power  = f["signal_power"][:]
                zonal = f["zonal_mean_error"][:]
            if not self.zonal_mean_history or not np.array_equal(zonal, self.zonal_mean_history[-1]):
                self.zonal_mean_history.append(zonal)
                if len(self.zonal_mean_history) > self._ZONAL_HISTORY_LEN:
                    self.zonal_mean_history.pop(0)


def _read_metrics(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _build_sections(cfg: Config, rows: list[dict]) -> tuple[str, list[Section]]:
    t = cfg.training
    last = rows[-1] if rows else None
    val_rows = [r for r in rows if r.get("val_loss")]
    best_row = min(val_rows, key=lambda r: float(r["val_loss"])) if val_rows else None
    epoch_num = int(last["epoch"]) if last else 0
    avg_elapsed = sum(float(r["elapsed_seconds"]) for r in rows) / len(rows) if rows else 0.0

    sections = [
        Section("[Optimizer]", [
            ("optimizer", t.optimizer),
        ]),
        Section("[Epoch]", [
            ("total",        str(t.epochs)),
            ("number",       str(epoch_num) if last else "-"),
            ("progress",     f"{100 * epoch_num / t.epochs:.1f}%" if t.epochs and last else "-"),
            ("avg duration", f"{avg_elapsed:.1f}s" if last else "-"),
        ]),
        Section("[LR]", [
            ("init",  str(t.learning_rate)),
            ("decay", f"{t.lr_decay_factor} / {t.lr_decay_every} ep"),
            ("lr",    last["learning_rate"] if last else str(t.learning_rate)),
        ]),
        Section("[Loss]", [
            ("val",      f"{float(last['val_loss']):.6f}" if last and last.get("val_loss") else "-"),
            ("train",    f"{float(last['train_loss']):.6f}" if last else "-"),
            ("ratio",    f"{float(last['val_loss']) / float(last['train_loss']):.2f}" if last and last.get("val_loss") and float(last['train_loss']) > 0 else "-"),
            ("best_val", f"{float(best_row['val_loss']):.6f} @ ep {best_row['epoch']}" if best_row else "-"),
        ]),
    ]

    return cfg.data.experiment_dir.name, sections


def _build_series(rows: list[dict]) -> list[RunSeries]:
    by_run: dict[str, list[dict]] = {}
    for r in rows:
        by_run.setdefault(r["run_id"], []).append(r)
    run_ids = list(by_run.keys())
    multi = len(run_ids) > 1
    return [
        RunSeries(
            run_id=run_id,
            label=f"run{i + 1}" if multi else "",
            epochs=[int(r["epoch"]) for r in run_rows],
            train_losses=[float(r["train_loss"]) for r in run_rows],
            val_losses=[float(r["val_loss"]) for r in run_rows],
        )
        for i, (run_id, run_rows) in enumerate(by_run.items())
    ]
