# Barotropic Model Diagnostic Fields

Diagnostic fields are registered in the Fortran source via `register_diag_field` and
`register_static_field`. The DiagTable in the experiment script acts as a filter that
selects which registered fields to write and at what averaging frequency.

Fields not listed in the DiagTable are still computed internally but are never written
to disk.

---

## Module: barotropic_diagnostics

Source: `submodules/isca/src/atmos_spectral_barotropic/barotropic_diagnostics.F90`

All fields in this module are on the 2D (lon, lat) grid.

---

### ucomp

- **Description:** Zonal (east-west) wind component. Derived from the streamfunction
  at each timestep via `u = -dpsi/dy`. Not a prognostic variable; computed from the
  vorticity field.
- **Units:** m/s
- **Typical range:** -100 to 100 m/s depending on forcing configuration
- **Source line:** barotropic_diagnostics.F90:104

---

### vcomp

- **Description:** Meridional (north-south) wind component. Derived from the
  streamfunction at each timestep via `v = dpsi/dx`. Not a prognostic variable.
- **Units:** m/s
- **Typical range:** -100 to 100 m/s
- **Source line:** barotropic_diagnostics.F90:105

---

### vor

- **Description:** Relative vorticity, defined as `zeta = dv/dx - du/dy`. This is
  the actual prognostic variable of the barotropic vorticity equation. The model
  time-steps this field directly in spectral space.
- **Units:** 1/s
- **Typical range:** -1e-4 to 1e-4 s^-1 in mid-latitude flows
- **Source line:** barotropic_diagnostics.F90:106

---

### pv

- **Description:** Absolute vorticity, defined as `f + zeta`, where `f = 2*Omega*sin(lat)`
  is the Coriolis parameter and `zeta` is the relative vorticity. On a barotropic sphere
  this is equivalent to the shallow-water potential vorticity when layer depth is uniform.
  Sometimes loosely called "pv" but it is not Ertel potential vorticity.
- **Units:** 1/s
- **Typical range:** 1e-5 to 2e-4 s^-1 (dominated by f at most latitudes)
- **Source line:** barotropic_diagnostics.F90:107

---

### stream

- **Description:** Streamfunction psi, related to vorticity by the Poisson equation
  `nabla^2 psi = zeta`. Wind components follow as `u = -dpsi/dy`, `v = dpsi/dx`.
  Computed by applying the inverse Laplacian to the vorticity in spectral space.
- **Units:** m^2/s
- **Typical range:** -1e7 to 1e7 m^2/s
- **Source line:** barotropic_diagnostics.F90:108

---

### trs

- **Description:** Spectral tracer. A passive scalar advected using the same spectral
  leapfrog scheme as the vorticity. Initialized with a step function: value 1 between
  10 and 20 degrees N, value -1 poleward of 70 degrees N, zero elsewhere.
  Enabled by `spec_tracer = True` in `barotropic_dynamics_nml`.
- **Units:** dimensionless
- **Typical range:** -1 to 1 (set by initial condition; diffuses with time)
- **Source line:** barotropic_diagnostics.F90:109

---

### tr

- **Description:** Grid tracer. A passive scalar advected using finite-volume advection
  in grid space (the `a_grid_horiz_advection` scheme). Uses the same initial condition
  as `trs`. Enabled by `grid_tracer = True` in `barotropic_dynamics_nml`. Compared with
  `trs` to evaluate the difference between spectral and grid-space transport schemes.
- **Units:** dimensionless
- **Typical range:** -1 to 1 (set by initial condition; diffuses with time)
- **Source line:** barotropic_diagnostics.F90:110

---

### eddy_vor

- **Description:** Eddy vorticity, defined as the relative vorticity with the zonal mean
  removed. Computed by zeroing the m=0 spectral coefficient of vorticity before
  transforming to grid space. Isolates the wave component of the flow.
- **Units:** 1/s
- **Typical range:** -1e-4 to 1e-4 s^-1
- **Source line:** barotropic_diagnostics.F90:111

---

### delta_u

- **Description:** Change in the zonal-mean zonal wind from the initial profile,
  defined as `u_bar(lat,t) - u_init(lat)`. Measures how the zonal-mean circulation
  has been accelerated or decelerated by the eddy forcing over time.
- **Units:** m/s
- **Typical range:** -50 to 50 m/s over a model year
- **Source line:** barotropic_diagnostics.F90:112

---

## Module: stirring_mod

Source: `submodules/isca/src/atmos_spectral_barotropic/stirring.F90`

---

### stirring

- **Description:** Instantaneous stirring forcing in grid space. This is the vorticity
  tendency contributed by the stochastic stirring at the current timestep, after applying
  the spatial localization envelope. Written as a time average over the output interval.
  Implements equation A.6 of Vallis et al. (2004).
- **Units:** 1/s^2
- **Typical range:** -1e-10 to 1e-10 s^-2 for typical amplitude settings
- **Type:** time-averaged diagnostic field
- **Source line:** stirring.F90:168

---

### stirring_amp

- **Description:** Spatial amplitude envelope of the stirring, defined as
  `amplitude * localize(lon, lat)`. This is a static (time-invariant) field written
  once at initialization. It shows the geographic distribution of stirring intensity.
  When `B = 0` the envelope is purely meridional (Gaussian in latitude). When `B > 0`
  it is also localized in longitude around `lon0`.
- **Units:** dimensionless (the amplitude parameter itself carries units of 1/s^2)
- **Type:** static field, written once at run start
- **Source line:** stirring.F90:167

---

### stirring_sqr

- **Description:** Time-mean of the squared stirring forcing, `mean(stirring^2)`,
  accumulated over all timesteps and written at the end of the run. Proportional to
  the variance of the stochastic forcing and used to characterize the energy injection
  rate of the stirring.
- **Units:** 1/s^4
- **Type:** static field, written once at run end
- **Source line:** stirring.F90:166
