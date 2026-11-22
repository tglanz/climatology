"""By-configuration evaluation using the canonical simulation sample contract."""

import json
from pathlib import Path

from ml.training.normalization import Normalization
from ml.services.simulations import list_simulation_dirs

from ml.data.simulation_data import try_read_simulation
from ml.data.climatology import diagnostic_for
from ml.diagnostics.errors import profile_rel_l2, profile_rmse
from ml.inference import predict_windows


def code_label(code: str, sim_root: Path) -> str:
    path = next(sim_root.glob(f"{code}-*/namelist.json"), None)
    if path is None:
        return code
    stirring = json.loads(path.read_text())["stirring_nml"]
    return f"{code} lat0={stirring['lat0']} amp={stirring['amplitude']:.2e} widthy={stirring['widthy']}"


def find_replicates(code: str, simulations) -> list[Path]:
    dirs = [
        p for p in list_simulation_dirs(simulations) if p.name.rsplit("-", 1)[0] == code
    ]
    if not dirs:
        raise ValueError(f"no simulations found for code {code!r}")
    return dirs


def evaluate_sim(sim_dir: Path, cfg, model, norm):
    norm = Normalization.from_dict(norm) if isinstance(norm, dict) else norm
    outcome = try_read_simulation(sim_dir, cfg.data, cfg.simulations.segment_pattern)
    if outcome.samples is None:
        return None
    result = outcome.samples
    if not result.metadata.matches(norm.metadata):
        raise ValueError("by-code samples differ from the checkpoint contract")
    device = next(model.parameters()).device
    result.predictions = predict_windows(model, norm, result.x_windows, device, 64)
    return result


def collect(codes, cfg, model, norm):
    return {
        code: (
            code_label(code, find_replicates(code, cfg.simulations)[0].parent),
            [
                result
                for path in find_replicates(code, cfg.simulations)
                if (result := evaluate_sim(path, cfg, model, norm)) is not None
            ],
        )
        for code in codes
    }


def print_metrics(code_results):
    for _, (label, results) in code_results.items():
        print(label)
        for result in results:
            for index, name in enumerate(result.metadata.y_vars):
                target = diagnostic_for(name)
                rmse = profile_rmse(
                    result.pred_profile[index], result.truth_profile[index], result.lat
                )
                relative = profile_rel_l2(
                    result.pred_profile[index], result.truth_profile[index], result.lat
                )
                print(
                    f"  {result.sim_dir.name} {name}: RMSE={rmse:.6g} [{target.units}], relL2={relative:.6g}; "
                    f"spinup={result.t_s}, convergence={result.t_c} [snapshot indices]"
                )
