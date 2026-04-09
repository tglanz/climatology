# Barotropic Model Namelists

Each Fortran module declares its own namelist. At runtime the executable reads
`input.nml`, which the Python `Namelist` object generates from the dictionary
passed to `exp.namelist`. Parameters not listed in `input.nml` take the default
values declared in the Fortran source.

---

## main_nml

Source: `submodules/isca/src/atmos_solo/atmos_model.F90:111`

Top-level run control. Defines the integration length and timestep.

---

### dt_atmos

- **Description:** Atmospheric model timestep.
- **Type:** integer
- **Units:** seconds
- **Default:** 0 (must be set)
- **Notes:** The leapfrog scheme advances by `2 * dt_atmos` per step. Stability
  requires `dt_atmos` to be small relative to the fastest wave in the system.

---

### days

- **Description:** Number of days in the integration segment.
- **Type:** integer
- **Default:** 0

---

### hours

- **Description:** Additional hours beyond `days` in the integration length.
- **Type:** integer
- **Default:** 0

---

### minutes

- **Description:** Additional minutes beyond `hours` in the integration length.
- **Type:** integer
- **Default:** 0

---

### seconds

- **Description:** Additional seconds beyond `minutes` in the integration length.
- **Type:** integer
- **Default:** 0

---

### calendar

- **Description:** Calendar type used for date arithmetic.
- **Type:** character(len=17)
- **Default:** blank (must be set)
- **Possible values:**
  - `no_calendar` -- pure day-count with no months or years; used for idealized simulations
  - `thirty_day_months` -- every month has 30 days
  - `julian` -- standard Julian calendar
  - `noleap` -- 365-day year with no leap years

---

### current_date

- **Description:** Starting date of the run as an array `[year, month, day, hour, minute, second]`.
  Only relevant when a real calendar type is used.
- **Type:** integer(6)
- **Default:** `[0, 0, 0, 0, 0, 0]`

---

### current_time

- **Description:** Starting time as `[day, hour, minute, second]`. Alternative to
  `current_date` for calendar-free runs.
- **Type:** integer(4)
- **Default:** `[0, 0, 0, 0]`

---

### memuse_interval

- **Description:** Interval between memory usage reports, in timesteps.
- **Type:** integer
- **Default:** 72

---

### print_memuse

- **Description:** Whether to print memory usage statistics periodically.
- **Type:** logical
- **Default:** .true.

---

### atmos_nthreads

- **Description:** Number of OpenMP threads per MPI rank for the atmosphere.
- **Type:** integer
- **Default:** 1

---

## atmosphere_nml

Source: `submodules/isca/src/atmos_spectral_barotropic/atmosphere.F90:110`

Controls the atmosphere driver loop.

---

### print_interval

- **Description:** Interval between stdout diagnostic print statements from the
  atmosphere driver.
- **Type:** integer
- **Units:** seconds
- **Default:** 86400 (once per model day)

---

## fms_nml

Source: `submodules/isca/src/shared/fms/fms.F90:291`

Controls the FMS framework: parallelism, performance clocking, and memory diagnostics.

---

### print_memory_usage

- **Description:** If true, prints memory usage statistics at various points during
  the run. Useful for detecting memory leaks.
- **Type:** logical
- **Default:** .false.

---

### domains_stack_size

- **Description:** Size of the MPP_DOMAINS halo-exchange stack in words. Increase
  if the model crashes with a stack overflow during domain decomposition operations.
  Setting to 0 uses the MPP default.
- **Type:** integer
- **Units:** words (4 bytes each)
- **Default:** 0

---

### stack_size

- **Description:** Size of the MPP user stack in words. Setting to 0 uses the MPP
  default.
- **Type:** integer
- **Default:** 0

---

### read_all_pe

- **Description:** If true, all PEs read global input data and extract their local
  subdomain. If false, only PE 0 reads and broadcasts.
- **Type:** logical
- **Default:** .true.

---

### clock_grain

- **Description:** Level of detail for performance timing instrumentation.
- **Type:** character
- **Default:** `NONE`
- **Possible values:** `NONE`, `COMPONENT`, `SUBCOMPONENT`, `MODULE_DRIVER`,
  `MODULE`, `ROUTINE`, `LOOP`, `INFRA` (increasing detail)

---

### clock_flags

- **Description:** Controls synchronization behavior of performance clocks.
- **Type:** character
- **Default:** `NONE`
- **Possible values:**
  - `NONE` -- no synchronization
  - `SYNC` -- synchronize PEs at clock boundaries for accurate load balance measurement
  - `DETAILED` -- SYNC plus detailed MPI performance diagnostics

---

### warning_level

- **Description:** Controls what happens when `error_mesg` is called with the WARNING flag.
- **Type:** character
- **Default:** `warning`
- **Possible values:**
  - `warning` -- prints a message and continues
  - `fatal` -- treats warnings as fatal errors and aborts

---

### iospec_ieee32

- **Description:** IO spec flag passed to `open_ieee32_file`. Machine-specific;
  rarely needs changing.
- **Type:** character(len=64)
- **Default:** `-N ieee_32`

---

## fms_io_nml

Source: `submodules/isca/src/shared/fms/fms_io.F90:385`

Controls parallel file I/O behavior for restart and diagnostic output.

---

### threading_write

- **Description:** Threading mode for write operations.
- **Type:** character(len=32)
- **Default:** `multi`
- **Possible values:**
  - `single` -- only one thread writes; avoids race conditions; required for most setups
  - `multi` -- all threads write simultaneously

---

### threading_read

- **Description:** Threading mode for read operations.
- **Type:** character(len=32)
- **Default:** `multi`
- **Possible values:** `single`, `multi`

---

### fileset_write

- **Description:** Controls whether output is written to a single file or one file per MPI rank.
- **Type:** character(len=32)
- **Default:** `multi`
- **Possible values:**
  - `single` -- one shared output file; simpler post-processing
  - `multi` -- one file per MPI rank; may be needed at very large core counts

---

### fms_netcdf_override

- **Description:** If true, FMS overrides Fortran unformatted I/O with NetCDF for restart files.
- **Type:** logical
- **Default:** .true.

---

### fms_netcdf_restart

- **Description:** If true, restart files are written in NetCDF format.
- **Type:** logical
- **Default:** .true.

---

### format

- **Description:** Output file format.
- **Type:** character(len=32)
- **Default:** `netcdf`
- **Possible values:** `netcdf`, `native`

---

### max_files_w

- **Description:** Maximum number of simultaneously open output files.
- **Type:** integer
- **Default:** 40

---

### max_files_r

- **Description:** Maximum number of simultaneously open input files.
- **Type:** integer
- **Default:** 40

---

### time_stamp_restart

- **Description:** If true, restart filenames include a timestamp.
- **Type:** logical
- **Default:** .true.

---

### print_chksum

- **Description:** If true, prints checksums of restart fields for debugging.
- **Type:** logical
- **Default:** .false.

---

### checksum_required

- **Description:** If true, checksums are required when reading restart files and the
  run aborts if they do not match.
- **Type:** logical
- **Default:** .true.

---

### read_data_bug

- **Description:** Compatibility flag for a known bug in older FMS restart reads.
  Set to true only when reading restarts written by older model versions.
- **Type:** logical
- **Default:** .false.

---

## barotropic_dynamics_nml

Source: `submodules/isca/src/atmos_spectral_barotropic/barotropic_dynamics.F90:150`

Controls the spectral dynamical core: resolution, damping, initial conditions, and tracers.

---

### num_lat

- **Description:** Number of Gaussian latitude grid points. Together with `num_fourier`
  this sets the resolution. For triangular truncation TN, use `num_lat = (3*N + 1) / 2`
  (rounded up to even) and `num_lon = 2 * num_lat`.
- **Type:** integer
- **Default:** 128
- **Example values:** 32 (T21, ~600 km), 64 (T42, ~300 km), 128 (T85, ~150 km)

---

### num_lon

- **Description:** Number of longitude grid points. Should satisfy `num_lon >= 2 * num_fourier + 1`
  for alias-free transforms. Typically `num_lon = 2 * num_lat`.
- **Type:** integer
- **Default:** 256

---

### num_fourier

- **Description:** Maximum retained zonal wavenumber (the T in TN truncation).
- **Type:** integer
- **Default:** 85

---

### num_spherical

- **Description:** Maximum retained total wavenumber. For triangular truncation this
  must equal `num_fourier + 1`.
- **Type:** integer
- **Default:** 86

---

### fourier_inc

- **Description:** Increment between retained zonal wavenumbers. Setting to 1 retains
  all wavenumbers. Setting to 2 retains only even wavenumbers (imposes zonal symmetry).
- **Type:** integer
- **Default:** 1

---

### triang_trunc

- **Description:** If true, use triangular truncation (isotropic, retains all total
  wavenumbers up to N). If false, use rhomboidal truncation.
- **Type:** logical
- **Default:** .true.

---

### damping_option

- **Description:** How the hyperdiffusion coefficient is computed.
- **Type:** character(len=64)
- **Default:** `resolution_dependent`
- **Possible values:**
  - `resolution_dependent` -- coefficient is scaled automatically with the grid resolution
  - `order_dependent` -- coefficient is applied as given without rescaling

---

### damping_order

- **Description:** Order of the hyperdiffusion operator applied to vorticity. The
  operator is `(-1)^(p+1) * coeff * nabla^(2p)`, so order 2 is del^4 (biharmonic)
  and order 4 is del^8.
- **Type:** integer
- **Default:** 4
- **Typical values:** 2 (biharmonic), 4 (del^8)

---

### damping_coeff

- **Description:** Hyperdiffusion coefficient applied to vorticity. The effective
  e-folding time for the smallest retained wavenumber is approximately `1/damping_coeff`.
- **Type:** real
- **Units:** 1/s
- **Default:** 1e-4

---

### damping_coeff_r

- **Description:** Rayleigh (linear) drag coefficient. Applies a uniform linear drag
  `du/dt = -damping_coeff_r * u` to damp large-scale flow. Set to 0 to disable.
- **Type:** real
- **Units:** 1/s
- **Default:** 0.0

---

### robert_coeff

- **Description:** Robert-Asselin filter coefficient for the leapfrog time scheme.
  Damps the computational mode that arises from the three-level leapfrog scheme.
  Larger values damp more aggressively but reduce effective time accuracy.
- **Type:** real
- **Default:** 0.04
- **Typical range:** 0.01 to 0.1

---

### initial_zonal_wind

- **Description:** Profile of the initial zonal wind.
- **Type:** character(len=64)
- **Default:** `two_jets`
- **Possible values:**
  - `zero` -- start from rest; no initial mean flow
  - `two_jets` -- two mid-latitude jets defined by
    `u = 25*cos(lat) - 30*cos^3(lat) + 300*sin^2(lat)*cos^6(lat)`

---

### zeta_0

- **Description:** Amplitude of the initial vorticity perturbation superimposed on
  the initial zonal wind. Set to 0 to start from a purely zonal flow.
- **Type:** real
- **Units:** 1/s
- **Default:** 8e-5

---

### m_0

- **Description:** Zonal wavenumber of the initial vorticity perturbation.
- **Type:** integer
- **Default:** 4

---

### eddy_lat

- **Description:** Latitude of the center of the initial vorticity perturbation.
- **Type:** real
- **Units:** degrees North
- **Default:** 45.0

---

### eddy_width

- **Description:** Meridional half-width (Gaussian sigma) of the initial vorticity
  perturbation.
- **Type:** real
- **Units:** degrees
- **Default:** 15.0

---

### spec_tracer

- **Description:** If true, activate the spectral passive tracer advected using the
  leapfrog scheme. Output field: `trs`.
- **Type:** logical
- **Default:** .true.

---

### grid_tracer

- **Description:** If true, activate the grid-space passive tracer advected using
  finite-volume advection. Output field: `tr`.
- **Type:** logical
- **Default:** .true.

---

### cutoff_wn

- **Description:** Total wavenumber below which the resolution-dependent damping
  coefficient is held constant (not scaled). Only used when
  `damping_option = resolution_dependent`.
- **Type:** integer
- **Default:** 30

---

### valid_range_v

- **Description:** Allowable range of the meridional wind. If any grid point exceeds
  this range the model aborts with a FATAL error. Used to detect numerical instability.
- **Type:** real(2)
- **Units:** m/s
- **Default:** -1000.0 to 1000.0

---

### south_to_north

- **Description:** If true, latitudes are ordered from south to north in the grid
  arrays. Changing this is not normally needed.
- **Type:** logical
- **Default:** .true.

---

### longitude_origin

- **Description:** Longitude of the first grid point.
- **Type:** real
- **Units:** degrees East
- **Default:** 0.0

---

### check_fourier_imag

- **Description:** If true, check that the imaginary part of the m=0 Fourier
  coefficient is zero (as it should be by symmetry). A debug option.
- **Type:** logical
- **Default:** .false.

---

## barotropic_physics_nml

Source: `submodules/isca/src/atmos_spectral_barotropic/barotropic_physics.F90:85`

The physics module is a stub in the barotropic model. No physical parameterizations
are active and the only namelist parameter is a placeholder.

---

### empty

- **Description:** Placeholder parameter with no effect. The namelist exists so that
  the FMS namelist-read machinery does not error when `barotropic_physics_nml` is
  absent from `input.nml`.
- **Type:** logical
- **Default:** undefined (never read by any code path)

---

## stirring_nml

Source: `submodules/isca/src/atmos_spectral_barotropic/stirring.F90:74`

Controls the stochastic vorticity stirring scheme described in Vallis et al. (2004),
doi:10.1175/1520-0469(2004)061<0264:AMASDM>2.0.CO;2. The stirring is an AR(1)
process in spectral space, localized in physical space by a Gaussian envelope.

---

### amplitude

- **Description:** Overall amplitude of the stochastic stirring forcing. Set to 0 to
  disable stirring entirely (the module then does nothing after initialization).
- **Type:** real
- **Units:** 1/s^2
- **Default:** 0.0

---

### decay_time

- **Description:** Decorrelation (e-folding) time of the AR(1) stirring process.
  Controls how quickly the stirring pattern changes. The AR(1) coefficients are
  `a = sqrt(1 - exp(-2*dt/decay_time))` and `b = exp(-dt/decay_time)`.
- **Type:** real
- **Units:** seconds
- **Default:** 2*86400 (2 days)

---

### lat0

- **Description:** Central latitude of the Gaussian meridional envelope. The stirring
  is strongest at this latitude and decays with Gaussian half-width `widthy`.
- **Type:** real
- **Units:** degrees North
- **Default:** 45.0

---

### widthy

- **Description:** Meridional half-width (Gaussian sigma) of the stirring envelope.
  Controls how meridionally broad the forcing region is.
- **Type:** real
- **Units:** degrees
- **Default:** 12.0

---

### B

- **Description:** Zonal asymmetry parameter. When B = 0 the stirring envelope is
  purely meridional (zonally uniform). When B > 0 the stirring is additionally
  localized in longitude around `lon0` with half-width `widthx`. The local amplitude
  is `amplitude * (1 + B * exp(-0.5 * ((lon - lon0) / widthx)^2))`.
- **Type:** real
- **Default:** 0.0 (zonally uniform)
- **Typical values:** 0.0 (uniform), 1.0 (moderate zonal localization)

---

### lon0

- **Description:** Central longitude of the zonal stirring envelope. Only active
  when B != 0.
- **Type:** real
- **Units:** degrees East
- **Default:** 180.0

---

### widthx

- **Description:** Zonal half-width (Gaussian sigma) of the stirring envelope. Only
  active when B != 0.
- **Type:** real
- **Units:** degrees
- **Default:** 45.0

---

### do_localize

- **Description:** If true, apply the spatial (lat/lon) localization envelope to the
  stirring. If false, the stirring is applied globally with uniform amplitude.
- **Type:** logical
- **Default:** .true.

---

### n_total_forcing_max

- **Description:** Upper bound on the total spherical wavenumber (m+n) of the forced
  modes. Only modes with `n_total_forcing_min < m+n < n_total_forcing_max` are stirred.
- **Type:** integer
- **Default:** 15

---

### n_total_forcing_min

- **Description:** Lower bound on the total spherical wavenumber (m+n) of the forced
  modes. Only modes with `n_total_forcing_min < m+n < n_total_forcing_max` are stirred.
- **Type:** integer
- **Default:** 9

---

### zonal_forcing_min

- **Description:** Minimum zonal wavenumber m of the forced modes. Only modes with
  `m > zonal_forcing_min` are stirred, subject to the total wavenumber constraints.
  This excludes the zonal mean and the lowest wavenumbers from being directly forced.
- **Type:** integer
- **Default:** 3
