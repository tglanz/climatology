import logging
from collections import defaultdict
from pathlib import Path

import click
import numpy as np
import torch

from ml.config import load as load_config
from ml.data.splits import Splits
from ml.data.sweep_file import SweepFile
from ml.diagnostics.evaluation import (
    SimResult,
    load_all_sims,
    profile_rel_l2,
)
from ml.diagnostics.spatial import cosine_latitude_weights
from ml.training.model import build_model
from ml.visualization.evaluation import (
    plot_baselines_bar,
    plot_baselines_profiles,
    plot_error_bias,
    plot_error_histogram,
    plot_generalization_param,
    plot_generalization_worst,
    plot_jet_scatter,
    plot_model_vs_noise_floor,
    plot_noise_floor_summary,
    plot_training_curve,
)

log = logging.getLogger(__name__)


@click.group()
def evaluate():
    pass


@evaluate.command("model")
@click.option("--training-dir", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--n-workers", default=8, show_default=True, type=int)
@click.option("--batch-size", default=64, show_default=True, type=int)
def evaluate_model(training_dir: Path, n_workers: int, batch_size: int):
    """Evaluate a trained SFNO model against all available simulation data."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    training_dir = training_dir.resolve()
    out_dir = training_dir / "evaluation"
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    cfg = load_config(training_dir / "config.toml")

    # experiment_dir in config is relative to project root, not to training_dir.
    # The canonical experiment layout has training/ as a direct child of exp_dir.
    exp_dir = training_dir.parent
    sim_dir_root = exp_dir / "simulations"
    assert sim_dir_root.exists(), f"simulations dir not found: {sim_dir_root}"

    sweep_path = exp_dir / "sweep.json"
    sweep = SweepFile(sweep_path) if sweep_path.exists() else None

    splits_manifest = training_dir / "splits.json"
    assert splits_manifest.exists(), f"splits.json not found in training dir: {splits_manifest}"
    log.info("using splits: %s", splits_manifest)
    splits = Splits.load(splits_manifest)

    test_set = set(splits.test)
    val_set = set(splits.validation)
    train_set = set(splits.train)

    all_sim_dirs = sorted(sim_dir_root.iterdir())
    log.info("found %d simulation directories", len(all_sim_dirs))

    log.info("loading simulations from NC files (%d workers)...", n_workers)
    sim_results = load_all_sims(all_sim_dirs, cfg.data, max_workers=n_workers)
    log.info("loaded %d simulations", len(sim_results))

    assert sim_results, "no simulations loaded"
    lat = sim_results[0].lat

    def split_label(sim_dir: Path) -> str:
        if sim_dir in test_set:
            return "test"
        if sim_dir in val_set:
            return "val"
        if sim_dir in train_set:
            return "train"
        return "unknown"

    model = _load_model(cfg, training_dir)
    norm = torch.load(training_dir / "normalization.pt", map_location="cpu", weights_only=True)
    device = _select_device()
    log.info("running inference on device: %s", device)
    model = _warmup_and_move(model, sim_results[0].x_windows.shape[1:], device)

    log.info("running inference on all sims...")
    for sr in sim_results:
        sr.pred_profile = _infer_mean_profile(model, norm, sr.x_windows, device, batch_size)

    has_training_curve = _section0_training_curve(training_dir, fig_dir)
    nearest_rows = _section1_baselines(sim_results, lat, splits, sweep, fig_dir)
    noise_floor_data = _section2_noise_floor(sim_results, lat, fig_dir)
    _section3_generalization(sim_results, lat, sweep, splits, fig_dir)
    _section4_error_structure(sim_results, lat, splits, fig_dir)
    _section5_summary_scatter(noise_floor_data, sim_results, splits, fig_dir)

    _write_report(out_dir, fig_dir, has_training_curve=has_training_curve, nearest_rows=nearest_rows, splits=splits, sim_results=sim_results, sweep=sweep)
    log.info("evaluation complete: %s", out_dir)


def _section0_training_curve(training_dir: Path, fig_dir: Path) -> bool:
    import matplotlib.pyplot as plt
    csv_path = training_dir / "epoch-metrics.csv"
    if not csv_path.exists():
        log.warning("epoch-metrics.csv not found; skipping training curve")
        return False
    log.info("section 0: training curve")
    fig = plot_training_curve(csv_path)
    fig.savefig(fig_dir / "training_curve.png", dpi=150)
    plt.close(fig)
    return True


def _load_model(cfg, training_dir: Path):
    model = build_model(cfg.model, dropout=None, zonal_mean=True)
    params_path = training_dir / "parameters.pt"
    assert params_path.exists(), f"model parameters not found: {params_path}"
    state = torch.load(params_path, map_location="cpu", weights_only=False)
    state.pop("_metadata", None)
    model.load_state_dict(state)
    model.eval()
    return model


def _select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _warmup_and_move(model, x_shape: tuple, device: torch.device):
    if device.type != "cpu":
        model.cpu()
        with torch.no_grad():
            model(torch.zeros(1, *x_shape))
        for m in model.modules():
            if hasattr(m, "_grid"):
                m._grid = None
    model.to(device)
    return model


def _infer_mean_profile(
    model,
    norm: dict,
    x_windows: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> np.ndarray:
    x_mean = norm["x_mean"].to(device)
    x_std = norm["x_std"].to(device)
    y_mean = norm["y_mean"].to(device)
    y_std = norm["y_std"].to(device)

    x_tensor = torch.from_numpy(x_windows)
    preds = []
    with torch.no_grad():
        for i in range(0, len(x_tensor), batch_size):
            xb = x_tensor[i : i + batch_size].to(device)
            xb_norm = (xb - x_mean) / x_std
            yb_norm = model(xb_norm)
            yb = yb_norm * y_std + y_mean
            preds.append(yb.squeeze(1).cpu().numpy())
    preds_all = np.concatenate(preds, axis=0)
    return preds_all.mean(axis=0)


def _section1_baselines(
    sim_results: list,
    lat: np.ndarray,
    splits: Splits,
    sweep,
    fig_dir: Path,
) -> list[dict]:
    log.info("section 1: baselines")
    test_results = [sr for sr in sim_results if sr.sim_dir in set(splits.test)]
    train_results = [sr for sr in sim_results if sr.sim_dir in set(splits.train)]

    if not test_results:
        log.warning("no test-split sims found; skipping baselines")
        return []

    truth_test = np.stack([sr.truth_profile for sr in test_results])
    train_truths = np.stack([sr.truth_profile for sr in train_results]) if train_results else truth_test
    global_train_mean = train_truths.mean(axis=0)

    def _rl2_all(pred_fn) -> float:
        return float(np.mean([profile_rel_l2(pred_fn(sr), sr.truth_profile, lat) for sr in test_results]))

    zero_score = _rl2_all(lambda sr: np.zeros_like(sr.truth_profile))
    mean_score = _rl2_all(lambda sr: global_train_mean)
    model_score = _rl2_all(lambda sr: sr.pred_profile)

    nearest_score = mean_score
    nearest_rows = []
    if sweep is not None and train_results:
        nearest_score = _rl2_all(lambda sr: _nearest_config_pred(sr.code, train_results, sweep))
        seen_codes = set()
        for sr in test_results:
            if sr.code in seen_codes:
                continue
            seen_codes.add(sr.code)
            info = _nearest_config_info(sr.code, train_results, sweep)
            if info is None:
                continue
            _, nearest_code, dist = info
            test_params = sweep.params_for(sr.code) or {}
            nearest_params = sweep.params_for(nearest_code) or {}
            nearest_rows.append({
                "test_code": sr.code,
                "test_params": test_params,
                "nearest_code": nearest_code,
                "nearest_params": nearest_params,
                "distance": dist,
            })

    names = ["zero", "train mean", "nearest config", "model"]
    scores = [zero_score, mean_score, nearest_score, model_score]

    fig = plot_baselines_bar(names, scores, highlight_idx=3)
    fig.savefig(fig_dir / "baselines_bar.png", dpi=150)
    import matplotlib.pyplot as plt
    plt.close(fig)

    pred_profiles_dict = {
        "zero": np.zeros_like(global_train_mean),
        "train mean": global_train_mean,
        "model mean": np.mean([sr.pred_profile for sr in test_results], axis=0),
    }
    fig = plot_baselines_profiles(lat, truth_test.mean(axis=0), pred_profiles_dict)
    fig.savefig(fig_dir / "baselines_profiles.png", dpi=150)
    plt.close(fig)

    return nearest_rows


def _nearest_config_info(
    code: str,
    train_results: list,
    sweep: SweepFile,
) -> tuple[np.ndarray, str, float] | None:
    """Return (pred_profile, nearest_code, distance) for the nearest training config."""
    varying = sweep.varying_keys()
    if not varying:
        return None

    test_params = sweep.params_for(code)
    if test_params is None:
        return None

    train_codes_seen: dict[str, list] = defaultdict(list)
    for sr in train_results:
        train_codes_seen[sr.code].append(sr.truth_profile)

    param_matrix = np.array([[sweep.params_for(c)[k] for k in varying] for c in train_codes_seen])
    test_vec = np.array([test_params[k] for k in varying], dtype=float)

    ranges = param_matrix.max(axis=0) - param_matrix.min(axis=0)
    ranges[ranges == 0] = 1.0
    norm_matrix = (param_matrix - param_matrix.min(axis=0)) / ranges
    norm_test = (test_vec - param_matrix.min(axis=0)) / ranges

    dists = np.linalg.norm(norm_matrix - norm_test, axis=1)
    best_idx = int(np.argmin(dists))
    best_code = list(train_codes_seen.keys())[best_idx]
    pred = np.mean(train_codes_seen[best_code], axis=0)
    return pred, best_code, float(dists[best_idx])


def _nearest_config_pred(code: str, train_results: list, sweep: SweepFile) -> np.ndarray:
    info = _nearest_config_info(code, train_results, sweep)
    if info is None:
        return np.mean([sr.truth_profile for sr in train_results], axis=0)
    return info[0]


def _section2_noise_floor(sim_results: list, lat: np.ndarray, fig_dir: Path) -> dict:
    log.info("section 2: noise floor")
    import matplotlib.pyplot as plt

    by_code: dict[str, list] = defaultdict(list)
    for sr in sim_results:
        by_code[sr.code].append(sr)

    codes, noise_rels, model_rels = [], [], []
    for code, srs in by_code.items():
        if len(srs) < 2:
            continue
        profiles = [sr.truth_profile for sr in srs]
        ensemble_mean = np.mean(profiles, axis=0)
        noise_rels.append(float(np.mean([profile_rel_l2(p, ensemble_mean, lat) for p in profiles])))
        model_rels.append(float(np.mean([profile_rel_l2(sr.pred_profile, sr.truth_profile, lat) for sr in srs])))
        codes.append(code)

    if codes:
        fig = plot_noise_floor_summary(codes, noise_rels, model_rels)
        fig.savefig(fig_dir / "noise_floor_summary.png", dpi=150)
        plt.close(fig)

    return {"codes": codes, "noise_rels": noise_rels, "model_rels": model_rels}


def _section3_generalization(
    sim_results: list,
    lat: np.ndarray,
    sweep,
    splits: Splits,
    fig_dir: Path,
):
    log.info("section 3: generalization")
    import matplotlib.pyplot as plt

    if sweep is None:
        log.warning("no sweep file; skipping generalization")
        return

    by_code: dict[str, list] = defaultdict(list)
    for sr in sim_results:
        by_code[sr.code].append(sr)

    test_set = set(splits.test)
    val_set = set(splits.validation)
    train_set = set(splits.train)

    def split_label_for_code(srs):
        for sr in srs:
            if sr.sim_dir in test_set:
                return "test"
        for sr in srs:
            if sr.sim_dir in val_set:
                return "val"
        for sr in srs:
            if sr.sim_dir in train_set:
                return "train"
        return "unknown"

    code_rels = {}
    for code, srs in by_code.items():
        rels = [profile_rel_l2(sr.pred_profile, sr.truth_profile, lat) for sr in srs]
        code_rels[code] = float(np.mean(rels))

    varying = sweep.varying_keys()
    for param_name in varying:
        param_values = []
        model_rels = []
        split_labels = []
        for code, srs in by_code.items():
            params = sweep.params_for(code)
            if params is None:
                continue
            param_values.append(float(params[param_name]))
            model_rels.append(code_rels.get(code, float("nan")))
            split_labels.append(split_label_for_code(srs))
        fig = plot_generalization_param(param_name, param_values, model_rels, split_labels)
        safe_name = param_name.replace("/", "_")
        fig.savefig(fig_dir / f"generalization_{safe_name}.png", dpi=150)
        plt.close(fig)

    sorted_by_rel = sorted(code_rels.items(), key=lambda kv: kv[1], reverse=True)
    worst_codes = sorted_by_rel[:6]
    worst_cases = []
    for code, rel in worst_codes:
        srs = by_code[code]
        truth_mean = np.mean([sr.truth_profile for sr in srs], axis=0)
        pred_mean = np.mean([sr.pred_profile for sr in srs], axis=0)
        worst_cases.append((code, truth_mean, pred_mean, rel))

    if worst_cases:
        fig = plot_generalization_worst(lat, worst_cases)
        fig.savefig(fig_dir / "generalization_worst.png", dpi=150)
        plt.close(fig)


def _section4_error_structure(
    sim_results: list,
    lat: np.ndarray,
    splits: Splits,
    fig_dir: Path,
):
    log.info("section 4: error structure")
    import matplotlib.pyplot as plt

    test_results = [sr for sr in sim_results if sr.sim_dir in set(splits.test)]
    if not test_results:
        log.warning("no test-split sims; skipping error structure")
        return

    all_preds = []
    all_truths = []
    for sr in test_results:
        all_preds.append(sr.pred_profile)
        all_truths.append(sr.truth_profile)

    preds_arr = np.stack(all_preds)
    truths_arr = np.stack(all_truths)
    errors = preds_arr - truths_arr

    fig = plot_error_bias(lat, errors)
    fig.savefig(fig_dir / "error_bias.png", dpi=150)
    plt.close(fig)

    rel_l2_vals = np.array([profile_rel_l2(p, t, lat) for p, t in zip(all_preds, all_truths)])
    fig = plot_error_histogram(rel_l2_vals)
    fig.savefig(fig_dir / "error_histogram.png", dpi=150)
    plt.close(fig)

    truth_jet_lat = np.array([float(lat[np.argmax(np.abs(t))]) for t in truths_arr])
    pred_jet_lat = np.array([float(lat[np.argmax(np.abs(p))]) for p in preds_arr])
    fig = plot_jet_scatter(
        truth_jet_lat, pred_jet_lat,
        "truth peak lat [deg]", "pred peak lat [deg]",
        "Jet latitude: predicted vs truth",
    )
    fig.savefig(fig_dir / "error_jet_lat.png", dpi=150)
    plt.close(fig)

    truth_jet_amp = np.array([float(np.max(np.abs(t))) for t in truths_arr])
    pred_jet_amp = np.array([float(np.max(np.abs(p))) for p in preds_arr])
    fig = plot_jet_scatter(
        truth_jet_amp, pred_jet_amp,
        "truth peak amplitude [m/s]", "pred peak amplitude [m/s]",
        "Jet amplitude: predicted vs truth",
    )
    fig.savefig(fig_dir / "error_jet_amp.png", dpi=150)
    plt.close(fig)


def _section5_summary_scatter(
    noise_floor_data: dict,
    sim_results: list,
    splits: Splits,
    fig_dir: Path,
):
    log.info("section 5: model vs noise floor summary")
    import matplotlib.pyplot as plt

    codes = noise_floor_data["codes"]
    if not codes:
        return

    test_set = set(splits.test)
    val_set = set(splits.validation)
    train_set = set(splits.train)

    by_code: dict[str, list] = defaultdict(list)
    for sr in sim_results:
        by_code[sr.code].append(sr)

    split_labels = []
    for code in codes:
        srs = by_code.get(code, [])
        if any(sr.sim_dir in test_set for sr in srs):
            split_labels.append("test")
        elif any(sr.sim_dir in val_set for sr in srs):
            split_labels.append("val")
        elif any(sr.sim_dir in train_set for sr in srs):
            split_labels.append("train")
        else:
            split_labels.append("unknown")

    fig = plot_model_vs_noise_floor(
        codes,
        noise_floor_data["noise_rels"],
        noise_floor_data["model_rels"],
        split_labels,
    )
    fig.savefig(fig_dir / "model_vs_noise_floor.png", dpi=150)
    plt.close(fig)


def _write_report(out_dir: Path, fig_dir: Path, has_training_curve: bool = True, nearest_rows: list[dict] | None = None, splits: Splits | None = None, sim_results: list | None = None, sweep=None):
    log.info("writing report.md")
    png_files = sorted(fig_dir.glob("*.png"))

    captions = {
        "training_curve.png": "Train and validation loss per epoch.",
        "baselines_bar.png": "relL2 of each predictor on the test split.",
        "baselines_profiles.png": "Mean truth and predictor profiles on the test split.",
        "noise_floor_summary.png": "Across-replicate noise floor (bars) vs model relL2 (dots) per config code, sorted ascending.",
        "model_vs_noise_floor.png": "Model relL2 vs noise floor relL2 per config, colored by split. Points above the diagonal exceed the noise floor.",
        "error_bias.png": "Per-sample (pred - truth) fan plot with mean bias (red) across test split.",
        "error_histogram.png": "Per-sample relL2 distribution across test split.",
        "error_jet_lat.png": "Predicted vs truth peak latitude across test split.",
        "error_jet_amp.png": "Predicted vs truth peak amplitude across test split.",
        "generalization_worst.png": "Profile overlays for the 6 worst-scoring config codes.",
    }

    generalization_figs = sorted(
        [f.name for f in png_files if f.name.startswith("generalization_") and f.name != "generalization_worst.png"]
    )

    training_figs = ["training_curve.png"] if has_training_curve else []
    sections = [
        ("Training", training_figs),
        ("Baselines", ["baselines_bar.png", "baselines_profiles.png"]),
        ("Noise Floor", ["noise_floor_summary.png", "model_vs_noise_floor.png"]),
        ("Generalization", generalization_figs + ["generalization_worst.png"]),
        ("Error Structure", ["error_bias.png", "error_histogram.png", "error_jet_lat.png", "error_jet_amp.png"]),
    ]

    lines = [
        "---",
        "header-includes:",
        "  - \\usepackage{float}",
        "  - \\floatplacement{figure}{H}",
        "---",
        "",
        "# Evaluation Report",
        "",
    ]

    if splits is not None and sim_results is not None:
        test_set = set(splits.test)
        val_set = set(splits.validation)
        train_set = set(splits.train)

        by_code: dict[str, list] = defaultdict(list)
        for sr in sim_results:
            by_code[sr.code].append(sr)

        def _split_label(srs):
            if any(sr.sim_dir in test_set for sr in srs): return "test"
            if any(sr.sim_dir in val_set for sr in srs): return "val"
            if any(sr.sim_dir in train_set for sr in srs): return "train"
            return "unknown"

        lines.append("## Split Summary")
        lines.append("")
        lines.append(f"| | count |")
        lines.append(f"|---|---|")
        lines.append(f"| train | {len(splits.train)} |")
        lines.append(f"| val | {len(splits.validation)} |")
        lines.append(f"| test | {len(splits.test)} |")
        lines.append("")

        if sweep is not None:
            varying = sweep.varying_keys()
            if varying:
                header = "| code | split | " + " | ".join(varying) + " |"
                sep = "|---|---|" + "---|" * len(varying)
                lines.append(header)
                lines.append(sep)
                for code, srs in sorted(by_code.items(), key=lambda kv: (_split_label(kv[1]), kv[0])):
                    label = _split_label(srs)
                    params = sweep.params_for(code)
                    param_vals = " | ".join(str(params.get(k, "")) for k in varying) if params else " | ".join("" for _ in varying)
                    lines.append(f"| {code} | {label} | {param_vals} |")
                lines.append("")
    for section_num, (section_title, fig_names) in enumerate(sections, start=1):
        lines.append(f"## {section_num}. {section_title}")
        lines.append("")
        if not fig_names and section_title == "Training":
            lines.append("> No training metrics available.")
            lines.append("")
        for fname in fig_names:
            if not (fig_dir / fname).exists():
                continue
            caption = captions.get(fname)
            if caption is None and fname.startswith("generalization_"):
                param = fname.replace("generalization_", "").replace(".png", "")
                caption = f"relL2 vs {param} value, colored by split."
            lines.append(f"![{fname}](figures/{fname})")
            lines.append("")
            if caption:
                lines.append(caption)
                lines.append("")
        if section_title == "Baselines" and nearest_rows:
            varying_keys = list(nearest_rows[0]["test_params"].keys())
            header = "| test code | " + " | ".join(varying_keys) + " | nearest code | " + " | ".join(f"nearest {k}" for k in varying_keys) + " | distance |"
            sep = "|---|" + "---|" * len(varying_keys) + "---|" + "---|" * len(varying_keys) + "---|"
            lines.append("### Nearest training config per test code")
            lines.append("")
            lines.append(header)
            lines.append(sep)
            for row in sorted(nearest_rows, key=lambda r: r["test_code"]):
                test_vals = " | ".join(str(row["test_params"].get(k, "")) for k in varying_keys)
                near_vals = " | ".join(str(row["nearest_params"].get(k, "")) for k in varying_keys)
                lines.append(f"| {row['test_code']} | {test_vals} | {row['nearest_code']} | {near_vals} | {row['distance']:.3f} |")
            lines.append("")

    report_path = out_dir / "report.md"
    report_path.write_text("\n".join(lines))
    log.info("report written to %s", report_path)
