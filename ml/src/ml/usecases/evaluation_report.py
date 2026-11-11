"""Write numerical tables and only the figures produced by the current invocation."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from ml.data.evaluation import SimulationLoadReport
from ml.data.splits import Splits
from ml.usecases.evaluation_results import TargetEvaluation


@dataclass(frozen=True)
class FigureArtifact:
    path: Path
    caption: str
    target: str | None = None


def _number(value: float | None) -> str:
    return "unavailable" if value is None else f"{value:.6g}"


def write_report(
    output: Path,
    figures: list[FigureArtifact],
    targets: list[TargetEvaluation],
    loaded: SimulationLoadReport,
    splits: Splits,
) -> None:
    lines = [
        "# Evaluation report",
        "",
        "Predictions are in physical target units. Each simulation prediction is the mean of its window predictions.",
        "Relative L2 excludes zero-reference cases; tables report the included and undefined counts.",
        "",
        "## Split coverage",
        "",
        "| Split | Assigned simulations | Loaded simulations |",
        "|---|---:|---:|",
    ]
    for name, paths in (
        ("train", splits.train),
        ("val", splits.validation),
        ("test", splits.test),
    ):
        path_set = {p.resolve() for p in paths}
        lines.append(
            f"| {name} | {len(paths)} | {sum(sr.sim_dir in path_set for sr in loaded.results)} |"
        )
    if loaded.excluded:
        lines.extend(
            ["", "### Excluded simulations", "", "| Simulation | Reason |", "|---|---|"]
        )
        lines.extend(
            f"| {outcome.sim_dir.name} | {outcome.reason.replace('|','/')} |"
            for outcome in loaded.excluded
        )
    lines.extend(
        [
            "",
            "## Training",
            "",
            "Training curves show the configured objective on normalized targets.",
        ]
    )
    for artifact in figures:
        if artifact.target is None:
            lines.extend(
                [
                    "",
                    f"![{artifact.caption}]({artifact.path.relative_to(output).as_posix()})",
                    "",
                ]
            )
    records = {}
    for target in targets:
        name = target.diagnostic.name
        lines.extend(
            [
                "",
                f"## {name}",
                "",
                f"Quantity: {target.diagnostic.label}; units: {target.diagnostic.units}.",
                "",
                "### Test simulations",
                "",
                "| Predictor | Mean relative L2 | Included | Undefined | Mean RMSE | Availability |",
                "|---|---:|---:|---:|---:|---|",
            ]
        )
        for score in target.scores:
            lines.append(
                f"| {score.name} | {_number(score.relative_l2.mean)} | {score.relative_l2.count} | "
                f"{score.relative_l2.undefined} | {_number(score.rmse.mean)} | {score.unavailable_reason or 'available'} |"
            )
        if not target.test_cases:
            lines.extend(["", "No test simulations loaded."])
        if target.nearest:
            lines.extend(
                [
                    "",
                    "### Nearest training configurations",
                    "",
                    "| Test code | Training code | Parameter distance |",
                    "|---|---|---:|",
                ]
            )
            unique = {match.test_code: match for match in target.nearest}
            lines.extend(
                f"| {match.test_code} | {match.train_code} | {match.distance:.6g} |"
                for match in unique.values()
            )
        lines.extend(
            [
                "",
                "### Replicate variability",
                "",
                "This is mean relative deviation from the finite replica mean. It is neither a standard deviation nor an irreducible-error bound.",
                "A single replica cannot estimate variability. Undefined ratios are excluded and counted.",
                "",
                "| Code | Split | Replicas | Mean relative deviation | Included | Undefined |",
                "|---|---|---:|---:|---:|---:|",
            ]
        )
        for row in target.variability:
            lines.append(
                f"| {row.code} | {row.split} | {row.replicas} | {_number(row.deviation.mean)} | {row.deviation.count} | {row.deviation.undefined} |"
            )
        for artifact in figures:
            if artifact.target == name:
                lines.extend(
                    [
                        "",
                        f"![{artifact.caption}]({artifact.path.relative_to(output).as_posix()})",
                        "",
                    ]
                )
        records[name] = {
            "units": target.diagnostic.units,
            "aggregation": "mean window prediction per simulation, then mean simulation score",
            "scores": [asdict(score) for score in target.scores],
            "replicate_variability": [asdict(row) for row in target.variability],
            "nearest_configurations": [asdict(match) for match in target.nearest],
        }
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.md").write_text("\n".join(lines) + "\n")
    payload = {
        "targets": records,
        "excluded": [
            {"simulation": str(o.sim_dir), "reason": o.reason} for o in loaded.excluded
        ],
        "figures": [str(f.path.relative_to(output)) for f in figures],
    }
    (output / "scores.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n"
    )
