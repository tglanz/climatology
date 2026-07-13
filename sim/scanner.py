import argparse
import hashlib
import itertools
import json
import shutil
from pathlib import Path

from isca.experiment import FailedRunError

from sim.barotropic_stirring import BarotropicStirring, BarotropicStirringParams
from sim.simulation import ExecutionParams

# NOTE: This scanner is currently hardcoded to BarotropicStirring. The Simulation
# abstraction was designed to eventually support multiple simulation types with
# different parameter sets. The scanner should be generalized (e.g. simulation type
# as a CLI argument, sweep params loaded from a config file) when a second simulation
# type is introduced.

OUTPUT_DIR = Path('output')


def _param_code(params: dict) -> str:
    s = json.dumps(params, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()[:6]


def _next_index(simulations_dir: Path, code: str) -> int:
    n = 0
    while (simulations_dir / f"{code}-{n}").exists():
        n += 1
    return n


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--compile',              action='store_true', help='Compile the codebase and exit.')
    parser.add_argument('--only-update-sweep-file', action='store_true', help='Merge new param codes into sweep.json without running simulations.')
    parser.add_argument('--index',            type=int,   default=None,  help='Replicate index per param config. Auto-incremented if omitted.')
    parser.add_argument('--experiment-name',  type=str,   default=None,  help='Output directory name under output/. Defaults to barotropic_stirring-T<harmonics>.')

    parser.add_argument('--max-retries',    type=int,   default=3,     help='Max retry attempts per simulation before marking as crashed.')
    parser.add_argument('--cores',            type=int,   default=8,     help='Number of MPI cores.')
    parser.add_argument('--segments',         type=int,   default=20,    help='Number of run segments.')
    parser.add_argument('--segment-days',     type=int,   default=7,     help='Simulated days per segment.')
    parser.add_argument('--dt-atmos',         type=int,   default=600,   help='Model timestep in seconds.')
    parser.add_argument('--fourier-harmonics',type=int,   default=85,    help='Spectral truncation T (triangular). Grid size is derived automatically.')

    parser.add_argument('--stirring-amplitude',   type=float, nargs='+', default=[1.0e-10],  help='Stirring vorticity forcing amplitude (s^-2).')
    parser.add_argument('--stirring-decay-time',  type=float, nargs='+', default=[172800.0], help='AR(1) decay time of stirring pattern in seconds.')
    parser.add_argument('--stirring-lat0',        type=float, nargs='+', default=[45.0],     help='Central latitude of stirring region (degrees).')
    parser.add_argument('--stirring-widthy',      type=float, nargs='+', default=[12.0],     help='Meridional half-width of stirring region (degrees).')
    parser.add_argument('--stirring-lon0',        type=float, nargs='+', default=[180.0],    help='Central longitude of stirring region (degrees).')
    parser.add_argument('--stirring-widthx',      type=float, nargs='+', default=[45.0],     help='Zonal half-width of stirring region (degrees).')
    parser.add_argument('--stirring-B',           type=float, nargs='+', default=[0.4],      help='Stirring asymmetry parameter (0 = symmetric, 1 = fully asymmetric).')

    args = parser.parse_args()

    experiment_name = args.experiment_name or f"barotropic_stirring-T{args.fourier_harmonics}"
    simulations_dir = OUTPUT_DIR / experiment_name / 'simulations'

    sweep_keys = ['stirring_amplitude', 'stirring_decay_time', 'stirring_lat0',
                  'stirring_widthy', 'stirring_lon0', 'stirring_widthx', 'stirring_B']
    sweep_values = [
        args.stirring_amplitude, args.stirring_decay_time, args.stirring_lat0,
        args.stirring_widthy, args.stirring_lon0, args.stirring_widthx, args.stirring_B,
    ]

    combos = [dict(zip(sweep_keys, vals)) for vals in itertools.product(*sweep_values)]
    codes  = {_param_code(c): c for c in combos}

    sweep_path = OUTPUT_DIR / experiment_name / 'sweep.json'
    sweep_path.parent.mkdir(parents=True, exist_ok=True)

    existing = json.loads(sweep_path.read_text()) if sweep_path.exists() else {}
    new_codes = {k: v for k, v in codes.items() if k not in existing}
    merged = {**existing, **new_codes}
    sweep_path.write_text(json.dumps(merged, indent=2))
    if new_codes:
        print(f"[sweep] added {len(new_codes)} new code(s): {list(new_codes)}")
    codes = merged

    if args.only_update_sweep_file:
        return

    if args.compile:
        BarotropicStirring(BarotropicStirringParams()).compile()
        return

    for code, stirring_params in codes.items():
        params = BarotropicStirringParams(
            fourier_harmonics   = args.fourier_harmonics,
            dt_atmos            = args.dt_atmos,
            segment_days        = args.segment_days,
            stirring_amplitude  = stirring_params['stirring_amplitude'],
            stirring_decay_time = stirring_params['stirring_decay_time'],
            stirring_lat0       = stirring_params['stirring_lat0'],
            stirring_widthy     = stirring_params['stirring_widthy'],
            stirring_lon0       = stirring_params['stirring_lon0'],
            stirring_widthx     = stirring_params['stirring_widthx'],
            stirring_B          = stirring_params['stirring_B'],
        )
        sim = BarotropicStirring(params)

        index = args.index if args.index is not None else _next_index(simulations_dir, code)
        sim_name = f"{code}-{index}"

        last_segment = simulations_dir / sim_name / f"run{args.segments:04d}" / 'atmos_daily.nc'
        if last_segment.exists():
            print(f"[skip] {sim_name}: {last_segment} already exists")
            continue

        ep = ExecutionParams(
            sim_name        = sim_name,
            simulations_dir = simulations_dir,
            num_cores       = args.cores,
            n_segments      = args.segments,
        )

        crashed_log = OUTPUT_DIR / experiment_name / 'crashed-sims.txt'
        for attempt in range(1, args.max_retries + 1):
            try:
                sim.execute(ep)
                break
            except FailedRunError:
                sim_out_dir  = ep.simulations_dir / ep.sim_name
                sim_work_dir = sim.work_dir(ep)
                if sim_out_dir.exists():
                    shutil.rmtree(sim_out_dir)
                if sim_work_dir.exists():
                    shutil.rmtree(sim_work_dir)

                if attempt < args.max_retries:
                    print(f"[retry] {sim_name}: attempt {attempt} failed, retrying...")
                else:
                    print(f"[failed] {sim_name}: all {args.max_retries} attempts failed, skipping")
                    with crashed_log.open('a') as f:
                        f.write(f"{sim_out_dir}\n{sim_work_dir}\n")


if __name__ == '__main__':
    main()
