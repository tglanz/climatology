import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ml.config import Config
from ml.data.climatology import is_climatology_var


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
        self.target_loss: float | None = (
            cfg.training.early_stopping.target_loss.value
            if cfg.training.early_stopping.target_loss is not None
            else None
        )
        self.is_climatology: bool = all(is_climatology_var(v) for v in cfg.data.y_vars)
        self.spatial_error: np.ndarray | None = None
        # step mode
        self.zonal_mean_history: list[np.ndarray] = []
        self.error_power: np.ndarray | None = None
        self.signal_power: np.ndarray | None = None
        # climatology mode
        self.profile_pred_history: list[np.ndarray] = []
        self.profile_pred_std: np.ndarray | None = None
        self.profile_truth: np.ndarray | None = None

    _ZONAL_HISTORY_LEN = 10
    _PROFILE_HISTORY_LEN = 10

    def update(self) -> None:
        rows = _read_metrics(self._cfg.paths.epoch_metrics_file)
        self.title, self.sections = _build_sections(self._cfg, rows)
        self.series = _build_series(rows)
        if self._cfg.paths.metrics_file.exists():
            import h5py
            with h5py.File(self._cfg.paths.metrics_file, "r") as f:
                self.spatial_error = f["spatial_error"][:]
                self.error_power  = f["error_power"][:] if "error_power" in f else None
                self.signal_power = f["signal_power"][:] if "signal_power" in f else None
                zonal        = f["zonal_mean_error"][:] if "zonal_mean_error" in f else None
                profile_pred     = f["profile_pred"][:]     if "profile_pred"     in f else None
                profile_pred_std = f["profile_pred_std"][:] if "profile_pred_std" in f else None
                profile_truth    = f["profile_truth"][:]    if "profile_truth"    in f else None
            if zonal is not None:
                if not self.zonal_mean_history or not np.array_equal(zonal, self.zonal_mean_history[-1]):
                    self.zonal_mean_history.append(zonal)
                    if len(self.zonal_mean_history) > self._ZONAL_HISTORY_LEN:
                        self.zonal_mean_history.pop(0)
            if profile_pred is not None:
                if not self.profile_pred_history or not np.array_equal(profile_pred, self.profile_pred_history[-1]):
                    self.profile_pred_history.append(profile_pred)
                    if len(self.profile_pred_history) > self._PROFILE_HISTORY_LEN:
                        self.profile_pred_history.pop(0)
            if profile_pred_std is not None:
                self.profile_pred_std = profile_pred_std
            if profile_truth is not None:
                self.profile_truth = profile_truth


def _read_metrics(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _early_stopping_items(t) -> list[tuple[str, str]]:
    es = t.early_stopping
    items: list[tuple[str, str]] = []
    if es.target_loss is not None:
        items.append(
            ("target_loss", f"{es.target_loss.value} ({es.target_loss.monitor})")
        )
    if es.patience is not None:
        p = es.patience
        items.append(
            (
                "patience",
                f"{p.patience} ep, min_delta={p.min_delta} ({p.monitor})",
            )
        )
    if not items:
        items.append(("none", "-"))
    return items


def _scheduler_items(t) -> list[tuple[str, str]]:
    s = t.scheduler
    items: list[tuple[str, str]] = [("kind", s.kind)]
    if s.kind == "step":
        items.append(("step_size", str(s.step.step_size)))
        items.append(("gamma",     str(s.step.gamma)))
    elif s.kind == "cosine":
        items.append(("t_max",   str(s.cosine.t_max)))
        items.append(("eta_min", str(s.cosine.eta_min)))
    elif s.kind == "plateau":
        items.append(("patience",  str(s.plateau.patience)))
        items.append(("factor",    str(s.plateau.factor)))
        items.append(("threshold", str(s.plateau.threshold)))
        items.append(("eta_min",   str(s.plateau.eta_min)))
    return items


def _build_sections(cfg: Config, rows: list[dict]) -> tuple[str, list[Section]]:
    t = cfg.training
    last = rows[-1] if rows else None
    val_rows = [r for r in rows if r.get("val_loss")]
    best_row = min(val_rows, key=lambda r: float(r["val_loss"])) if val_rows else None
    epoch_num = int(last["epoch"]) if last else 0
    avg_elapsed = sum(float(r["elapsed_seconds"]) for r in rows) / len(rows) if rows else 0.0

    optimizer_items = [("optimizer", t.optimizer)]
    if t.optimizer == "adamw" and t.regularization.weight_decay is not None:
        optimizer_items.append(("weight_decay", str(t.regularization.weight_decay)))
    if t.regularization.dropout is not None:
        optimizer_items.append(("dropout", str(t.regularization.dropout)))
    if t.grad_clip is not None:
        optimizer_items.append(("grad_clip", str(t.grad_clip)))

    lr_items: list[tuple[str, str]] = [
        ("init", str(t.learning_rate)),
        ("lr",   last["learning_rate"] if last else str(t.learning_rate)),
    ]
    lr_items.extend(_scheduler_items(t))

    sections = [
        Section("[Optimizer]", optimizer_items),
        Section("[Epoch]", [
            ("total",        str(t.epochs)),
            ("number",       str(epoch_num) if last else "-"),
            ("progress",     f"{100 * epoch_num / t.epochs:.1f}%" if t.epochs and last else "-"),
            ("avg duration", f"{avg_elapsed:.1f}s" if last else "-"),
        ]),
        Section("[LR]", lr_items),
        Section("[Loss]", [
            ("kind",     t.loss),
            ("val",      f"{float(last['val_loss']):.6f}" if last and last.get("val_loss") else "-"),
            ("train",    f"{float(last['train_loss']):.6f}" if last else "-"),
            ("ratio",    f"{float(last['val_loss']) / float(last['train_loss']):.2f}" if last and last.get("val_loss") and float(last['train_loss']) > 0 else "-"),
            ("best_val", f"{float(best_row['val_loss']):.6f} @ ep {best_row['epoch']}" if best_row else "-"),
        ]),
        Section("[Early Stopping]", _early_stopping_items(t)),
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
