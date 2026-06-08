"""
Early stopping criteria for the training loop.

A criterion is anything that, given per-epoch loss information, can vote to
end training. The trainer holds a single CompositeEarlyStopper that wraps
zero or more child criteria; training stops as soon as any child fires.

Note: PyTorch has no built-in early stopping. The mechanism is provided by
higher-level frameworks (Lightning, Ignite, Skorch, Transformers Trainer).
This module implements a small in-house version because this project uses
raw PyTorch.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ml.config import EarlyStoppingConfig


@dataclass
class EarlyStoppingInfo:
    """Snapshot of the information available at the end of an epoch."""

    epoch: int
    train_loss: float
    val_loss: float | None
    best_val_loss: float
    best_val_epoch: int
    learning_rate: float


def _select(monitor: str, info: EarlyStoppingInfo) -> float | None:
    if monitor == "val":
        return info.val_loss
    if monitor == "train":
        return info.train_loss
    raise ValueError(f"unknown monitor: {monitor}")


class EarlyStopping(ABC):
    """Abstract base for early stopping criteria."""

    @abstractmethod
    def should_early_stop(self, info: EarlyStoppingInfo) -> bool:
        """Return True iff training should stop after the current epoch."""

    @abstractmethod
    def reason(self) -> str:
        """Human-readable description, used for logging when the criterion fires."""


class TargetLossStop(EarlyStopping):
    """
    Stop when the monitored loss drops at or below `value`.

    Why this is useful:
        Avoids burning compute once the model has met an a-priori "good
        enough" quality bar set by an external benchmark or downstream
        consumer. Best when the goal is binary (clear a threshold), not
        "as good as possible". Does NOT protect against overfitting or
        plateaus; pair it with PatienceStop when both matter.
    """

    def __init__(self, value: float, monitor: str = "val"):
        assert monitor in ("val", "train"), f"unknown monitor: {monitor}"
        self.value = value
        self.monitor = monitor

    def should_early_stop(self, info: EarlyStoppingInfo) -> bool:
        v = _select(self.monitor, info)
        return v is not None and v <= self.value

    def reason(self) -> str:
        return f"target_loss reached: {self.monitor} <= {self.value}"


class PatienceStop(EarlyStopping):
    """
    Stop when the monitored loss has not improved by at least `min_delta`
    for `patience` consecutive epochs.

    Why this is useful:
        This is the canonical "early stopping" of Prechelt (1998). It
        detects plateaus and overfitting in real time, which is the most
        common cause of wasted training compute. When validation has
        stopped improving but train continues to drop, this is a clear
        overfitting signal and stops the run before compute is spent
        moving train loss further from val. Recommended on by default
        for any run of nontrivial length.
    """

    def __init__(
        self,
        patience: int = 10,
        min_delta: float = 1e-4,
        monitor: str = "val",
    ):
        assert patience > 0, f"patience must be positive, got {patience}"
        assert min_delta >= 0, f"min_delta must be non-negative, got {min_delta}"
        assert monitor in ("val", "train"), f"unknown monitor: {monitor}"
        self.patience = patience
        self.min_delta = min_delta
        self.monitor = monitor
        self._best: float | None = None
        self._epochs_without_improvement = 0

    def should_early_stop(self, info: EarlyStoppingInfo) -> bool:
        v = _select(self.monitor, info)
        if v is None:
            return False
        if self._best is None or v < self._best - self.min_delta:
            self._best = v
            self._epochs_without_improvement = 0
            return False
        self._epochs_without_improvement += 1
        return self._epochs_without_improvement >= self.patience

    def reason(self) -> str:
        return (
            f"no improvement on {self.monitor} for {self.patience} epochs "
            f"(min_delta={self.min_delta})"
        )


class CompositeEarlyStopper(EarlyStopping):
    """
    Composite of one or more EarlyStopping criteria. Stops when any child
    fires. Empty composite never stops; this lets the trainer always hold
    a CompositeEarlyStopper without special-casing the no-criteria case.

    Why this is useful:
        Different criteria address different failure modes (target reached
        vs plateau vs overfit) and are usefully combined. The composite
        keeps the trainer's stopping check uniform: one method call, one
        reason string for logs, no list iteration in client code.
    """

    def __init__(self, stoppers: list[EarlyStopping] | None = None):
        self._stoppers: list[EarlyStopping] = list(stoppers or [])
        self._fired: EarlyStopping | None = None

    def add(self, stopper: EarlyStopping) -> "CompositeEarlyStopper":
        """Append a child stopper. Returns self for chaining."""
        self._stoppers.append(stopper)
        return self

    def __len__(self) -> int:
        return len(self._stoppers)

    def __iter__(self):
        return iter(self._stoppers)

    def should_early_stop(self, info: EarlyStoppingInfo) -> bool:
        # Query every child so each one's internal state advances correctly,
        # even when an earlier child already fires this epoch.
        any_fired = False
        for s in self._stoppers:
            if s.should_early_stop(info):
                if self._fired is None:
                    self._fired = s
                any_fired = True
        return any_fired

    def reason(self) -> str:
        if self._fired is None:
            return "no criterion has fired"
        return self._fired.reason()

    @classmethod
    def from_config(cls, cfg: "EarlyStoppingConfig") -> "CompositeEarlyStopper":
        """
        Build a composite from an EarlyStoppingConfig. Children are added
        only for subsections that are actually configured. The composite
        is always returned (possibly empty) so callers can use it
        unconditionally.
        """
        composite = cls()
        if cfg.target_loss is not None:
            composite.add(
                TargetLossStop(
                    value=cfg.target_loss.value,
                    monitor=cfg.target_loss.monitor,
                )
            )
        if cfg.patience is not None:
            composite.add(
                PatienceStop(
                    patience=cfg.patience.patience,
                    min_delta=cfg.patience.min_delta,
                    monitor=cfg.patience.monitor,
                )
            )
        return composite
