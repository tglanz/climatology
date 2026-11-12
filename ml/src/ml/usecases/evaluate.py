"""Evaluate the saved sample contract, then render current numerical results."""

from collections import defaultdict
import json
import logging
from pathlib import Path

import numpy as np

from ml.config import load as load_config
from ml.data.prepared import for_run, predict_prepared, digest
from ml.data.splits import Splits
from ml.data.sweep_file import SweepFile
from ml.diagnostics.errors import ScoreSummary, profile_relative_l2_values
from ml.inference import load_checkpoint, select_device
from ml.usecases.evaluation_report import FigureArtifact, write_report
from ml.usecases.evaluation_results import build_target_evaluation, TargetEvaluation
from ml.visualization.evaluation import (
    plot_baselines_bar,
    plot_baselines_profiles,
    plot_error_bias,
    plot_error_histogram,
    plot_generalization_param,
    plot_generalization_worst,
    plot_jet_scatter,
    plot_model_vs_variability,
    plot_replicate_variability,
    plot_training_curve,
)

log = logging.getLogger(__name__)


def _relative(case, latitude):
    return float(profile_relative_l2_values(case.prediction, case.truth, latitude))


def _render_target(target: TargetEvaluation, sweep, save):
    name, lat = target.diagnostic.name, target.latitude
    label, units = target.diagnostic.label, target.diagnostic.units

    def emit(figure, filename, caption):
        save(figure, f"{name}/{filename}", caption, name)

    valid_scores = [
        score for score in target.scores if score.relative_l2.mean is not None
    ]
    if valid_scores:
        names = [score.name for score in valid_scores]
        emit(
            plot_baselines_bar(
                names,
                [score.relative_l2.mean for score in valid_scores],
                names.index("model") if "model" in names else -1,
            ),
            "baselines.png",
            "Mean Gaussian-weighted relative L2 on test simulations.",
        )
    tests = target.test_cases
    if tests:
        truths = np.stack([case.truth for case in tests])
        predictions = np.stack([case.prediction for case in tests])
        profiles = {
            p.name: p.profiles.mean(0)
            for p in target.predictors
            if p.profiles is not None
        }
        emit(
            plot_baselines_profiles(lat, truths.mean(0), profiles, label, units),
            "profiles.png",
            "Mean truth and predictor profiles across test simulations.",
        )
        emit(
            plot_error_bias(lat, predictions - truths, units),
            "bias.png",
            "Per-simulation error profiles and mean bias on the test split.",
        )
        errors = profile_relative_l2_values(predictions, truths, lat)
        finite = errors[np.isfinite(errors)]
        if finite.size:
            emit(
                plot_error_histogram(finite),
                "errors.png",
                "Relative L2 distribution across test simulations; zero-reference cases are excluded.",
            )
        if target.diagnostic.variable == "ucomp":
            for quantity, truth_values, predicted_values, unit in (
                (
                    "latitude",
                    lat[np.abs(truths).argmax(-1)],
                    lat[np.abs(predictions).argmax(-1)],
                    "deg",
                ),
                (
                    "amplitude",
                    np.abs(truths).max(-1),
                    np.abs(predictions).max(-1),
                    "m/s",
                ),
            ):
                emit(
                    plot_jet_scatter(
                        truth_values,
                        predicted_values,
                        f"truth [{unit}]",
                        f"prediction [{unit}]",
                        f"Strongest absolute zonal-wind extremum: {quantity}",
                    ),
                    f"peak_{quantity}.png",
                    f"Strongest absolute zonal-wind extremum {quantity} on test simulations.",
                )

    rows = [
        row
        for row in target.variability
        if row.deviation.mean is not None and row.model_error.mean is not None
    ]
    if rows:
        emit(
            plot_replicate_variability(
                [r.code for r in rows],
                [r.deviation.mean for r in rows],
                [r.model_error.mean for r in rows],
            ),
            "variability.png",
            "Mean relative deviation from each configuration's replica mean versus model error.",
        )
        emit(
            plot_model_vs_variability(
                [r.code for r in rows],
                [r.deviation.mean for r in rows],
                [r.model_error.mean for r in rows],
                [r.split for r in rows],
            ),
            "model_vs_variability.png",
            "Descriptive replica deviation versus model error, colored by split; the diagonal is equality.",
        )

    by_code = defaultdict(list)
    for case in target.cases:
        by_code[case.code].append(case)
    code_errors = {
        code: ScoreSummary.from_values([_relative(case, lat) for case in group]).mean
        for code, group in by_code.items()
    }
    if sweep is not None:
        for parameter in sweep.varying_keys():
            values, scores, splits = [], [], []
            for code, group in sorted(by_code.items()):
                params = sweep.params_for(code)
                if (
                    params is not None
                    and parameter in params
                    and code_errors[code] is not None
                ):
                    values.append(float(params[parameter]))
                    scores.append(code_errors[code])
                    splits.append(group[0].split)
            if values:
                emit(
                    plot_generalization_param(parameter, values, scores, splits),
                    f"generalization_{parameter}.png",
                    f"Mean per-simulation relative L2 by {parameter}, colored by split.",
                )
    worst = sorted(
        [(code, error) for code, error in code_errors.items() if error is not None],
        key=lambda item: (-item[1], item[0]),
    )[:6]
    if worst:
        cases = [
            (
                code,
                np.mean([c.truth for c in by_code[code]], 0),
                np.mean([c.prediction for c in by_code[code]], 0),
                error,
            )
            for code, error in worst
        ]
        emit(
            plot_generalization_worst(lat, cases, label, units),
            "worst.png",
            "Worst configurations across loaded splits. Curves average profiles; titles average simulation errors.",
        )


def run(
    training_dir: Path,
    n_workers: int = 8,
    batch_size: int = 64,
    device: str = "auto",
    prepared_dir: Path | None = None,
):
    if batch_size < 1 or n_workers < 0:
        raise ValueError("invalid evaluation batch size or worker count")
    training_dir = training_dir.resolve()
    cfg = load_config(training_dir / "config.toml")
    checkpoint = load_checkpoint(cfg, training_dir)
    splits = Splits.load(training_dir / "splits.json")
    splits.validate()
    directory = for_run(training_dir, prepared_dir)
    norm = checkpoint.normalization
    loaded = predict_prepared(
        directory, splits, checkpoint, select_device(device), batch_size
    )
    sweep_path = directory / "sweep.json"
    sweep = SweepFile(sweep_path) if sweep_path.exists() else None
    targets = [
        build_target_evaluation(loaded.results, splits, index, sweep)
        for index in range(len(norm.metadata.y_vars))
    ]
    output = training_dir / "evaluation"
    artifacts = []

    def save(figure, filename, caption, target=None):
        import matplotlib.pyplot as plt

        path = output / "figures" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            figure.savefig(path, dpi=150)
        finally:
            plt.close(figure)
        artifacts.append(FigureArtifact(path, caption, target))

    try:
        csv_path = training_dir / cfg.paths.epoch_metrics_file.relative_to(
            cfg.paths.training_dir
        )
    except ValueError:
        csv_path = cfg.paths.epoch_metrics_file
    if csv_path.exists():
        info_path = training_dir / "training.json"
        run_id = (
            json.loads(info_path.read_text())["run_id"] if info_path.exists() else None
        )
        try:
            figure = plot_training_curve(csv_path, run_id)
        except ValueError as exc:
            log.warning("training curve unavailable: %s", exc)
        else:
            save(
                figure,
                "training.png",
                f"{cfg.training.loss} on normalized targets, averaged by sample count.",
            )
    for target in targets:
        _render_target(target, sweep, save)
    write_report(output, artifacts, targets, loaded, splits)
    np.savez_compressed(
        output / "profiles.npz",
        simulation_paths=np.array([str(r.sim_dir) for r in loaded.results]),
        target_names=np.array(norm.metadata.y_vars),
        latitudes=norm.metadata.grid.latitudes,
        truth=np.stack([r.truth_profile for r in loaded.results]),
        predictions=np.stack([r.pred_profile for r in loaded.results]),
    )
    (output / "inputs.json").write_text(
        json.dumps(
            {
                "prepared": json.loads((training_dir / "prepared.json").read_text()),
                "parameters_sha256": digest(training_dir / "parameters.pt"),
                "normalization_sha256": digest(training_dir / "normalization.pt"),
                "config_sha256": digest(training_dir / "config.toml"),
                "device": str(select_device(device)),
                "batch_size": batch_size,
            },
            indent=2,
        )
        + "\n"
    )
    log.info("evaluation complete: %s", output)
    return targets
