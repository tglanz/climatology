import argparse
import json
import math
import os
from pathlib import Path

from isca import BarotropicCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE


def next_run_dir(simulations_dir: Path) -> Path:
    n = 0
    while (simulations_dir / str(n)).exists():
        n += 1
    return simulations_dir / str(n)


def is_fft_friendly(n: int) -> bool:
    if n == 0:
        return False
    for p in [2, 3, 5]:
        while n % p == 0:
            n //= p
    return n == 1


def alias_free_grid(num_fourier: int) -> tuple[int, int]:
    min_lat = math.ceil((3 * num_fourier + 1) / 2)
    min_lon = 3 * num_fourier + 1
    num_lat = min_lat if min_lat % 2 == 0 else min_lat + 1
    num_lon = min_lon
    while not is_fft_friendly(num_lon):
        num_lon += 1
    return num_lat, num_lon


def create_namelist_dict(args: argparse.Namespace) -> dict:
    num_lat, num_lon = alias_free_grid(args.fourier_harmonics)
    return {
        'main_nml': {
            'days'    : args.segment_days,
            'hours'   : 0,
            'minutes' : 0,
            'seconds' : 0,
            'dt_atmos': args.dt_atmos,
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
        'barotropic_dynamics_nml': {
            'triang_trunc'      : True,
            'num_fourier'       : args.fourier_harmonics,
            'num_spherical'     : args.fourier_harmonics + 1,
            'num_lat'           : num_lat,
            'num_lon'           : num_lon,
            'fourier_inc'       : 1,
            'damping_option'    : 'resolution_dependent',
            'damping_order'     : 2,
            'damping_coeff'     : 1.157e-4,
            'damping_coeff_r'   : 1.929e-6,
            'grid_tracer'       : True,
            'spec_tracer'       : True,
            'm_0'               : 6,
            'zeta_0'            : 0.0,
            'eddy_lat'          : 45.0,
            'eddy_width'        : 10.0,
            'robert_coeff'      : 0.04,
            'initial_zonal_wind': 'zero',
        },
        'barotropic_physics_nml': {},
        'stirring_nml': {
            'amplitude' : args.stirring_amplitude,
            'decay_time': args.stirring_decay_time,
            'lat0'      : args.stirring_lat0,
            'widthy'    : args.stirring_widthy,
            'lon0'      : args.stirring_lon0,
            'widthx'    : args.stirring_widthx,
            'B'         : args.stirring_B,
        },
    }


def create_namelist(args: argparse.Namespace) -> Namelist:
    return Namelist(create_namelist_dict(args))


OUTPUT_DIR = Path('output')

cb = BarotropicCodeBase.from_directory(GFDL_BASE)

diag = DiagTable()
diag.add_file('atmos_daily', 1, 'days', time_units='days')
diag.add_field('barotropic_diagnostics', 'ucomp',       time_avg=True)
diag.add_field('barotropic_diagnostics', 'vcomp',       time_avg=True)
diag.add_field('barotropic_diagnostics', 'vor',         time_avg=True)
diag.add_field('barotropic_diagnostics', 'pv',          time_avg=True)
diag.add_field('barotropic_diagnostics', 'stream',      time_avg=True)
diag.add_field('barotropic_diagnostics', 'trs',         time_avg=True)
diag.add_field('barotropic_diagnostics', 'tr',          time_avg=True)
diag.add_field('barotropic_diagnostics', 'eddy_vor',    time_avg=True)
diag.add_field('barotropic_diagnostics', 'delta_u',     time_avg=True)
diag.add_field('stirring_mod',           'stirring',     time_avg=True)
diag.add_field('stirring_mod',           'stirring_amp', time_avg=True)
diag.add_field('stirring_mod',           'stirring_sqr', time_avg=True)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--compile',          action='store_true', help='Compile the codebase and exit.')
    parser.add_argument('--index',            type=int,   default=None,     help='Simulation index. Auto-incremented if omitted.')
    parser.add_argument('--experiment-name',  type=str,   default=None,     help='Output directory name under output/. Defaults to barotropic_stirring-T<harmonics>.')

    parser.add_argument('--cores',            type=int,   default=8,        help='Number of MPI cores.')
    parser.add_argument('--segments',         type=int,   default=15,       help='Number of run segments.')
    parser.add_argument('--segment-days',     type=int,   default=7,        help='Simulated days per segment.')
    parser.add_argument('--dt-atmos',         type=int,   default=600,      help='Model timestep in seconds.')
    parser.add_argument('--fourier-harmonics',type=int,   default=85,       help='Spectral truncation T (triangular). Grid size is derived automatically.')

    parser.add_argument('--stirring-amplitude',  type=float, default=1.0e-10,  help='Stirring vorticity forcing amplitude (s^-2).')
    parser.add_argument('--stirring-decay-time', type=float, default=172800.0, help='AR(1) decay time of stirring pattern in seconds.')
    parser.add_argument('--stirring-lat0',       type=float, default=45.0,     help='Central latitude of stirring region (degrees).')
    parser.add_argument('--stirring-widthy',     type=float, default=12.0,     help='Meridional half-width of stirring region (degrees).')
    parser.add_argument('--stirring-lon0',       type=float, default=180.0,    help='Central longitude of stirring region (degrees).')
    parser.add_argument('--stirring-widthx',     type=float, default=45.0,     help='Zonal half-width of stirring region (degrees).')
    parser.add_argument('--stirring-B',          type=float, default=0.4,      help='Stirring asymmetry parameter (0 = symmetric, 1 = fully asymmetric).')

    args = parser.parse_args()

    experiment_name = args.experiment_name or f"barotropic_stirring-T{args.fourier_harmonics}"
    experiment_dir  = OUTPUT_DIR / experiment_name
    simulations_dir = experiment_dir / 'simulations'

    if args.index is not None:
        exp_name = str(args.index)
        last_segment = simulations_dir / exp_name / f"run{args.segments:04d}" / 'atmos_daily.nc'
        if last_segment.exists():
            print(f"[skip] index={exp_name}: {last_segment} already exists")
            raise SystemExit(0)

    cb.compile()
    if args.compile:
        raise SystemExit(0)

    if args.index is None:
        exp_name = next_run_dir(simulations_dir).name

    namelist_dict = create_namelist_dict(args)
    namelist = Namelist(namelist_dict)

    exp = Experiment(exp_name, codebase=cb, database=str(simulations_dir))
    exp.diag_table = diag
    exp.clear_rundir()
    exp.namelist = namelist

    sim_dir = simulations_dir / exp_name
    sim_dir.mkdir(parents=True, exist_ok=True)
    (sim_dir / 'namelist.json').write_text(json.dumps(namelist_dict, indent=2))

    exp.run(1, use_restart=False, num_cores=args.cores)
    for i in range(2, args.segments + 1):
        exp.run(i, num_cores=args.cores)


if __name__ == '__main__':
    main()
