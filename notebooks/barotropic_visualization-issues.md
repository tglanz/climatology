# barotropic_visualization.ipynb - Known Issues

NOTE: SESSION was disrupted while trying to fix PR1. The last thing mentioned: he blow-up is a CFL violation -- the spectral Laplacian inversion assigns large PSI values
   at low wavenumbers, driving large winds that violate the 6-hour timestep stability limit.
  I need to replace the forward Euler integration with exact spectral zonal advection (shift
  vorticity by U_mean * dt / a in Fourier space, which is unconditionally stable), plus a
  stirring term to drive interesting time evolution.

## Priority 1: Root Cause (Fix First)

Most problems stem from the synthetic data being too artificial. Fixing the data
generation will resolve several downstream issues automatically:

- Narrowband spectrum (wavenumbers 4-8 only) instead of broadband
- Time evolution that scales amplitude rather than evolving the flow
- V component not properly derived from the same field as U

The fix requires generating data with a realistic broadband spectrum and a
physically plausible time evolution (e.g., advecting the field forward in time).

## Priority 2: Broken Plots (Unusable)

### 2.2 Kinetic Energy Spectrum
The synthetic field only has energy at wavenumbers 4-8. The spectrum has a sharp
cliff at wavenumber 8 then drops to numerical noise (~1e-28). The k^{-3} reference
line sits entirely above the cliff. The plot does not demonstrate what a real
energy spectrum looks like. Blocked on Priority 1.

### 3.2 Power Spectrum Comparison / Spectral Ratio
The Gaussian blur prediction has a nearly flat spectrum while the reference drops
to near-zero above wavenumber 8. The ratio reaches ~10^17 at high wavenumbers,
making the spectral ratio plot completely uninterpretable. Blocked on Priority 1.

### 1.5 Enstrophy Conservation
Enstrophy grows monotonically by 3.5x, which is physically wrong for a conservation
diagnostic. Caused by the time series scaling vorticity as `VOR_0 * (1 + 0.08*t)`,
which uniformly amplifies all values. Blocked on Priority 1.

### 1.3 Zonal Mean Zonal Wind
All 12 time steps are nearly identical and the colorbar is useless. The time
evolution in the synthetic data is too small to be visible. Blocked on Priority 1.

## Priority 3: Wrong Output (Misleading)

### 2.1 Quiver (Wind Vectors)
Vectors are enormous and point in nearly vertical directions:
- `scale` parameter is wrong for the data magnitudes
- `V_APPROX` (derived from streamfunction gradient) is badly scaled relative to
  `U_FULL`, producing unrealistically large meridional winds

### 3.3 PDE Residual Contours
The residual contours are crowded only at the poles and nearly absent everywhere
else, giving a misleading picture of where the residual is large.

## Priority 4: Missing Visualizations

### Vorticity Evolution Over Time
There is no plot showing how the vorticity field evolves spatially over time.
Two techniques should be added:

- **Multi-panel snapshot sequence**: a row of vorticity maps at evenly spaced
  time steps (e.g., t=0, t=3, t=6, t=11) side by side. Good for static reports
  and papers.

- **Animation**: `matplotlib.animation.FuncAnimation` renders as an embedded
  HTML5 video in Jupyter. More informative for seeing continuous evolution but
  not suitable for static documents.

Both are BVE-specific diagnostics, though the techniques generalize to any
time-evolving field.

