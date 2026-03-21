# Running the Barotropic Vorticity Equation with Stirring in Isca

This document is specific to the [barotropic](#barotropic) vorticity equation (BVE) with
[stochastic stirring](#stochastic-stirring). For general Isca setup, installation, and
environment configuration refer to the official documentation:
https://execlim.github.io/Isca/

---

## Overview

Isca includes a spectral barotropic model that [integrates](#numerical-integration) the
[non-divergent](#non-divergent-flow) [barotropic](#barotropic) vorticity equation on
the sphere:

$$\frac{\partial \zeta}{\partial t} + \mathbf{u} \cdot \nabla(\zeta + f) = D(\zeta) + S$$

**Variables and terms:**

| Symbol | Name | Description |
|---|---|---|
| $\zeta$ | [Relative vorticity](#vorticity) | The local rotation of the fluid relative to Earth's surface (s$^{-1}$). This is the primary prognostic variable -- the quantity the model steps forward in time. |
| $t$ | Time | Continuous time (s). |
| $\frac{\partial \zeta}{\partial t}$ | Local tendency | Rate of change of vorticity at a fixed point in space. The model computes this from the right-hand side and advances it with the [leapfrog scheme](#leapfrog-scheme). |
| $\mathbf{u} = (u, v)$ | Horizontal velocity | Zonal ($u$, eastward) and meridional ($v$, northward) wind components (m s$^{-1}$). Derived at each step from $\zeta$ via the [streamfunction](#streamfunction). |
| $\nabla$ | Horizontal gradient operator | $\nabla = (\partial/\partial x,\, \partial/\partial y)$ on the sphere. |
| $\mathbf{u} \cdot \nabla(\zeta + f)$ | Advection of absolute vorticity | The transport of [absolute vorticity](#vorticity) $\zeta + f$ by the flow. This is the nonlinear term: it moves vorticity around without creating or destroying it, and it drives the formation of jets and eddies. |
| $f = 2\Omega\sin\phi$ | [Coriolis parameter](#coriolis-parameter) | Planetary vorticity at latitude $\phi$. It varies with latitude but not with time, so $\nabla f = \partial f/\partial y \neq 0$ -- this latitudinal gradient is what allows Rossby waves to exist. |
| $\zeta + f$ | Absolute vorticity | Total vorticity of a fluid parcel including Earth's rotation. Conserved following a parcel when $D = 0$ and $S = 0$. |
| $D(\zeta)$ | [Spectral hyperdiffusion](#spectral-hyperdiffusion) | A scale-selective dissipation operator that removes energy from the smallest resolved scales. Necessary to prevent grid-scale noise from accumulating. |
| $S$ | [Stochastic stirring](#stochastic-stirring) | A spatially localized, temporally correlated random forcing applied in spectral space. Represents the injection of vorticity by processes not explicitly modeled (e.g., baroclinic instability). |

The left-hand side $\frac{\partial \zeta}{\partial t} + \mathbf{u} \cdot \nabla(\zeta + f)$ is
the material derivative of absolute vorticity -- the rate of change following a fluid parcel.
In the absence of forcing and dissipation ($D = S = 0$), this equals zero, meaning absolute
vorticity is conserved along parcel trajectories. This conservation law is what constrains
the large-scale flow and drives the Rossby wave dynamics the model is designed to study.

The model is [non-divergent](#non-divergent-flow) by construction: the wind field is derived
from a [streamfunction](#streamfunction) $\psi$ such that $\zeta = \nabla^2 \psi$, meaning
only one scalar field is needed to describe the full flow.

Time integration uses a [leapfrog scheme](#leapfrog-scheme) with a
[Robert-Asselin filter](#robert-asselin-filter).

---

## Relevant Source Files

All barotropic model source lives under `src/atmos_spectral_barotropic/`:

| File | Role |
|---|---|
| `atmosphere.F90` | Top-level coupler; calls dynamics, physics, diagnostics |
| `barotropic_dynamics.F90` | Spectral time-stepping of $\zeta$; initial conditions |
| `barotropic_physics.F90` | Physics interface (empty by default) |
| `barotropic_diagnostics.F90` | Registers and outputs diagnostic fields |
| `stirring.F90` | [Stochastic stirring](#stochastic-stirring) (Vallis et al. 2004) |

The compiled source list is at `src/extra/model/barotropic/path_names`.

The reference test case with stirring is:

```
exp/test_cases/barotropic_vorticity_equation/barotropic_vor_eq_stirring_test.py
```

---

## Setup and Installation

For full installation instructions see https://execlim.github.io/Isca/.

> If running inside the `sim` devcontainer, steps 1-3 below are handled automatically
> at container creation: the conda environment is created, the `isca` Python package is
> installed, and all environment variables are set. Skip directly to step 4 to verify.

### 1. Create the Isca conda environment

```bash
conda env create -f submodules/isca/ci/environment-py.yml
conda activate isca_env
```

This installs all required dependencies: `gfortran`, `openmpi`, `netcdf-fortran`,
`numpy`, `xarray`, `pandas`, `f90nml`, `jinja2`, `sh`, and `tqdm`.

### 2. Install the Isca Python package

```bash
cd submodules/isca/src/extra/python
pip install -e .
```

The `-e` flag installs in editable mode: changes to the source are immediately
reflected without reinstalling.

### 3. Set required environment variables

Add these to your `~/.bashrc` so they persist across sessions:

```bash
# Root of the Isca source tree
export GFDL_BASE=/path/to/climatology/submodules/isca

# Selects the compiler env file from $GFDL_BASE/src/extra/env/
# 'ubuntu_conda' is appropriate for Linux + conda + gfortran
export GFDL_ENV=ubuntu_conda

# Where compiled binaries and run directories are written
export GFDL_WORK=/path/to/isca_work

# Where completed run output is stored
export GFDL_DATA=/path/to/isca_data
```

Then reload:

```bash
source ~/.bashrc
```

`GFDL_BASE` and `GFDL_ENV` are required at import time by the `isca` Python package.
`GFDL_WORK` and `GFDL_DATA` control where compiled code and model output land.

The env files in `$GFDL_BASE/src/extra/env/` set compiler variables (`F90=mpifort`,
`CC=mpicc`) and the Makefile template. For HPC clusters a different env file is
typically needed -- see `src/extra/env/` for available options.

### 4. Verify

```bash
python -c "from isca import BarotropicCodeBase; print('OK')"
```

---

## Running the Test Case

The experiment script is at `sim/example_barotropic_stirring.py`. Run it with:

```bash
conda activate isca_env
python sim/example_barotropic_stirring.py
```

The script automatically detects the number of available CPUs and rounds down to the
nearest power of 2 (the requirement imposed by Isca's MPI domain decomposition).

`cb.compile()` compiles to `$GFDL_WORK/codebase`. Subsequent runs reuse the compiled
binary unless recompilation is requested.

---

## Namelist Parameters

All namelists are passed as a dict to `Experiment.namelist`.

### `main_nml` -- Integration control

| Parameter | Type | Default | Description |
|---|---|---|---|
| `days` | int | -- | Run segment length in days |
| `hours` | int | -- | Additional hours |
| `minutes` | int | -- | Additional minutes |
| `seconds` | int | -- | Additional seconds |
| `dt_atmos` | int (s) | -- | Model time step in seconds |
| `calendar` | str | -- | Use `'no_calendar'` for the barotropic model |

### `barotropic_dynamics_nml` -- Spectral dynamics

Source: `barotropic_dynamics.F90`, lines 119-160.

**Grid and spectral resolution**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `num_lat` | int | 128 | Number of Gaussian latitude grid points |
| `num_lon` | int | 256 | Number of longitude grid points |
| `num_fourier` | int | 85 | Maximum retained zonal [wavenumber](#spherical-harmonics-and-spectral-truncation) $m_{\max}$ |
| `num_spherical` | int | 86 | Maximum retained total wavenumber index ($= m_{\max} + 1$ for [triangular truncation](#spherical-harmonics-and-spectral-truncation)) |
| `fourier_inc` | int | 1 | Zonal wavenumber increment (1 = no skip) |
| `triang_trunc` | bool | `.true.` | Use [triangular truncation](#spherical-harmonics-and-spectral-truncation) |

The test case uses T85 resolution (128 Gaussian latitudes, 256 longitudes).

**Diffusion**

The model applies [spectral hyperdiffusion](#spectral-hyperdiffusion) of the form
$D(\zeta) = -\nu (-\nabla^2)^p \zeta$ where $p$ is `damping_order`.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `damping_option` | str | `'resolution_dependent'` | Diffusion scheme. `'resolution_dependent'` scales the coefficient with resolution |
| `damping_order` | int | 4 | Order $p$ of hyperdiffusion ($p=1$: Laplacian, $p=2$: biharmonic, etc.) |
| `damping_coeff` | real (s$^{-1}$) | `1e-4` | Hyperdiffusion coefficient $\nu$ |
| `damping_coeff_r` | real (s$^{-1}$) | `0.0` | Linear (Rayleigh) drag coefficient; applied at all wavenumbers |

The stirring test case uses `damping_order=2` and `damping_coeff_r=1.929e-6`
(a weak linear drag with timescale $\approx 6$ days) to prevent the zonal-mean flow
from growing without bound.

**Time filter**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `robert_coeff` | real | `0.04` | [Robert-Asselin filter](#robert-asselin-filter) coefficient for the leapfrog scheme |

**Initial conditions**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `initial_zonal_wind` | str | `'two_jets'` | `'two_jets'`: analytic two-jet profile; `'zero'`: no initial mean flow |
| `zeta_0` | real (s$^{-1}$) | `8e-5` | Amplitude of the superimposed initial [vorticity](#vorticity) perturbation |
| `m_0` | int | 4 | Zonal [wavenumber](#spherical-harmonics-and-spectral-truncation) of the initial vorticity perturbation |
| `eddy_lat` | real (deg) | 45.0 | Latitude of the initial vorticity perturbation |
| `eddy_width` | real (deg) | 15.0 | Meridional Gaussian half-width of the initial perturbation |

Set `zeta_0=0.0` for a purely zonal initial state with no perturbation.

**Passive tracers**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `spec_tracer` | bool | `.true.` | Advect a passive tracer in spectral space |
| `grid_tracer` | bool | `.true.` | Advect a passive tracer in grid space |

Both tracers are initialized to $+1$ between 10-20 N and $-1$ poleward of 70 N.

---

### `stirring_nml` -- Stochastic vorticity forcing

Source: `stirring.F90`.

The stirring scheme follows Vallis et al. (2004), equation A.6. At each time step, the
spectral stirring field is updated as an [AR(1) process](#ar1-process):

$$S^{n+1} = e^{-\Delta t/\tau} \, S^n + A \sqrt{1 - e^{-2\Delta t/\tau}} \, \xi^n$$

where $\tau$ is `decay_time`, $A$ is `amplitude`, and $\xi^n$ is white noise in
[spectral space](#spherical-harmonics-and-spectral-truncation). The forcing is then
localized in physical space by a Gaussian envelope before being transformed back to
spectral space and added to $\partial\zeta/\partial t$.

**Reference:** Vallis, G. K., Gerber, E. P., Kushner, P. J., & Cash, B. A. (2004).
A mechanism and simple dynamical model of the North Atlantic Oscillation and annular modes.
*Journal of the Atmospheric Sciences*, 61(3), 264-280.
https://doi.org/10.1175/1520-0469(2004)061<0264:AMASDM>2.0.CO;2

| Parameter | Type | Default | Description |
|---|---|---|---|
| `amplitude` | real (s$^{-2}$) | `0.0` | Forcing amplitude $A$. **Must be non-zero** to activate stirring |
| `decay_time` | real (s) | `172800` (2 days) | e-folding timescale $\tau$ of the [AR(1) process](#ar1-process); controls temporal correlation of the forcing |
| `lat0` | real (deg) | `45.0` | Central latitude of the meridional Gaussian localization |
| `widthy` | real (deg) | `12.0` | Meridional Gaussian half-width of the localization |
| `lon0` | real (deg) | `180.0` | Central longitude for zonal localization (only active when `B != 0`) |
| `widthx` | real (deg) | `45.0` | Zonal Gaussian half-width (only active when `B != 0`) |
| `B` | real | `0.0` | Zonal modulation amplitude. `B=0`: forcing is zonally uniform; `B>0`: applies a zonal Gaussian of amplitude $B$ centered at `lon0` |
| `do_localize` | bool | `.true.` | If `.false.`, the forcing is applied uniformly everywhere with no spatial envelope |
| `n_total_forcing_min` | int | `9` | Only modes with total wavenumber $m+n >$ this value are forced |
| `n_total_forcing_max` | int | `15` | Only modes with total wavenumber $m+n <$ this value are forced |
| `zonal_forcing_min` | int | `3` | Only modes with zonal wavenumber $m >$ this value are forced |

The wave mask selects spectral modes satisfying all three conditions simultaneously:
$m > 3$, $m+n > 9$, $m+n < 15$. This targets synoptic-scale eddies and excludes the
largest scales and the zonal mean.

The test case value `amplitude=3e-11` with `decay_time=172800` (2 days) produces
moderate mid-latitude stirring at T85.

---

### `fms_nml` -- FMS runtime settings

| Parameter | Type | Description |
|---|---|---|
| `print_memory_usage` | bool | Print memory usage to log |
| `domains_stack_size` | int | Stack size for domain decomposition; increase if the model aborts with a stack error |

### `fms_io_nml` -- I/O settings

| Parameter | Type | Description |
|---|---|---|
| `threading_write` | str | `'single'`: one process writes output |
| `fileset_write` | str | `'single'`: write a single output file, not one per MPI rank |

---

## Diagnostics

Diagnostics are registered via `DiagTable`. Fields from two modules are available.

### `barotropic_diagnostics`

| Field | Units | Description |
|---|---|---|
| `ucomp` | m s$^{-1}$ | Zonal wind $u$ |
| `vcomp` | m s$^{-1}$ | Meridional wind $v$ |
| `vor` | s$^{-1}$ | [Relative vorticity](#vorticity) $\zeta$ |
| `pv` | s$^{-1}$ | [Absolute vorticity](#vorticity) $\zeta + f$ (labeled `pv` in the barotropic context) |
| `stream` | m$^2$ s$^{-1}$ | [Streamfunction](#streamfunction) $\psi$ |
| `trs` | -- | Spectral passive tracer |
| `tr` | -- | Grid-space passive tracer |
| `eddy_vor` | s$^{-1}$ | Non-zonal (eddy) component of $\zeta$ |
| `delta_u` | m s$^{-1}$ | Change in zonal-mean zonal wind from initial state |

### `stirring_mod`

| Field | Units | Description |
|---|---|---|
| `stirring` | s$^{-2}$ | Instantaneous stirring field $S$ in grid space |
| `stirring_amp` | -- | Spatial amplitude envelope of the stirring |
| `stirring_sqr` | s$^{-4}$ | Time-mean of $S^2$ over the full integration |

Example diagnostic table configuration:

```python
diag = DiagTable()
diag.add_file('atmos_monthly', 30, 'days', time_units='days')

diag.add_field('barotropic_diagnostics', 'ucomp',    time_avg=True)
diag.add_field('barotropic_diagnostics', 'vcomp',    time_avg=True)
diag.add_field('barotropic_diagnostics', 'vor',      time_avg=True)
diag.add_field('barotropic_diagnostics', 'pv',       time_avg=True)
diag.add_field('barotropic_diagnostics', 'stream',   time_avg=True)
diag.add_field('barotropic_diagnostics', 'eddy_vor', time_avg=True)
diag.add_field('stirring_mod',           'stirring', time_avg=True)

exp.diag_table = diag
```

---

## Inspecting Output

Output is written to `$GFDL_DATA/<experiment_name>/` as NetCDF files, one per segment.
For the example script the path is:

```
$GFDL_DATA/barotropic_stirring/run0001/atmos_monthly.nc
$GFDL_DATA/barotropic_stirring/run0002/atmos_monthly.nc
...
```

### Quick inspection with ncdump

`ncdump` (provided by the `netcdf-bin` package) lets you inspect a file without writing
any code.

```bash
# Show dimensions, variables, and global attributes
ncdump -h $GFDL_DATA/barotropic_stirring/run0001/atmos_monthly.nc

# Dump values of a specific variable
ncdump -v vor $GFDL_DATA/barotropic_stirring/run0001/atmos_monthly.nc
```

### Loading with xarray

xarray is the standard way to work with Isca output in Python. It understands NetCDF
dimensions and coordinates natively.

```python
import xarray as xr
import os

data_dir = os.path.join(os.environ['GFDL_DATA'], 'barotropic_stirring')

# Load a single segment
ds = xr.open_dataset(f'{data_dir}/run0001/atmos_monthly.nc')
print(ds)

# Load all segments at once along the time dimension
ds = xr.open_mfdataset(f'{data_dir}/run*/atmos_monthly.nc', combine='by_coords')
```

The dataset will have dimensions `(time, lat, lon)` and variables matching what was
registered in the `DiagTable`.

### Basic plots with matplotlib

```python
import matplotlib.pyplot as plt

# Time-mean relative vorticity
vor_mean = ds['vor'].mean('time')

fig, ax = plt.subplots()
vor_mean.plot(ax=ax, cmap='RdBu_r')
ax.set_title('Time-mean relative vorticity')
plt.show()

# Zonal-mean zonal wind evolution over time
u_zonal = ds['ucomp'].mean('lon')
u_zonal.plot(x='time', y='lat', cmap='RdBu_r')
plt.show()
```

### Checking for problems

Before analysing results it is worth verifying the output is physically reasonable:

```python
import numpy as np

# Vorticity should be O(1e-5) to O(1e-4) s^-1 in mid-latitudes
print(ds['vor'].max().values, ds['vor'].min().values)

# NaN values indicate the model blew up
assert not ds['vor'].isnull().any(), "NaN detected in vorticity output"

# delta_u shows how much the zonal-mean wind has changed from the initial state
ds['delta_u'].mean('lon').plot(x='time', y='lat')
```

---

## References

- Vallis, G. K., Gerber, E. P., Kushner, P. J., & Cash, B. A. (2004). A mechanism and
  simple dynamical model of the North Atlantic Oscillation and annular modes.
  *Journal of the Atmospheric Sciences*, 61(3), 264-280.
  https://doi.org/10.1175/1520-0469(2004)061<0264:AMASDM>2.0.CO;2

- Isca documentation: https://execlim.github.io/Isca/

- Isca source repository: https://github.com/ExeClim/Isca

---

## Glossary

### Barotropic

A fluid is barotropic when its density depends only on pressure, not on temperature or
other thermodynamic variables. In practice for atmospheric modeling, this means the
flow has no vertical structure: wind speed and direction are the same at every altitude.

The barotropic model is a drastic simplification of the real atmosphere. Its value is
that it isolates purely horizontal, depth-averaged dynamics. Because the flow is
two-dimensional and [non-divergent](#non-divergent-flow), a single scalar field -- the
[vorticity](#vorticity), or equivalently the [streamfunction](#streamfunction) -- completely
describes the state. This makes it computationally cheap and analytically tractable,
which is why it has been widely used to study jet streams, Rossby waves, and large-scale
turbulence.

The opposite of barotropic is **baroclinic**: a flow in which density varies with both
pressure and temperature, producing vertical wind shear. The real atmosphere is
baroclinic, and baroclinic instability is the primary mechanism producing mid-latitude
weather systems.

---

### Vorticity

Vorticity is a measure of local rotation in a fluid. For a two-dimensional horizontal
flow with velocity $(u, v)$, the vertical component of vorticity is:

$$\zeta = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}$$

Positive $\zeta$ means counterclockwise rotation (cyclonic in the Northern Hemisphere),
negative means clockwise (anticyclonic).

**Relative vorticity** ($\zeta$) measures rotation relative to the Earth's surface.

**Absolute vorticity** ($\zeta + f$) adds the vorticity due to Earth's own rotation
(the [Coriolis parameter](#coriolis-parameter) $f$). This is what is conserved
following a fluid parcel in the frictionless, non-divergent barotropic model. In the
Isca diagnostics it is labeled `pv` (potential vorticity), which in the barotropic
context reduces to absolute vorticity.

In terms of scale: a strong mid-latitude cyclone has $\zeta \sim 10^{-4}$ s$^{-1}$,
the Coriolis parameter at 45 N is $f \approx 10^{-4}$ s$^{-1}$, and the initial
vorticity perturbation `zeta_0=8e-5` in the test case is of comparable magnitude.

---

### Coriolis Parameter

The Coriolis effect arises because the Earth is a rotating reference frame. Any object
moving horizontally on Earth's surface is deflected -- to the right in the Northern
Hemisphere, to the left in the Southern -- because the ground itself is rotating beneath it.

The **Coriolis parameter** $f$ quantifies the local strength of this effect:

$$f = 2\Omega\sin\phi$$

where $\Omega = 7.292 \times 10^{-5}$ rad s$^{-1}$ is Earth's rotation rate and $\phi$
is latitude. It is zero at the equator, positive in the Northern Hemisphere, and negative
in the Southern Hemisphere. At 45 N, $f \approx 1.03 \times 10^{-4}$ s$^{-1}$.

In the barotropic model, $f$ appears as the planetary vorticity. The conserved quantity
following fluid parcels is absolute vorticity $\zeta + f$: if a parcel moves poleward
(where $f$ increases), $\zeta$ must decrease to compensate, which is the mechanism
behind Rossby wave propagation.

---

### Streamfunction

When a flow is [non-divergent](#non-divergent-flow) ($\nabla \cdot \mathbf{u} = 0$),
the entire wind field can be described by a single scalar function $\psi$ called the
streamfunction:

$$u = -\frac{\partial \psi}{\partial y}, \qquad v = \frac{\partial \psi}{\partial x}$$

Contours of constant $\psi$ are streamlines -- lines that the flow is parallel to.
High-pressure systems correspond to $\psi$ maxima (anticyclonic circulation), and
low-pressure systems to $\psi$ minima (cyclonic circulation).

The relationship between streamfunction and [vorticity](#vorticity) is a Poisson equation:

$$\zeta = \nabla^2 \psi$$

This is what makes the spectral approach natural: in spectral space, $\nabla^2$
becomes a simple multiplication by $-n(n+1)/a^2$ (where $n$ is the total spherical
harmonic wavenumber and $a$ is Earth's radius), so inverting from $\zeta$ to $\psi$
is algebraically trivial. Isca uses this to compute `stream` in the diagnostics.

---

### Non-Divergent Flow

A flow is non-divergent when:

$$\nabla \cdot \mathbf{u} = \frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = 0$$

This means there is no net convergence or divergence of mass at any point. In a
two-dimensional non-divergent flow, air columns neither expand nor contract horizontally,
which rules out gravity waves and acoustic waves. The barotropic model enforces this
constraint exactly. The consequence is that the flow can be represented entirely by the
[streamfunction](#streamfunction), reducing the state from two fields ($u$, $v$) to one
scalar ($\psi$ or equivalently $\zeta$).

---

### Numerical Integration

In the context of this model, "integration" means advancing the equations of motion
forward in time on a computer. Given the state of the atmosphere at time $t$ (the
[vorticity](#vorticity) field $\zeta$), the model computes $\partial\zeta/\partial t$
from the governing equation and steps forward by a small time increment $\Delta t$
(`dt_atmos`). This is repeated thousands of times to simulate days or months of
atmospheric evolution.

The barotropic model uses a [leapfrog scheme](#leapfrog-scheme) for this purpose.
Because the equations are nonlinear and include [stochastic stirring](#stochastic-stirring),
small errors accumulate over time -- the simulation is not expected to reproduce any
specific real atmospheric trajectory, but rather to produce statistically representative
behavior.

---

### Spectral Hyperdiffusion

Diffusion smooths out small-scale noise by removing energy from small spatial scales.
In a spectral model, this is applied directly in spectral space for efficiency and
precision.

**Hyperdiffusion** is an extension of ordinary diffusion using higher powers of the
Laplacian $\nabla^2$:

$$D(\zeta) = -\nu \, (-\nabla^2)^p \, \zeta$$

where $p$ is the order (`damping_order`) and $\nu$ is the coefficient (`damping_coeff`).

For ordinary diffusion, $p=1$. For biharmonic diffusion, $p=2$. Higher $p$ makes the
operator act more selectively on the smallest resolved scales, leaving the large scales
nearly untouched. This is desirable in atmospheric models because it prevents the
spurious accumulation of energy at the grid scale (which would make the model blow up)
while minimally affecting the large-scale dynamics of interest.

In spectral space, this simplifies to multiplication: a mode with total wavenumber $n$
is damped at a rate proportional to $[n(n+1)/a^2]^p$, so higher wavenumbers are
damped much more strongly.

**Rayleigh drag** (`damping_coeff_r`) is a linear friction $-r\zeta$ applied uniformly
to all scales. It represents a crude parameterization of boundary-layer drag and prevents
the zonal-mean flow from accelerating indefinitely under stirring.

---

### Stochastic Stirring

Stochastic stirring is a randomly varying forcing added to the vorticity equation to
represent, in a statistical sense, the effects of processes not explicitly modeled --
such as baroclinic instability generating eddies. Rather than computing the full
three-dimensional baroclinic dynamics, the stirring injects vorticity fluctuations
at selected scales with a prescribed spatial pattern and temporal character.

The implementation in Isca follows Vallis et al. (2004) and uses an
[AR(1) process](#ar1-process) in spectral space:

$$S^{n+1} = e^{-\Delta t/\tau} \, S^n + A \sqrt{1 - e^{-2\Delta t/\tau}} \, \xi^n$$

At each time step $n$, the previous stirring $S^n$ is partially "remembered" (with
decay $e^{-\Delta t/\tau}$) and a fresh random perturbation $\xi^n$ is added. The
result is a forcing that has a finite memory of $\tau$ (`decay_time`) seconds and
spatial localization controlled by the Gaussian envelope parameters (`lat0`, `widthy`,
`lon0`, `widthx`, `B`). The wavenumber range of the forcing is controlled by the wave
mask (`n_total_forcing_min`, `n_total_forcing_max`, `zonal_forcing_min`), targeting
synoptic-scale eddies.

The physical motivation is to mimic the random generation of Rossby wave activity by
baroclinic instability in the mid-latitude atmosphere, while keeping the model
two-dimensional and computationally tractable.

---

### Spherical Harmonics and Spectral Truncation

Rather than storing the [vorticity](#vorticity) field on a grid of latitude-longitude
points, the spectral barotropic model expands it as a sum of spherical harmonic functions:

$$\zeta(\lambda, \phi, t) = \sum_{m=-M}^{M} \sum_{n=|m|}^{N} \hat{\zeta}_m^n(t) \, Y_m^n(\lambda, \phi)$$

where $\lambda$ is longitude, $\phi$ is latitude, $m$ is the **zonal wavenumber**
(number of oscillations around a latitude circle), $n$ is the **total wavenumber**
index, and $Y_m^n$ are the spherical harmonic basis functions. The coefficients
$\hat{\zeta}_m^n$ are complex numbers stored in spectral space.

This representation has two major advantages. First, horizontal derivatives (including
$\nabla^2$) reduce to algebraic operations on the coefficients, making diffusion and
[streamfunction](#streamfunction) inversion exact and cheap. Second, the nonlinear
advection term is computed in grid space and then transformed back, using the
efficient spherical harmonic transform.

**Triangular truncation** (T$N$) retains all modes with $|m| \leq N$ and $n \leq N$.
This gives an isotropic, symmetric spectrum. The test case uses T85:
`num_fourier=85`, `num_spherical=86`. The associated physical-space grid has
128 Gaussian latitudes and 256 longitudes, which satisfies the aliasing-free
condition for quadratic nonlinearities.

The smallest resolved horizontal scale at T85 is roughly $\sim$200 km.

---

### AR(1) Process

An autoregressive process of order 1 (AR(1)) is a discrete-time stochastic process
where each value depends linearly on the previous value plus a random noise term:

$$x^{n+1} = \alpha \, x^n + \sigma \, \xi^n$$

where $0 < \alpha < 1$ is the persistence (autocorrelation), $\sigma$ controls the
noise amplitude, and $\xi^n$ is independent white noise at each step.

The continuous-time analogue is the Ornstein-Uhlenbeck process, which has a finite
memory (e-folding time $\tau$) and a stationary variance. In the stirring module,
$\alpha = e^{-\Delta t/\tau}$ and $\sigma = A\sqrt{1 - e^{-2\Delta t/\tau}}$. The
factor $\sqrt{1 - \alpha^2}$ ensures the long-time variance of $S$ converges to $A^2$
regardless of the time step $\Delta t$.

Short `decay_time` ($\tau \ll \Delta t$) produces nearly uncorrelated (white) noise.
Long `decay_time` ($\tau \gg \Delta t$) produces a slowly varying, persistent forcing.

---

### Leapfrog Scheme

The leapfrog scheme is a second-order explicit time-integration method. Instead of
stepping from time $n$ to $n+1$ using only the state at $n$, it uses:

$$\zeta^{n+1} = \zeta^{n-1} + 2\Delta t \left.\frac{\partial \zeta}{\partial t}\right|_n$$

It "leaps" over the current time level using the tendency evaluated at $n$ and the
state from one step earlier ($n-1$). This makes it second-order accurate and
computationally efficient, but it supports a spurious decoupled "computational mode"
in which the odd and even time levels drift apart. This is suppressed by the
[Robert-Asselin filter](#robert-asselin-filter).

The leapfrog scheme is conditionally stable: the time step must satisfy a CFL condition.
For the barotropic model at T85, `dt_atmos=1200` s (20 minutes) is a safe choice.

---

### Robert-Asselin Filter

The Robert-Asselin filter is a time-domain smoother applied at each leapfrog step to
suppress the computational mode. It replaces the current time level with a weighted
average of the three time levels:

$$\zeta^{n}_{\text{filtered}} = \zeta^n + \frac{\nu_R}{2}(\zeta^{n-1} - 2\zeta^n + \zeta^{n+1})$$

where $\nu_R$ is `robert_coeff`. The standard value is 0.04. Larger values damp the
computational mode more aggressively but also introduce a small first-order damping
error into the physical solution. It is a necessary numerical artifact of the leapfrog
scheme.