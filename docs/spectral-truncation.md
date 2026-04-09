# Spectral Truncation in Atmospheric Models

---

## Conceptual Background

### How spectral models represent fields

Instead of storing the value of (say) vorticity at every grid point directly, a spectral
model represents fields as a sum of spherical harmonic basis functions on the sphere.
Each spherical harmonic is labelled by two integers:

- m -- the zonal wavenumber (how many oscillations around a latitude circle)
- n -- the meridional index (related to how many oscillations from pole to pole)

The full field at any point is reconstructed by summing all retained (m, n) pairs.
The model time-steps the spectral coefficients, then transforms to grid space when
needed (e.g. for nonlinear products) and transforms back.

### Why truncate?

You cannot retain infinitely many harmonics. Truncation at wavenumber N means you
discard all harmonics above some threshold. This sets the effective spatial resolution
of the model.

### Triangular vs rhomboidal truncation

Two common truncation shapes exist. For triangular truncation TN:

    retain all (m, n) where m <= N and n <= N

The retained modes form a triangle in (m, n) space. Every zonal wavenumber up to N
has the same number of meridional modes. This gives isotropic resolution -- the model
resolves roughly the same spatial scale in the zonal and meridional directions.

For rhomboidal truncation RN:

    retain all (m, n) where n <= N + m

The retained modes form a rhombus. Rhomboidal truncation gives higher meridional
resolution at low zonal wavenumbers but is no longer standard. Triangular truncation
is used in virtually all modern spectral models.

---

## Practical Reference

### What does T21 mean?

T21 means triangular truncation at N = 21. The model retains all spherical harmonics
with zonal wavenumber m <= 21 and total wavenumber n <= 21. The "T" stands for
triangular.

Common resolutions and their approximate grid spacing at mid-latitudes:

    T21   ~600 km   (coarse, fast, good for dynamics studies)
    T42   ~300 km
    T63   ~200 km
    T85   ~150 km
    T170  ~75 km

### Why do we need num_lat if T21 already defines the resolution?

This is the key question. The spectral truncation (num_fourier = 21) defines the
resolution in spectral space. But the model also needs a physical grid to evaluate
nonlinear terms (products like u * zeta). That grid must be fine enough to represent
all the products of the retained harmonics without aliasing errors.

When you multiply two fields each containing wavenumbers up to N, the product contains
wavenumbers up to 2N. To represent that product exactly on the grid you need enough
grid points to resolve wavenumber 2N without aliasing.

The standard dealiasing rule for a triangular truncation TN is:

    num_lat >= (3 * N + 1) / 2   (round up to the nearest integer, preferably even)
    num_lon >= 3 * N + 1

For T21:

    num_lat >= (3 * 21 + 1) / 2 = 32.0  -->  num_lat = 32
    num_lon >= 3 * 21 + 1       = 64    -->  num_lon = 64

So num_lat = 32 and num_lon = 64 are the minimum alias-free grid sizes for T21. That
is exactly what the barotropic stirring example uses.

You can use a larger grid than the minimum (the extra points cost compute but do not
change the spectral resolution). You cannot safely use a smaller grid without aliasing
contaminating your solution.

### Summary of the relationship

    num_fourier  = N = 21      -- the spectral resolution, sets which harmonics are retained
    num_spherical = N + 1 = 22 -- the maximum total wavenumber n retained (triangular rule)
    num_lat      = 32          -- the Gaussian grid rows, sized to avoid aliasing
    num_lon      = 64          -- the longitude grid columns, sized to avoid aliasing

num_fourier and num_lat are not redundant. num_fourier controls the spectral truncation.
num_lat controls the physical grid. They are linked by the dealiasing rule but you set
them independently because the transforms module needs both.

### Quick reference table

    T-level   num_fourier   num_spherical   num_lat   num_lon
    T21       21            22              32        64
    T42       42            43              64        128
    T63       63            64              96        192
    T85       85            86              128       256
    T170      170           171             256       512

### num_spherical

For triangular truncation num_spherical must always equal num_fourier + 1. It is the
maximum value of the total wavenumber index n in the (m, n) pair. The reason it is
a separate parameter rather than inferred is that the transforms module was written
to also support rhomboidal truncation, where the relationship is different.

---

## In the Script

```python
'barotropic_dynamics_nml': {
    'triang_trunc' : True,   # use triangular (isotropic) truncation
    'num_fourier'  : 21,     # T21: retain harmonics up to m = n = 21
    'num_spherical': 22,     # must be num_fourier + 1 for triangular truncation
    'num_lat'      : 32,     # Gaussian grid: (3*21+1)/2 = 32, alias-free minimum
    'num_lon'      : 64,     # longitude grid: 3*21+1 = 64, alias-free minimum
    'fourier_inc'  : 1,      # retain all zonal wavenumbers (increment of 1)
}
```
