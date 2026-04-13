import math
import os

from isca import BarotropicCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE

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

# Use all available cores, rounded down to the nearest power of 2.
# Isca requires the core count to be a power of 2 (1, 2, 4, 8, 16, ...).
_cpu_count = os.cpu_count() or 1
# NCORES = 2 ** (_cpu_count.bit_length() - 1)
class Settings:
    Cores = 2
    Segments = 15
    DtAtmosSec = 600
    StirringAmplitude = 1.0e-10
    StirringB = 0.4
    FourierHarmonics = 85

experiment_name = 'barotropic_stirring'
cb = BarotropicCodeBase.from_directory(GFDL_BASE)
exp = Experiment('', codebase=cb, database=f"output/{experiment_name}-T{Settings.FourierHarmonics}")

# DiagTable controls which model fields are written to NetCDF output and at what frequency.
# Fields must be registered in the Fortran source via register_diag_field; the table acts as
# a filter that selects which of those registered fields to actually write and how to average them.
#
# The add_field is defined by:
#   add_field(self, module, name, time_avg=False, files=None):
#
# Fields defined in submodules/isca/src/atmos_spectral_barotropic/barotropic_diagnostics.F90
diag = DiagTable()
diag.add_file('atmos_daily', 1, 'days', time_units='days')

# PRESUMEBLY; everything other than vorticity can be reconstructed.

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
# Instantaneous stirring forcing (vorticity tendency) in grid space [1/s^2]
diag.add_field('stirring_mod',           'stirring',     time_avg=True)
# Spatial amplitude envelope of the stirring: amplitude * localize(lon, lat) [dimensionless]
diag.add_field('stirring_mod',           'stirring_amp', time_avg=True)
# Time-mean of stirring^2 over the full integration, written at run end [1/s^4]
diag.add_field('stirring_mod',           'stirring_sqr', time_avg=True)

exp.diag_table = diag
exp.clear_rundir()

num_lat, num_lon = alias_free_grid(Settings.FourierHarmonics)

# The available namelists are defined in the F90 modules.
# To find how the modules involved we need to find the modules of the relevant executable.
# In this case, we use `BarotropicCodeBase`, inside it look for the name.
# Then, the file paths are defined in submodules/isca/src/extra/model/barotropic/path_names.
exp.namelist = Namelist({
    # FMS top-level run control
    'main_nml': {
        # Total integration length
        'days'    : 7,
        'hours'   : 0,
        'minutes' : 0,
        'seconds' : 0,
        # Atmospheric timestep [s]
        'dt_atmos': Settings.DtAtmosSec,
        # Calendar type; 'no_calendar' means day-count only (no months/years)
        'calendar': 'no_calendar',
    },

    # Atmosphere driver settings
    'atmosphere_nml': {
        # Interval between stdout diagnostic prints [s]
        'print_interval': 86400,
    },

    # FMS parallel I/O settings
    'fms_io_nml': {
        # Single-threaded writes avoid race conditions in parallel runs
        'threading_write': 'single',
        # Write a single output file instead of one per MPI rank
        'fileset_write'  : 'single',
    },

    # FMS framework settings
    'fms_nml': {
        # Print per-PE memory usage at each major step
        'print_memory_usage': True,
        # Stack memory [bytes] for domain-decomposition halo exchanges
        'domains_stack_size': 200000,
    },

    # Barotropic dynamical core
    # submodules/isca/src/atmos_spectral_barotropic/barotropic_dynamics.F90:150
    'barotropic_dynamics_nml': {
        # Use triangular (isotropic) spectral truncation instead of rhomboidal
        'triang_trunc'      : True,
        # Maximum retained zonal wavenumber; this is the T in TN truncation
        'num_fourier'       : Settings.FourierHarmonics,
        # Maximum retained total wavenumber; must equal num_fourier + 1 for triangular truncation
        'num_spherical'     : Settings.FourierHarmonics + 1,
        # Alias-free Gaussian grid dimensions (see alias_free_grid)
        'num_lat'           :  num_lat,
        'num_lon'           :  num_lon,
        # Step size when iterating over zonal wavenumbers m = 0, inc, 2*inc, ...
        # Set to 1 to retain all wavenumbers. Set to 2 to retain only even wavenumbers,
        # which enforces zonal symmetry (useful for hemispheric or symmetric experiments).
        'fourier_inc'       : 1,
        # How the hyperdiffusion coefficient scales with resolution.
        # 'resolution_dependent' rescales damping_coeff so the e-folding time at the
        # truncation wavenumber stays constant regardless of N; safe default for any resolution.
        'damping_option'    : 'resolution_dependent',
        # The hyperdiffusion operator is (-1)^(p+1) * coeff * nabla^(2p).
        # Order 2 gives del^4 (biharmonic), which damps small scales sharply while
        # leaving large scales almost untouched. Higher orders are even more selective.
        'damping_order'     : 2,
        # Strength of the hyperdiffusion applied to vorticity [1/s].
        # Sets the e-folding decay rate of the smallest retained wavenumber.
        # Too small: energy piles up at small scales and the model blows up.
        # Too large: you are effectively coarsening the resolution you paid for.
        'damping_coeff'     : 1.157e-4,
        # Linear drag coefficient [1/s] applied uniformly to all wavenumbers.
        # Unlike hyperdiffusion this damps large scales too; it acts like surface friction
        # and prevents unbounded acceleration of the zonal mean flow by the stirring.
        'damping_coeff_r'   : 1.929e-6,
        # Passive tracer advected in grid space using finite-volume advection.
        # More diffusive than the spectral tracer but conserves mass locally.
        'grid_tracer'       : True,
        # Passive tracer advected in spectral space using the same leapfrog scheme as vorticity.
        # Less diffusive than the grid tracer; useful for comparing transport schemes.
        'spec_tracer'       : True,
        # Zonal wavenumber of the initial vorticity perturbation added to the zonal flow.
        # m=6 gives a wave-6 pattern (~60 deg longitude per cycle), typical of mid-latitude eddies.
        # Only active when zeta_0 != 0.
        'm_0'               : 6,
        # Amplitude of the initial vorticity perturbation [1/s].
        # 0 means the run starts from a purely zonal flow with no wave activity;
        # any instability or wave growth must then be seeded by the stirring.
        'zeta_0'            : 0.0,
        # Latitude center of the initial vorticity perturbation [degrees N].
        'eddy_lat'          : 45.0,
        # Meridional Gaussian half-width of the initial vorticity perturbation [degrees].
        # Controls how meridionally confined the seed perturbation is.
        'eddy_width'        : 10.0,
        # Robert-Asselin filter coefficient for the leapfrog scheme.
        # The leapfrog timestep is unstable without this filter; it damps the spurious
        # computational mode that grows by decoupling odd and even timesteps.
        # Larger values damp more aggressively but reduce effective time accuracy.
        'robert_coeff'      : 0.04,
        # Initial zonal wind profile. 'zero' starts from rest so all circulation is
        # driven entirely by the stirring. 'two_jets' initializes mid-latitude jets.
        'initial_zonal_wind': 'zero',
    },

    # Barotropic physics (empty: no physical parameterizations active)
    # submodules/isca/src/atmos_spectral_barotropic/barotropic_physics.F90
    'barotropic_physics_nml': {},

    # Stochastic vorticity stirring (Vallis et al. 2004, doi:10.1175/1520-0469(2004)061<0264:AMASDM>2.0.CO;2)
    # submodules/isca/src/atmos_spectral_barotropic/stirring.F90:74
    'stirring_nml': {
        'decay_time': 172800,
        'amplitude' : Settings.StirringAmplitude,
        'lat0'      : 45.,
        'lon0'      : 180.,
        'widthy'    : 12.,
        'widthx'    : 45.,
        'B'         : Settings.StirringB,
    },
})

if __name__ == '__main__':
    cb.compile()
    exp.run(1, use_restart=False, num_cores=Settings.Cores)
    for i in range(2, Settings.Segments + 1):
        exp.run(i, num_cores=Settings.Cores)
