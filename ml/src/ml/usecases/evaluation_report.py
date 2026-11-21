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
        lines.extend(
            [
                "",
                "### Does the model use its inputs?",
                "",
                "Positive skill beats the training mean. A variance ratio near zero indicates collapsed configuration predictions.",
                "Correlation measures matching changes across configurations; slope measures their amplitude. These are undefined without variation.",
                "",
                "| Split | Configurations | RMSE | Skill over train mean | Variance ratio | Anomaly correlation | Anomaly slope | Pairing permutation p | Input/target overlap |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for split, row in target.learning["splits"].items():
            values = [
                row["mse"] ** 0.5,
                row["skill_over_train_mean"],
                row["configuration_variance_ratio"],
                row["configuration_anomaly_correlation"],
                row["configuration_anomaly_slope"],
                row["permutation_p"],
                row["input_target_overlap_fraction"],
            ]
            lines.append(
                f"| {split} | {row['configurations']} | "
                + " | ".join(_number(v) for v in values)
                + " |"
            )
        lines.extend(
            [
                "",
                "Pairing permutations exchange complete configuration-mean predictions within each split (199 draws, seed 17). Small p supports correct input/target pairing, not physical causation.",
                "Input/target overlap is the mean fraction of input snapshots inside the target averaging interval. Positive overlap limits a forecasting claim.",
                "",
                "### Paired test comparison",
                "",
                "| Reference | Model skill | Reference MSE minus model MSE | 95% configuration bootstrap interval | Configurations |",
                "|---|---:|---:|---|---:|",
            ]
        )
        for reference_name, row in target.learning["paired_test_skill"].items():
            interval = ", ".join(_number(v) for v in row["ci95"])
            lines.append(
                f"| {reference_name} | {_number(row['skill'])} | {_number(row['mse_improvement'])} | [{interval}] | {row['configurations']} |"
            )
        lines.extend(
            [
                "",
                "Positive MSE improvement favors the model. Bootstrap draws resample configurations, retaining their replicas together (1000 draws, seed 17). Few configurations give unstable intervals.",
                "The short-window mean averages the target field over the same input windows. It can use extra observed quantities, such as wind when the model sees only vorticity; it is a physical averaging reference.",
                "The parameter ridge uses only forcing parameters and training-configuration mean targets (fixed ridge 1e-6). It tests whether field inputs add value beyond a simple parameter map.",
            ]
        )
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
            "learning": target.learning,
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
