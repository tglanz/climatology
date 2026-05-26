import argparse
import json
import math
import os
from pathlib import Path

import numpy as np

from isca import BarotropicCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE


def next_run_dir(experiment_dir: Path) -> Path:
    n = 0
    while (experiment_dir / str(n)).exists():
        n += 1
    return experiment_dir / str(n)

def is_fft_friendly(n):
    """Check if n only has prime factors 2, 3, and 5."""
    if n == 0: return False
    for p in [2, 3, 5]:
        while n % p == 0:
            n //= p
    return n == 1

def alias_free_grid(num_fourier):
    # Minimum requirements for alias-free quadratic products
    min_lat = math.ceil((3 * num_fourier + 1) / 2)
    min_lon = 3 * num_fourier + 1

    # 1. Ensure num_lat is even (standard for Gaussian grids)
    num_lat = min_lat if min_lat % 2 == 0 else min_lat + 1

    # 2. Find the next FFT-friendly number for num_lon
    num_lon = min_lon
    while not is_fft_friendly(num_lon):
        num_lon += 1

    return num_lat, num_lon


def sample_ic(seed: int) -> dict:
    """Draw a deterministic initial-condition parameter set from a seeded RNG.

    The four knobs are the ones exposed by Isca's barotropic_dynamics_nml; randomness
    across sims comes entirely from this function. Re-running with the same seed
    reproduces the same IC.
    """
    rng = np.random.default_rng(seed)
    return {
        'm_0'       : int(rng.integers(3, 7)),               # inclusive 3..6
        'zeta_0'    : float(rng.uniform(4.0e-5, 1.6e-4)),
        'eddy_lat'  : float(rng.uniform(25.0, 65.0)),
        'eddy_width': float(rng.uniform(10.0, 20.0)),
    }


class Settings:
    Cores = 8
    Segments = 15
    DtAtmosSec = 1200
    FourierHarmonics = 85

EXPERIMENT_BASE = 'barotropic_decaying'
OUTPUT_DIR = Path('output')

cb = BarotropicCodeBase.from_directory(GFDL_BASE)

# DiagTable: same fields as the stirring run minus the three stirring_mod entries,
# which do not exist when stirring is disabled.
diag = DiagTable()
diag.add_file('atmos_daily', 1, 'days', time_units='days')

# Zonal wind component [m/s]
diag.add_field('barotropic_diagnostics', 'ucomp',    time_avg=True)
# Meridional wind component [m/s]
diag.add_field('barotropic_diagnostics', 'vcomp',    time_avg=True)
# Relative vorticity zeta = dv/dx - du/dy [1/s]
diag.add_field('barotropic_diagnostics', 'vor',      time_avg=True)
# Absolute (planetary) vorticity f + zeta [1/s]
diag.add_field('barotropic_diagnostics', 'pv',       time_avg=True)
# Streamfunction psi where u = -dpsi/dy, v = dpsi/dx [m^2/s]
diag.add_field('barotropic_diagnostics', 'stream',   time_avg=True)
# Spectral tracer advected in spectral space via the leapfrog scheme [dimensionless]
diag.add_field('barotropic_diagnostics', 'trs',      time_avg=True)
# Grid tracer advected in grid space via finite-volume advection [dimensionless]
diag.add_field('barotropic_diagnostics', 'tr',       time_avg=True)
# Eddy vorticity: relative vorticity with the zonal mean (m=0) removed [1/s]
diag.add_field('barotropic_diagnostics', 'eddy_vor', time_avg=True)
# Change in zonal wind from initial profile: u_bar - u_init [m/s]
diag.add_field('barotropic_diagnostics', 'delta_u',  time_avg=True)

num_lat, num_lon = alias_free_grid(Settings.FourierHarmonics)


def build_namelist(ic: dict) -> Namelist:
    return Namelist({
        # FMS top-level run control
        'main_nml': {
            'days'    : 7,
            'hours'   : 0,
            'minutes' : 0,
            'seconds' : 0,
            'dt_atmos': Settings.DtAtmosSec,
            'calendar': 'no_calendar',
        },

        'atmosphere_nml': {
            'print_interval': 86400,
        },

        'fms_io_nml': {
            'threading_write': 'single',
            'fileset_write'  : 'single',
        },

        'fms_nml': {
            'print_memory_usage': True,
            'domains_stack_size': 200000,
        },

        # Barotropic dynamical core, unforced configuration mirroring
        # submodules/isca/exp/test_cases/barotropic_vorticity_equation/barotropic_vor_eq_test.py
        'barotropic_dynamics_nml': {
            'triang_trunc'  : True,
            'num_fourier'   : Settings.FourierHarmonics,
            'num_spherical' : Settings.FourierHarmonics + 1,
            'num_lat'       : num_lat,
            'num_lon'       : num_lon,
            'fourier_inc'   : 1,
            'damping_option': 'resolution_dependent',
            # Order 4 (del^8) damps small scales more sharply than the order-2
            # biharmonic used in the stirring run, since here there is no source
            # of small-scale energy and we want any energy that does cascade
            # downscale to dissipate cleanly.
            'damping_order' : 4,
            'damping_coeff' : 1.0e-4,
            # No linear drag (no damping_coeff_r): without stirring there is no
            # mean-flow acceleration to balance, so surface-friction-like drag
            # would just bleed energy out of the large scales.
            'grid_tracer'   : True,
            'spec_tracer'   : True,
            # Per-sim sampled initial condition.
            'm_0'           : ic['m_0'],
            'zeta_0'        : ic['zeta_0'],
            'eddy_lat'      : ic['eddy_lat'],
            'eddy_width'    : ic['eddy_width'],
            'robert_coeff'  : 0.04,
        },

        'barotropic_physics_nml': {},
    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--compile', action='store_true', help='compile only, do not run')
    parser.add_argument('--index', type=int, default=None, help='run index; if omitted, auto-increments')
    args = parser.parse_args()

    experiment_dir = OUTPUT_DIR / f"{EXPERIMENT_BASE}-T{Settings.FourierHarmonics}"
    simulations_dir = experiment_dir / 'simulations'

    if args.index is not None:
        exp_name = str(args.index)
        last_segment = simulations_dir / exp_name / f"run{Settings.Segments:04d}" / 'atmos_daily.nc'
        if last_segment.exists():
            print(f"[skip] index={exp_name}: {last_segment} already exists")
            raise SystemExit(0)

    cb.compile()
    if args.compile:
        raise SystemExit(0)

    if args.index is None:
        exp_name = next_run_dir(simulations_dir).name

    seed = int(exp_name)
    ic = sample_ic(seed)
    print(f"[ic] index={exp_name} seed={seed} {ic}")

    sim_dir = simulations_dir / exp_name
    sim_dir.mkdir(parents=True, exist_ok=True)
    with open(sim_dir / 'ic.json', 'w') as f:
        json.dump({'seed': seed, **ic}, f, indent=2)

    exp = Experiment(exp_name, codebase=cb, database=str(simulations_dir))
    exp.diag_table = diag
    exp.clear_rundir()
    exp.namelist = build_namelist(ic)

    exp.run(1, use_restart=False, num_cores=Settings.Cores)
    for i in range(2, Settings.Segments + 1):
        exp.run(i, num_cores=Settings.Cores)
