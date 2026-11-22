# Textbook refactor - review and verification

Date: 22 November 2026.

## Editorial contract

Applied `/Users/tal.glanzman/own/dotfiles/agent/skills/tg-make-textbook/SKILL.md`,
including both subject references. Mathematics remains the primary flavor, with
physics supporting the applications. The user's graduate audience and scope take
precedence over the skill catalog's undergraduate description.

The refactor adds chapter questions, a shared numbered object counter, explicit
hypotheses, target-labelled proofs/derivations, grayscale role typography, and
section exercises. All 83 original equation numbers are preserved. The student
edition omits solutions; the separate instructor key covers every exercise.

## Content review and corrections

The same two requested independent agents reviewed all twelve chapters and the
complete instructor key against the skill: **Computer science graduate** and
**Earth science professor**. They checked labels, source-transform regressions,
complete hypotheses, arguments, worked examples, physical models, signs, units,
and exercise solutions.

Corrections made through their feedback:

- Fixed one stale proof target and sentence fragments left by splitting the old
  prose into formal objects. Added the remaining short target-labelled proofs.
- Made $L^2$, periodic smoothness, positive-variance, kernel-domain, and nullspace
  assumptions explicit. Distinguished continuous sampled representatives from
  arbitrary point assignments in the aliasing statement.
- Completed the cross-degree associated-Legendre orthogonality argument, not just
  the same-degree normalization.
- Used Vallis' density-as-a-function-of-pressure convention for barotropic flow,
  including constant density; set forcing and dissipation both to zero for the
  Rossby-wave dispersion model.
- Distinguished kernel Fourier coefficients from angular wavenumber and moved
  the spherical-kernel coefficient definition before its first use.
- Worked the previously asserted basis-normalization and constant-forcing
  examples. Added explicit data for characteristic crossing.
- Added independent problems on the converse Parseval test, backward-diffusion
  instability, Galerkin mean conservation, and an integral-operator bound.

Both reviewers closed the content review with no material issue remaining.
All 63 instructor solutions were checked; no arithmetic or sign error remained.

## Layout review and final checks

- Student PDF: 66 pages, 244 teaching objects, 63 exercises, 83 main equations,
  and 191 validated internal links. Every object/exercise label occurs in the PDF.
- Checked unique page numbers, chapter/subchapter headers, citations, source and
  PDF hashes, and absence of instructor solutions in the student edition.
- All 42 bounded mathematical probes passed. Chapter/source/book parity,
  sequential object and exercise counters, immediate proof targets, and the
  one-to-one exercise/key mapping passed.
- Three-pass XeLaTeX compilation has no overfull boxes or missing glyphs.
- Every final PDF page was rendered and inspected at original image detail:
  CS reviewer covered pages 1-32, Earth-science reviewer covered pages 33-66.
  Six short-object/paragraph pagination defects were corrected, followed by
  another exhaustive pass over the same ranges. Both visual reviews passed.
- Refactored Quarto book rendered successfully: 31 HTML pages; 1,460 local
  HTML links and section targets checked without a broken target. HTML uses the
  same labelled source and matching grayscale role styles.
- The saved initial PDF retains SHA-256
  `c88fb0ec08af038495f3c5fb2256095eac9d14d176bc335597c79885e3c56e6b`,
  matching the original committed artifact. Existing Isca changes are preserved.

The build record identifies the exact student source, output PDF, instructor key,
source PDFs, skill, and build-input hashes. Render proofs and intermediate files
remain under ignored `.build/`. No simulation or model-training run was needed.

---

## Initial edition review and verification

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
