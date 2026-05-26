"""
Per-run training metadata persisted as JSON.

`TrainingInfo` is a snapshot of everything a future reader needs to
understand a training run without re-deriving it from the original config:
data splits, model architecture, optimizer/scheduler/early-stopping
settings, environment (device, library versions, git SHA), and the file
paths of every artifact produced during the run. It is written once at
the start of `Trainer.fit` and overwritten once at the end with the final
summary fields.
"""

from __future__ import annotations

import csv
import json
import platform
import re
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import torch

    from ml.config import Config


@dataclass
class TrainingInfo:
    """Run metadata snapshot. Persisted as `training.json` in the run dir."""

    run_id: str
    start_time: str
    end_time: str | None = None

    paths: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)
    data: dict[str, Any] = field(default_factory=dict)
    model: dict[str, Any] = field(default_factory=dict)
    training: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)

    # populated by finalize() at end of run
    total_epochs: int | None = None
    best_val_loss: float | None = None
    best_val_epoch: int | None = None
    stopped_early: bool | None = None

    @classmethod
    def collect(
        cls,
        cfg: "Config",
        run_id: str,
        model: "torch.nn.Module",
        device: "torch.device",
    ) -> "TrainingInfo":
        return cls(
            run_id=run_id,
            start_time=_now_iso(),
            paths=_collect_paths(cfg),
            artifacts=_collect_artifacts(cfg),
            data=_collect_data(cfg),
            model=_collect_model(cfg, model),
            training=_collect_training(cfg),
            environment=_collect_environment(device),
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2, default=_json_default)

    def finalize(
        self,
        total_epochs: int,
        best_val_loss: float,
        best_val_epoch: int,
        stopped_early: bool,
    ) -> None:
        self.end_time = _now_iso()
        self.total_epochs = total_epochs
        self.best_val_loss = (
            best_val_loss if best_val_loss < float("inf") else None
        )
        self.best_val_epoch = best_val_epoch if best_val_epoch > 0 else None
        self.stopped_early = stopped_early


def rotate_training_dir(training_dir: Path) -> Path | None:
    """
    If `training_dir` exists, rename it to `<name>-<N>` where N is one more
    than the highest existing sibling matching the same prefix. Returns the
    new path of the rotated directory, or None if there was nothing to
    rotate.

    Used so that `<experiment>/training` always refers to the most recent
    run, with prior runs preserved as `training-1`, `training-2`, etc.
    Custom-named siblings (e.g. `training-300-53`) are ignored by the
    matcher and stay where they are.
    """
    if not training_dir.exists():
        return None
    pattern = re.compile(rf"^{re.escape(training_dir.name)}-(\d+)$")
    nums: list[int] = []
    for child in training_dir.parent.iterdir():
        if not child.is_dir():
            continue
        m = pattern.match(child.name)
        if m:
            nums.append(int(m.group(1)))
    n = max(nums) + 1 if nums else 1
    rotated = training_dir.parent / f"{training_dir.name}-{n}"
    training_dir.rename(rotated)
    return rotated


# --- internals ---


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_default(obj: Any) -> Any:
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"unserializable type: {type(obj).__name__}")


def _rel_to(target: Path, base: Path) -> str:
    """
    Return target as a string relative to base, walking up the directory
    tree as needed (e.g. siblings render as `../sibling/file`). Falls back
    to an absolute path on different drives or other relative_to failures.
    """
    try:
        return str(target.relative_to(base, walk_up=True))
    except ValueError:
        return str(target.resolve())


def _collect_paths(cfg: "Config") -> dict[str, Any]:
    p = cfg.paths
    return {
        "experiment_dir": str(cfg.data.experiment_dir),
        "training_dir": str(p.training_dir),
        "checkpoint_dir": str(p.checkpoint_dir),
        "preprocessed_dir": str(p.preprocessed_dir),
    }


def _collect_artifacts(cfg: "Config") -> dict[str, Any]:
    """Map each artifact name to its path relative to training_dir when possible."""
    p = cfg.paths
    base = p.training_dir
    candidates = {
        "config":         base / "config.toml",
        "parameters":     p.checkpoint_dir / "parameters.pt",
        "normalization":  p.checkpoint_dir / "normalization.pt",
        "epoch_metrics":  p.epoch_metrics_file,
        "runs":           p.runs_file,
        "metrics":        p.metrics_file,
        "training_info":  p.training_info_file,
        "splits_manifest": p.preprocessed_dir / "splits.json",
    }
    return {name: _rel_to(path, base) for name, path in candidates.items()}


def _collect_data(cfg: "Config") -> dict[str, Any]:
    import h5py

    d = cfg.data
    info: dict[str, Any] = {
        "x_vars": list(d.x_vars),
        "y_vars": list(d.y_vars),
        "split": d.split,
        "windows": {
            "input_length":       d.windows.input_length,
            "spinup_timesteps":   d.windows.spinup_timesteps,
            "anchor":             d.windows.anchor,
            "mode":               d.windows.mode,
            "max_per_simulation": d.windows.max_per_simulation,
        },
        "splits": {},
    }

    manifest_path = cfg.paths.preprocessed_dir / "splits.json"
    if not manifest_path.exists():
        return info

    with open(manifest_path) as f:
        manifest = json.load(f)

    for split_name, sim_dirs in manifest.items():
        h5_path = cfg.paths.preprocessed_dir / f"{split_name}.h5"
        n_pairs = None
        if h5_path.exists():
            with h5py.File(h5_path, "r") as hf:
                n_pairs = int(hf["x"].shape[0])
        info["splits"][split_name] = {
            "n_simulations": len(sim_dirs),
            "n_pairs": n_pairs,
        }
    return info


def _collect_model(cfg: "Config", model: "torch.nn.Module") -> dict[str, Any]:
    sub = cfg.model.active_sub_config()
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return {
        "architecture": cfg.model.architecture,
        "n_modes": list(sub.n_modes),
        "hidden_channels": sub.hidden_channels,
        "n_layers": sub.n_layers,
        "in_channels": sub.in_channels,
        "out_channels": sub.out_channels,
        "total_params": total,
        "trainable_params": trainable,
    }


def _collect_training(cfg: "Config") -> dict[str, Any]:
    t = cfg.training
    return {
        "epochs": t.epochs,
        "batch_size": t.batch_size,
        "learning_rate": t.learning_rate,
        "loss": t.loss,
        "optimizer": t.optimizer,
        "grad_clip": t.grad_clip,
        "regularization": _serialize_regularization(t.regularization),
        "scheduler": _serialize_scheduler(t.scheduler),
        "early_stopping": _serialize_early_stopping(t.early_stopping),
    }


def _serialize_regularization(r) -> dict[str, Any]:
    return {"weight_decay": r.weight_decay, "dropout": r.dropout}


def _serialize_scheduler(s) -> dict[str, Any]:
    out: dict[str, Any] = {"kind": s.kind}
    if s.kind == "step":
        out["step"] = asdict(s.step)
    elif s.kind == "cosine":
        out["cosine"] = asdict(s.cosine)
    elif s.kind == "plateau":
        out["plateau"] = asdict(s.plateau)
    return out


def _serialize_early_stopping(es) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if es.target_loss is not None:
        out["target_loss"] = asdict(es.target_loss)
    if es.patience is not None:
        out["patience"] = asdict(es.patience)
    return out


def _collect_environment(device: "torch.device") -> dict[str, Any]:
    import torch

    return {
        "device": str(device),
        "torch_version": torch.__version__,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "git_sha": _git_sha(),
    }


def _git_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=2,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


# --- summaries (read-side) ---


@dataclass
class TrainingSummary:
    """One row per past training run, used by `ml util summarize-trainings`."""

    name: str
    path: Path
    start_time: str | None = None
    end_time: str | None = None
    total_epochs: int | None = None
    best_val_loss: float | None = None
    best_val_epoch: int | None = None
    final_train_loss: float | None = None
    final_val_loss: float | None = None
    stopped_early: bool | None = None
    loss_kind: str | None = None
    optimizer: str | None = None
    scheduler: str | None = None
    n_params: int | None = None

    @property
    def duration_seconds(self) -> float | None:
        if not self.start_time or not self.end_time:
            return None
        try:
            t0 = datetime.fromisoformat(self.start_time)
            t1 = datetime.fromisoformat(self.end_time)
            return (t1 - t0).total_seconds()
        except (ValueError, TypeError):
            return None


def load_summary(training_dir: Path) -> TrainingSummary:
    """
    Best-effort summary load.

    Pulls structured info from training.json when present; otherwise
    falls back to runs.csv (last row) and epoch-metrics.csv. Designed
    so legacy run directories without training.json still produce a
    useful row.
    """
    s = TrainingSummary(name=training_dir.name, path=training_dir)
    _augment_from_training_json(s, training_dir / "training.json")
    _augment_from_runs_csv(s, training_dir / "runs.csv")
    _augment_from_epoch_metrics(s, training_dir / "epoch-metrics.csv")
    return s


def list_training_summaries(
    experiment_dir: Path, training_dir_name: str = "training"
) -> list[TrainingSummary]:
    """
    Find all training directories under `experiment_dir` (matching either
    `<training_dir_name>` or `<training_dir_name>-*`) and return their
    summaries sorted newest-first by start_time, falling back to dir
    mtime.
    """
    if not experiment_dir.exists():
        return []
    dirs: list[Path] = []
    for child in experiment_dir.iterdir():
        if not child.is_dir():
            continue
        if child.name == training_dir_name or child.name.startswith(
            f"{training_dir_name}-"
        ):
            dirs.append(child)

    summaries = [load_summary(d) for d in dirs]
    summaries.sort(key=_summary_sort_key, reverse=True)
    return summaries


# --- internals: summary loading ---


def _augment_from_training_json(s: TrainingSummary, path: Path) -> None:
    if not path.exists():
        return
    try:
        with open(path) as f:
            info = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    s.start_time = info.get("start_time")
    s.end_time = info.get("end_time")
    s.total_epochs = info.get("total_epochs")
    s.best_val_loss = info.get("best_val_loss")
    s.best_val_epoch = info.get("best_val_epoch")
    s.stopped_early = info.get("stopped_early")
    training = info.get("training") or {}
    s.loss_kind = training.get("loss")
    s.optimizer = training.get("optimizer")
    sched = training.get("scheduler") or {}
    s.scheduler = sched.get("kind")
    model = info.get("model") or {}
    s.n_params = model.get("total_params")


def _augment_from_runs_csv(s: TrainingSummary, path: Path) -> None:
    if not path.exists():
        return
    try:
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError:
        return
    if not rows:
        return
    last = rows[-1]
    if s.start_time is None:
        s.start_time = last.get("start_time") or None
    if s.end_time is None:
        s.end_time = last.get("end_time") or None
    if s.total_epochs is None:
        s.total_epochs = _maybe_int(last.get("total_epochs"))
    if s.best_val_loss is None:
        s.best_val_loss = _maybe_float(last.get("best_val_loss"))
    if s.best_val_epoch is None:
        s.best_val_epoch = _maybe_int(last.get("best_val_epoch"))
    if s.stopped_early is None:
        raw = last.get("stopped_early")
        if raw in ("True", "False"):
            s.stopped_early = raw == "True"


def _augment_from_epoch_metrics(s: TrainingSummary, path: Path) -> None:
    if not path.exists():
        return
    try:
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError:
        return
    if not rows:
        return
    last = rows[-1]
    s.final_train_loss = _maybe_float(last.get("train_loss"))
    s.final_val_loss = _maybe_float(last.get("val_loss"))
    if s.start_time is None:
        s.start_time = rows[0].get("timestamp") or None
    if s.end_time is None:
        s.end_time = last.get("timestamp") or None
    if s.total_epochs is None:
        s.total_epochs = _maybe_int(last.get("epoch"))
    if s.best_val_loss is None:
        best_row = None
        for r in rows:
            v = _maybe_float(r.get("val_loss"))
            if v is None:
                continue
            if best_row is None or v < _maybe_float(best_row.get("val_loss")):
                best_row = r
        if best_row is not None:
            s.best_val_loss = _maybe_float(best_row.get("val_loss"))
            s.best_val_epoch = _maybe_int(best_row.get("epoch"))


def _summary_sort_key(s: TrainingSummary) -> float:
    if s.start_time:
        try:
            return datetime.fromisoformat(s.start_time).timestamp()
        except (ValueError, TypeError):
            pass
    try:
        return s.path.stat().st_mtime
    except OSError:
        return 0.0


def _maybe_int(v) -> int | None:
    if v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _maybe_float(v) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
