# 16. Correct book mathematics and references

Priority: P1.

## Verified errata

| Source | Correction and check |
|---|---|
| `book/01-vector-calculus/change-of-variables.qmd:15-17` | Do not combine oriented inverse limits with an absolute derivative. For g(u)=-u, f=1 on [0,1], the present formula gives -1 instead of 1. |
| `book/01-vector-calculus/spherical.qmd:109` | Under L G=delta, the 3D Green function for -Delta is 1/(4 pi r). Flux of -grad(1/r) is 4 pi. |
| `book/02-harmonic-analysis/function-spaces.qmd:15-18` | Polynomials of degree at most n have dimension n+1. They are not infinite-dimensional. |
| `book/02-harmonic-analysis/fourier-series.qmd:9-15` | Distinguish ordinary Fourier coefficients from coefficients in the normalized orthonormal basis. For f=1, c0=1 while its normalized-basis coefficient is sqrt(2 pi). |
| Same file, line 36 | State periodic-extension smoothness and endpoint compatibility. Smooth f(x)=x on the interval still has 1/n Fourier decay. |
| Same file, line 60 | The square wave has jumps and is not C0. State the denominator when quoting Gibbs overshoot percentages. |
| `book/04-geophysical-fluid-dynamics/motion.qmd:25-31` | Incompressibility does not alone imply spatially constant density. State the homogeneous-density assumption where used. |

## Work

Fix these claims using consistent definitions.
Audit related worked examples and all remaining equations before adding theory.
Declare the bibliography in Quarto and check every citation key and section reference.
Verify metadata against primary publications, including the GSNO reference.
Avoid duplicating shared definitions.

## Verify

1. Recompute the listed counterexamples by hand or with a small independent symbolic check.
2. Check dimensions, signs, normalization, domains, and spherical coordinate conventions throughout.
3. Render with citations enabled. Require no unresolved citations or cross-references.
4. Inspect every changed equation and worked example in the rendered book.
