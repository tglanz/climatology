"""Physical-unit evaluation of prepared test windows on their saved coordinates."""

from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np

from ml.config import load
from ml.data.climatology import diagnostic_for
from ml.data.metadata import DataMetadata
from ml.data.prepared import for_run
from ml.diagnostics.errors import ScoreSummary, profile_relative_l2_values
from ml.inference import load_checkpoint, select_device, prepare_device, predict_windows


@dataclass(frozen=True)
class SampleEvaluation:
    predictions: np.ndarray
    truth: np.ndarray
    metadata: DataMetadata
    rmses: np.ndarray
    relatives: np.ndarray

    @property
    def latitudes(self) -> np.ndarray:
        return self.metadata.grid.latitudes


def run(
    training_dir: Path,
    batch_size: int = 64,
    limit: int | None = None,
    device: str = "auto",
) -> SampleEvaluation:
    if limit is not None and limit < 1:
        raise ValueError("sample limit must be positive")
    training_dir = training_dir.resolve()
    cfg = load(training_dir / "config.toml")
    checkpoint = load_checkpoint(cfg, training_dir)
    with h5py.File(for_run(training_dir) / "test.h5", "r") as handle:
        metadata = DataMetadata.read_hdf5(handle)
        if not checkpoint.normalization.metadata.matches(metadata):
            raise ValueError("prepared test data differ from the saved checkpoint")
        x, truth = handle["x"][:limit], handle["y"][:limit]
    selected = select_device(device)
    prepare_device(checkpoint.model, x.shape[1:], selected)
    predictions = predict_windows(
        checkpoint.model, checkpoint.normalization, x, selected, batch_size
    )
    if truth.shape != predictions.shape or not np.isfinite(truth).all():
        raise ValueError("prepared targets have invalid values or shapes")
    rmses = np.sqrt(np.sum(metadata.grid.weights * (predictions - truth) ** 2, axis=-1))
    relatives = profile_relative_l2_values(predictions, truth, metadata.grid.latitudes)
    return SampleEvaluation(predictions, truth, metadata, rmses, relatives)


def print_metrics(result: SampleEvaluation):
    print("Prepared test windows; physical units; equal weight per window.")
    for index, name in enumerate(result.metadata.y_vars):
        target = diagnostic_for(name)
        rmse = ScoreSummary.from_values(result.rmses[:, index])
        relative = ScoreSummary.from_values(result.relatives[:, index])
        print(
            f"{name}: mean RMSE={rmse.mean} [{target.units}], mean relative L2={relative.mean}; "
            f"included={relative.count}, undefined={relative.undefined}"
        )
