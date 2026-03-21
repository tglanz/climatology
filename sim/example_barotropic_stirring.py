import os

from isca import BarotropicCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE

# Use all available cores, rounded down to the nearest power of 2.
# Isca requires the core count to be a power of 2 (1, 2, 4, 8, 16, ...).
_cpu_count = os.cpu_count() or 1
NCORES = 2 ** (_cpu_count.bit_length() - 1)

cb = BarotropicCodeBase.from_directory(GFDL_BASE)
exp = Experiment('barotropic_stirring', codebase=cb)

diag = DiagTable()
diag.add_file('atmos_monthly', 30, 'days', time_units='days')

diag.add_field('barotropic_diagnostics', 'ucomp',    time_avg=True)
diag.add_field('barotropic_diagnostics', 'vcomp',    time_avg=True)
diag.add_field('barotropic_diagnostics', 'vor',      time_avg=True)
diag.add_field('barotropic_diagnostics', 'pv',       time_avg=True)
diag.add_field('barotropic_diagnostics', 'stream',   time_avg=True)
diag.add_field('barotropic_diagnostics', 'trs',      time_avg=True)
diag.add_field('barotropic_diagnostics', 'tr',       time_avg=True)
diag.add_field('barotropic_diagnostics', 'eddy_vor', time_avg=True)
diag.add_field('barotropic_diagnostics', 'delta_u',  time_avg=True)
diag.add_field('stirring_mod',           'stirring',     time_avg=True)
diag.add_field('stirring_mod',           'stirring_amp', time_avg=True)
diag.add_field('stirring_mod',           'stirring_sqr', time_avg=True)

exp.diag_table = diag
exp.clear_rundir()

exp.namelist = Namelist({
    'main_nml': {
        'days'    : 30,
        'hours'   : 0,
        'minutes' : 0,
        'seconds' : 0,
        'dt_atmos': 1200,
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
        'num_lat'           : 32,   # T21 resolution (~600km)
        'num_lon'           : 64,
        'num_fourier'       : 21,
        'num_spherical'     : 22,
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
        'decay_time': 172800,
        'amplitude' : 3.e-11,
        'lat0'      : 45.,
        'lon0'      : 180.,
        'widthy'    : 12.,
        'widthx'    : 45.,
        'B'         : 1.0,
    },
})

N_SEGMENTS = 12  # 12 x 30 days = 1 model year

if __name__ == '__main__':
    cb.compile()
    exp.run(1, use_restart=False, num_cores=NCORES)
    for i in range(2, N_SEGMENTS + 1):
        exp.run(i, num_cores=NCORES)
