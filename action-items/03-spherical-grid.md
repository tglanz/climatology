# 03. Define the spherical grid contract

Priority: P1. Needed before harmonic-head comparisons.

## Evidence

`ml/src/ml/training/model.py:24-42` does not specify a grid.
The pinned `SphericalConv` defaults to equiangular transforms.
Actual sampled Isca output uses ascending Gauss-Legendre latitude nodes.
`docs/norms.md:26-65` derives cosine weights for uniform latitude spacing, then applies the result as a general area rule.
HDF5 output currently stores no latitude coordinates.

## Work

Carry real coordinates and grid conventions from source to processed data and checkpoint.
Set the SFNO transform grid and orientation explicitly.
Distinguish a chosen cosine-weighted score from actual Gaussian quadrature.
Use one coordinate-aware weighting policy where an area integral is intended.
Record normalization, truncation, axis order, and artifact compatibility.

The grid mismatch is verified. Its effect on model quality has not been measured.
Reversing latitude alone is not a separately proven performance defect.

## Verify

1. Add `test_spherical_grid.py`. Sample a known retained harmonic on the exact Gaussian nodes.
2. Transform and reconstruct it. Require maximum error below `1e-5` in float32 and the expected spectral mode.
3. Reverse the input row order through the adapter. Reverse back and require the same physical field.
4. For normalized spherical area means, require mean(1)=1, mean(sin(phi))=0, and mean(P2(sin(phi)))=0 within 1e-6. If testing unnormalized area, integral(1) must equal 4*pi*a^2.
5. Round-trip coordinates through HDF5 and checkpoint metadata. Reject incompatible grids clearly.
