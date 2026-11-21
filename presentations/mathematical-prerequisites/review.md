# Review and verification record

Date: 21 November 2026.

Two independent agents reviewed the complete first draft, then re-reviewed the
revised sources and PDF. Their assigned perspectives were **Computer science
graduate** and **Earth science professor**, as requested. They assessed clarity,
conciseness, readability, self-containment, source attribution, and correctness.

## Computer science graduate

Required findings and resolutions:

- Added a compact calculus bridge: product and chain rules, definite integration,
  the fundamental theorem, integration by parts, and a worked integral.
- Defined local integrability, test-function convergence for distributions,
  the universal test-function condition, and limits defining the zero-boundary
  energy space. Added the weak Poisson forcing class and a precise cited
  existence statement.
- Derived the smooth tangent-field decomposition, defined a harmonic tangent
  field, explained path independence on the sphere, and distinguished the
  displayed tangent-vector convention from AW's coupled vector harmonics.
- Marked the associated Legendre norm as a quoted source result; expanded the
  ordinary Legendre normalization calculation.
- Added conjugate-compatible Fourier weights and real degree-wise spherical
  weights for real features and real activations.
- Removed duplicate PDF navigation, corrected the answer pointer, introduced
  supremum, and cut the unused tensor digression.

Closure: all required findings resolved; no material mathematical or pedagogical
issue remained. The reviewer checked revised sources, PDF text, and rendered
navigation, sphere, spectral-layer, answer, and reference pages.

## Earth science professor

Required findings and resolutions:

- Repaired unnumbered running headers, removed duplicate navigation, and replaced
  overflowing repository paths with short linked labels.
- Added the initial-field and weak-forcing function classes, and sufficient
  kernel/input assumptions for spherical integral operators.
- Specified countable additivity, the critical-point condition for the Hessian
  test, and the dimensionless periodic coordinate in the derivative example.
- Clarified the separate answer section, Legendre proof, and relative versus
  absolute enstrophy. Calibrated the preface as a compact graduate introduction.

Closure: all required precision, navigation, and layout corrections resolved;
no material remaining issue. The reviewer also confirmed the added tangent-field
proof and real spectral constraints. Checks of spherical area, streamfunction
signs, harmonic phases, sampling bounds, Rossby dispersion, spectra, and
correlation formulas found no substantive sign or normalization error.

## Final verification

- 12 substantive chapters; every teaching subchapter opens with result and
  motivation; every chapter has a main-result summary and self-test.
- 48 PDF pages, 83 unique sequential main-equation numbers, 162 checked internal
  links, and 217 named PDF destinations.
- 42 small mathematical probes cover polynomial orthogonality, quadrature
  exactness and its limit, Parseval examples, nonlinear projection, DFT aliasing,
  serial covariance counting, Rossby residuals, and spectral ratios.
- PDF source/build hashes match. Every page has a unique matching page number;
  every mathematical page has chapter and subchapter running text.
- Three-pass XeLaTeX build: no overfull boxes, missing glyphs, or unresolved
  references. Every final page was rendered and visually inspected using
  four-page sheets; layout-only final changes were checked against prior renders.
- The complete book rendered with Quarto 1.11.9 in a fresh output directory:
  31 HTML pages and 1,437 local HTML links/section targets checked without a
  broken target. The generated mathematical chapters pass source-parity checks.
- `git diff --check` passed. No simulation, training, saved data, or Isca patch
  was changed. The concurrent physical-prerequisite work was preserved.

The build record identifies the exact source and output hashes. The recorded
repository revision is the pre-commit build context, not a claim about a later
commit identifier or remote deployment. Rendered temporary proofs and build logs
are kept under ignored `.build/`.
