"""Evaluation data models and calculations, independent of plotting and file output."""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ml.data.climatology import TargetDiagnostic, diagnostic_for
from ml.data.simulation_data import SimulationSamples
from ml.data.evaluation import SimulationPrediction
from ml.data.splits import Splits
from ml.data.sweep_file import SweepFile
from ml.diagnostics.errors import ScoreSummary, profile_relative_l2_values, profile_rmse


@dataclass(frozen=True)
class ProfileCase:
    sim_dir: Path
    code: str
    split: str
    truth: np.ndarray
    prediction: np.ndarray
    window_predictions: np.ndarray | None = None
    window_baselines: np.ndarray | None = None
    target_overlap: float | None = None


@dataclass(frozen=True)
class Predictor:
    name: str
    profiles: np.ndarray | None
    unavailable_reason: str = ""


@dataclass(frozen=True)
class PredictorScore:
    name: str
    relative_l2: ScoreSummary
    rmse: ScoreSummary
    unavailable_reason: str = ""


@dataclass(frozen=True)
class NearestMatch:
    test_code: str
    train_code: str
    distance: float


@dataclass(frozen=True)
class ReplicateVariability:
    code: str
    replicas: int
    split: str
    deviation: ScoreSummary
    model_error: ScoreSummary


@dataclass
class TargetEvaluation:
    diagnostic: TargetDiagnostic
    latitude: np.ndarray
    cases: list[ProfileCase]
    predictors: list[Predictor] = field(default_factory=list)
    scores: list[PredictorScore] = field(default_factory=list)
    nearest: list[NearestMatch] = field(default_factory=list)
    variability: list[ReplicateVariability] = field(default_factory=list)
    learning: dict = field(default_factory=dict)

    @property
    def test_cases(self) -> list[ProfileCase]:
        return [case for case in self.cases if case.split == "test"]


def _nearest_profiles(
    train: list[ProfileCase], tests: list[ProfileCase], sweep: SweepFile | None
):
    if not train:
        return (
            Predictor("nearest configuration", None, "No training simulations loaded"),
            [],
        )
    if sweep is None:
        return Predictor("nearest configuration", None, "No parameter metadata"), []
    codes = sorted({case.code for case in train})
    keys = sweep.varying_keys()
    if not keys:
        return Predictor("nearest configuration", None, "No varying parameters"), []
    all_codes = codes + [case.code for case in tests]
    if any(
        sweep.params_for(code) is None
        or any(key not in sweep.params_for(code) for key in keys)
        for code in all_codes
    ):
        return (
            Predictor("nearest configuration", None, "Incomplete parameter metadata"),
            [],
        )
    matrix = np.array(
        [[sweep.params_for(code)[key] for key in keys] for code in codes], dtype=float
    )
    if not np.isfinite(matrix).all():
        return (
            Predictor("nearest configuration", None, "Nonfinite training parameters"),
            [],
        )
    ranges = np.ptp(matrix, axis=0)
    ranges[ranges == 0] = 1
    profiles, matches = [], []
    for case in tests:
        vector = np.array(
            [sweep.params_for(case.code)[key] for key in keys], dtype=float
        )
        if not np.isfinite(vector).all():
            return (
                Predictor("nearest configuration", None, "Nonfinite test parameters"),
                [],
            )
        distances = np.linalg.norm((matrix - vector) / ranges, axis=1)
        index = int(np.argmin(distances))
        code = codes[index]
        profiles.append(
            np.mean([case.truth for case in train if case.code == code], axis=0)
        )
        matches.append(NearestMatch(case.code, code, float(distances[index])))
    return Predictor("nearest configuration", np.stack(profiles)), matches


def _parameter_profiles(train, tests, sweep):
    """Fixed ridge regression: fit only training-configuration mean targets."""
    if sweep is None or len({c.code for c in train}) < 2:
        return Predictor(
            "parameter ridge",
            None,
            "Need parameter metadata and at least two training configurations",
        )
    keys = sweep.varying_keys()
    codes = sorted({c.code for c in train})
    if not keys or any(
        sweep.params_for(c) is None or any(k not in sweep.params_for(c) for k in keys)
        for c in codes + [c.code for c in tests]
    ):
        return Predictor(
            "parameter ridge", None, "Incomplete or constant parameter metadata"
        )
    x = np.array([[sweep.params_for(c)[k] for k in keys] for c in codes], dtype=float)
    query = np.array(
        [[sweep.params_for(c.code)[k] for k in keys] for c in tests], dtype=float
    )
    if not np.isfinite(x).all() or not np.isfinite(query).all():
        return Predictor("parameter ridge", None, "Nonfinite parameter metadata")
    mean, scale = x.mean(0), x.std(0)
    scale[scale == 0] = 1
    design = np.column_stack((np.ones(len(x)), (x - mean) / scale))
    query = np.column_stack((np.ones(len(query)), (query - mean) / scale))
    truth = np.stack(
        [np.mean([c.truth for c in train if c.code == code], axis=0) for code in codes]
    )
    penalty = np.eye(design.shape[1]) * 1e-6
    penalty[0, 0] = 0
    coefficients = np.linalg.solve(design.T @ design + penalty, design.T @ truth)
    return Predictor("parameter ridge", query @ coefficients)


def baseline_predictions(cases: list[ProfileCase], sweep: SweepFile | None):
    """Training-derived predictions depend only on train targets and test parameters."""
    train = [case for case in cases if case.split == "train"]
    tests = [case for case in cases if case.split == "test"]
    if not tests:
        return [], []
    shape = (len(tests), len(tests[0].truth))
    mean = (
        Predictor(
            "train mean",
            np.broadcast_to(
                np.mean([case.truth for case in train], axis=0), shape
            ).copy(),
        )
        if train
        else Predictor("train mean", None, "No training simulations loaded")
    )
    nearest, matches = _nearest_profiles(train, tests, sweep)
    return [
        Predictor("zero", np.zeros(shape)),
        mean,
        nearest,
        _parameter_profiles(train, tests, sweep),
        (
            Predictor(
                "short-window mean",
                np.stack([c.window_baselines.mean(0) for c in tests]),
            )
            if all(c.window_baselines is not None for c in tests)
            else Predictor(
                "short-window mean",
                None,
                "Prepared data lack window averaging references; prepare again",
            )
        ),
        Predictor("model", np.stack([case.prediction for case in tests])),
    ], matches


def score_predictor(
    predictor: Predictor, tests: list[ProfileCase], latitude: np.ndarray
) -> PredictorScore:
    if predictor.profiles is None:
        return PredictorScore(
            predictor.name,
            ScoreSummary(None, 0, 0),
            ScoreSummary(None, 0, 0),
            predictor.unavailable_reason,
        )
    truth = np.stack([case.truth for case in tests])
    if predictor.profiles.shape != truth.shape:
        raise ValueError("baseline prediction shape differs from test profiles")
    relative = profile_relative_l2_values(predictor.profiles, truth, latitude)
    rmse = [
        profile_rmse(p, t, latitude)
        for p, t in zip(predictor.profiles, truth, strict=True)
    ]
    return PredictorScore(
        predictor.name,
        ScoreSummary.from_values(relative),
        ScoreSummary.from_values(rmse),
    )


def _replicate_variability(
    cases: list[ProfileCase], latitude: np.ndarray
) -> list[ReplicateVariability]:
    records = []
    for code in sorted({case.code for case in cases}):
        group = [case for case in cases if case.code == code]
        truth = np.stack([case.truth for case in group])
        model_error = ScoreSummary.from_values(
            profile_relative_l2_values(
                np.stack([case.prediction for case in group]), truth, latitude
            )
        )
        deviation = ScoreSummary(None, 0, 0)
        if len(group) > 1:
            reference = np.broadcast_to(truth.mean(axis=0), truth.shape)
            deviation = ScoreSummary.from_values(
                profile_relative_l2_values(truth, reference, latitude)
            )
        records.append(
            ReplicateVariability(
                code, len(group), group[0].split, deviation, model_error
            )
        )
    return records


def build_target_evaluation(
    results: list[SimulationSamples | SimulationPrediction],
    splits: Splits,
    index: int,
    sweep: SweepFile | None,
) -> TargetEvaluation:
    membership = {
        path.resolve(): name
        for name, paths in (
            ("train", splits.train),
            ("val", splits.validation),
            ("test", splits.test),
        )
        for path in paths
    }
    first = results[0]
    target = TargetEvaluation(
        diagnostic_for(first.metadata.y_vars[index]),
        first.lat,
        [
            ProfileCase(
                sr.sim_dir,
                sr.code,
                membership[sr.sim_dir.resolve()],
                sr.truth_profile[index],
                sr.pred_profile[index],
                (
                    getattr(sr, "window_predictions", None)[:, index]
                    if getattr(sr, "window_predictions", None) is not None
                    else None
                ),
                (
                    sr.window_baselines[:, index]
                    if getattr(sr, "window_baselines", None) is not None
                    else None
                ),
                getattr(sr, "target_overlap", None),
            )
            for sr in results
        ],
    )
    target.predictors, target.nearest = baseline_predictions(target.cases, sweep)
    target.scores = [
        score_predictor(p, target.test_cases, target.latitude)
        for p in target.predictors
    ]
    target.variability = _replicate_variability(target.cases, target.latitude)
    from ml.diagnostics.learning import learning_diagnostics

    target.learning = learning_diagnostics(target)
    return target
