"""Configuration-level evidence for learning beyond constant or averaged profiles."""

import numpy as np

from ml.diagnostics.grid import gaussian_latitude_weights, legendre_basis


def _ratio(numerator, denominator):
    return float(numerator / denominator) if denominator > 0 else None


def _skill(error, reference_error):
    ratio = _ratio(error, reference_error)
    return None if ratio is None else 1 - ratio


def _mse(prediction, truth, weights):
    return np.sum((prediction - truth) ** 2 * weights, axis=-1)


def _groups(cases, values):
    return np.stack(
        [
            np.mean(
                [v for c, v in zip(cases, values, strict=True) if c.code == code],
                axis=0,
            )
            for code in sorted({c.code for c in cases})
        ]
    )


def learning_diagnostics(target):
    weights = gaussian_latitude_weights(target.latitude)
    train = [c for c in target.cases if c.split == "train"]
    reference = np.mean([c.truth for c in train], axis=0) if train else None
    result = {
        "splits": {},
        "paired_test_skill": {},
        "seed": 17,
        "bootstrap_draws": 1000,
        "permutation_draws": 199,
    }
    for split in ("train", "val", "test"):
        cases = [c for c in target.cases if c.split == split]
        if not cases:
            continue
        truth = np.stack([c.truth for c in cases])
        pred = np.stack([c.prediction for c in cases])
        mse = float(_mse(pred, truth, weights).mean())
        observed = _groups(cases, truth)
        predicted = _groups(cases, pred)
        t = observed - observed.mean(0)
        p = predicted - predicted.mean(0)
        truth_spread = np.sum(t**2 * weights)
        pred_spread = np.sum(p**2 * weights)
        cross = np.sum(t * p * weights)
        row = {
            "simulations": len(cases),
            "configurations": len(observed),
            "mse": mse,
            "skill_over_train_mean": (
                None
                if reference is None
                else _skill(mse, _mse(reference, truth, weights).mean())
            ),
            "configuration_variance_ratio": _ratio(pred_spread, truth_spread),
            "configuration_anomaly_correlation": _ratio(
                cross, np.sqrt(truth_spread * pred_spread)
            ),
            "configuration_anomaly_slope": _ratio(cross, truth_spread),
        }
        windows = [c for c in cases if c.window_predictions is not None]
        row["window_prediction_mse_about_simulation_mean"] = (
            float(
                np.mean(
                    [
                        _mse(c.window_predictions, c.prediction, weights).mean()
                        for c in windows
                    ]
                )
            )
            if windows
            else None
        )
        overlaps = [c.target_overlap for c in cases if c.target_overlap is not None]
        row["input_target_overlap_fraction"] = (
            float(np.mean(overlaps)) if overlaps else None
        )
        if len(observed) >= 3:
            rng = np.random.default_rng(17)
            null = np.array(
                [
                    _mse(
                        predicted[rng.permutation(len(predicted))], observed, weights
                    ).mean()
                    for _ in range(199)
                ]
            )
            correct = float(_mse(predicted, observed, weights).mean())
            row["permuted_pairing_mse"] = float(null.mean())
            row["correct_pairing_mse"] = correct
            row["permutation_p"] = float((1 + np.count_nonzero(null <= correct)) / 200)
        else:
            row["permutation_p"] = None
        result["splits"][split] = row
    tests = target.test_cases
    if tests:
        truth = np.stack([c.truth for c in tests])
        model_error = _groups(
            tests, _mse(np.stack([c.prediction for c in tests]), truth, weights)
        )
        for predictor in target.predictors:
            if predictor.name == "model" or predictor.profiles is None:
                continue
            baseline_error = _groups(tests, _mse(predictor.profiles, truth, weights))
            difference = baseline_error - model_error
            rng = np.random.default_rng(17)
            draws = rng.integers(0, len(difference), (1000, len(difference)))
            lower, upper = (
                np.quantile(difference[draws].mean(axis=1), [0.025, 0.975])
                if len(difference) > 1
                else (None, None)
            )
            ratio = _ratio(model_error.mean(), baseline_error.mean())
            result["paired_test_skill"][predictor.name] = {
                "skill": None if ratio is None else 1 - ratio,
                "mse_improvement": float(difference.mean()),
                "ci95": [
                    None if lower is None else float(lower),
                    None if upper is None else float(upper),
                ],
                "configurations": len(difference),
            }
    # The exact discrete Gaussian projection measures representation error before fitting.
    height = len(weights)
    basis = legendre_basis(target.latitude, height)
    truth = np.stack([c.truth for c in target.cases])
    pred = np.stack([c.prediction for c in target.cases])
    coefficients = truth @ (weights[:, None] * basis)
    prediction_coefficients = pred @ (weights[:, None] * basis)
    result["spectrum"] = {
        "truth_energy": (coefficients**2).mean(0).tolist(),
        "error_energy": ((prediction_coefficients - coefficients) ** 2)
        .mean(0)
        .tolist(),
        "aggregation": "all loaded simulations, equal simulation weight",
    }
    result["truncation_rmse"] = {
        str(cutoff): float(
            np.sqrt(
                _mse(
                    coefficients[:, :cutoff] @ basis[:, :cutoff].T, truth, weights
                ).mean()
            )
        )
        for cutoff in sorted({min(height, n) for n in (1, 2, 4, 8, 16, 32, height)})
    }
    return result
