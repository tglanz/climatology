"""Completed prepared artifacts and their immutable run references."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

from ml.data.evaluation import SimulationLoadReport, SimulationPrediction
from ml.data.isca_dataset import IscaDataset
from ml.data.metadata import DataMetadata
from ml.data.simulation_data import SimulationOutcome
from ml.data.splits import Splits

FORMAT = "climatology-prepared-v1"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def write_manifest(directory: Path) -> None:
    names = ["train.h5", "val.h5", "test.h5", "splits.json", "preparation.toml"]
    if (directory / "sweep.json").exists():
        names.append("sweep.json")
    payload = {"format": FORMAT, "files": {n: digest(directory / n) for n in names}}
    (directory / "manifest.json").write_text(json.dumps(payload, indent=2) + "\n")


def verify(directory: Path, expected: dict | None = None) -> dict:
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest.get("format") != FORMAT:
        raise ValueError("unsupported prepared manifest; regenerate data")
    required = {"train.h5", "val.h5", "test.h5", "splits.json", "preparation.toml"}
    if not required.issubset(manifest.get("files", {})):
        raise ValueError("incomplete prepared manifest")
    if expected is not None and manifest != expected:
        raise ValueError("prepared manifest differs from the saved run")
    for name, checksum in manifest["files"].items():
        if Path(name).name != name or digest(directory / name) != checksum:
            raise ValueError(f"prepared artifact changed: {name}")
    return manifest


def bind(directory: Path, training_dir: Path) -> None:
    manifest = verify(directory)
    (training_dir / "prepared.json").write_text(
        json.dumps(
            {"directory": str(directory.resolve()), "manifest": manifest}, indent=2
        )
        + "\n"
    )


def for_run(training_dir: Path, override: Path | None = None) -> Path:
    record = json.loads((training_dir / "prepared.json").read_text())
    directory = Path(override or record["directory"])
    verify(directory, record["manifest"])
    return directory


@dataclass(frozen=True)
class PreparedSimulation:
    path: Path
    metadata: DataMetadata
    x: np.ndarray
    truth: np.ndarray
    starts: tuple[int, ...]
    provenance: dict


def iter_simulations(directory: Path, splits: Splits):
    """Read one simulation at a time; paths identify sources without opening them."""
    for name, assigned in (
        ("train", splits.train),
        ("val", splits.validation),
        ("test", splits.test),
    ):
        file = directory / f"{name}.h5"
        IscaDataset(file)
        with h5py.File(file, "r") as handle:
            metadata = DataMetadata.read_hdf5(handle)
            paths = [Path(p) for p in handle["simulation_paths"].asstr()[:]]
            offsets = handle["simulation_offsets"][:]
            provenance = json.loads(handle.attrs["simulation_provenance"])
            if (
                len(offsets) != len(paths) + 1
                or offsets[0] != 0
                or offsets[-1] != len(handle["x"])
                or np.any(np.diff(offsets) <= 0)
                or len(provenance) != len(paths)
                or handle["window_starts"].shape != (len(handle["x"]),)
            ):
                raise ValueError("invalid prepared window ownership")
            excluded = json.loads(handle.attrs["exclusions"])
            accepted = {p.resolve() for p in paths}
            rejected = {Path(p["simulation"]).resolve() for p in excluded}
            if accepted & rejected or accepted | rejected != {
                p.resolve() for p in assigned
            }:
                raise ValueError(
                    "prepared simulation membership differs from assignments"
                )
            for index, path in enumerate(paths):
                a, b = offsets[index : index + 2]
                truth = handle["simulation_targets"][index]
                if not np.isfinite(truth).all() or not np.array_equal(
                    handle["y"][a:b], np.broadcast_to(truth, (b - a, *truth.shape))
                ):
                    raise ValueError(
                        "prepared window targets differ from simulation truth"
                    )
                yield PreparedSimulation(
                    path,
                    metadata,
                    handle["x"][a:b],
                    truth,
                    tuple(int(v) for v in handle["window_starts"][a:b]),
                    provenance[index],
                )


def predict_prepared(directory, splits, checkpoint, device, batch_size):
    from ml.inference import prepare_device, predict_windows

    results, excluded = [], []
    model = None
    for item in iter_simulations(directory, splits):
        if not checkpoint.normalization.metadata.matches(item.metadata):
            raise ValueError("prepared simulation differs from checkpoint metadata")
        if model is None:
            model = prepare_device(checkpoint.model, item.x.shape[1:], device)
        predictions = predict_windows(
            model, checkpoint.normalization, item.x, device, batch_size
        )
        results.append(
            SimulationPrediction(
                item.path, item.metadata, item.truth, predictions.mean(axis=0)
            )
        )
    for split in ("train", "val", "test"):
        with h5py.File(directory / f"{split}.h5", "r") as handle:
            excluded.extend(
                SimulationOutcome(Path(e["simulation"]), None, e["reason"])
                for e in json.loads(handle.attrs["exclusions"])
            )
    if not results:
        raise ValueError("prepared data contain no simulations")
    return SimulationLoadReport(results, excluded)
