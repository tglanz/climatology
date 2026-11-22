# Textbook review and verification record

Date: 22 November 2026.

## Editorial refactor

The explicitly requested `tg-make-textbook` skill was read with both its physics
and mathematics references. Physics is the primary flavor. The user's graduate
level, physical scope, source editions, notation, and equation numbering remain
in force.

The revision adds chapter questions, a shared chapter counter for 140 teaching
objects, target-named proofs and derivations, worked examples, and thirty
exercises grouped by topic and difficulty. Physical laws, idealized models,
definitions, and derived results use distinct labels. Definitions/models use a
left rule, results a box, and examples a top rule; these distinctions survive
grayscale printing. The checked instructor solutions are separate from the
student PDF and Markdown.

## Fresh reader reviews

Two independent agents reviewed the full revised manuscript and all thirty
solutions using the requested roles. These are agent personas, not claims of
review by credentialed human readers. The approval of the earlier edition was
not treated as approval of the refactor.

| Reviewer role | Findings resolved | Re-review outcome |
|---|---|---|
| Computer science graduate | Added a cell/patch proof of the integral theorems; restored result hypotheses and first-use explanations; separated linearization assumptions from the derived PDE; corrected object roles, refactoring joins, and exercise boundary cases. | No remaining actionable clarity, conciseness, pedagogical-role, or exercise-answer finding. |
| Earth science professor | Restored the depth-independent layer and non-divergent mean-flow conditions; qualified the buoyancy parcel, harmonic derivative orders, stochastic initial moments, covariance, and forced budgets; checked every new example and solution; clarified implementation facts versus assumptions. | Scientific re-review passed. The final requested positive forcing-variance condition is present in Exercise 9.1. |

The sampled AR variance exercise now asks for the first sampled crossing,
$\Delta t\lceil\tau/\Delta t\rceil$, rather than assuming $t=\tau$ is sampled.
Single-mode energy ratios explicitly require a nonzero coefficient. Definition
8.3 states $0\leq m\leq\ell$ before the derivative formula and remains with its
formulas on PDF page 38. Exercise topic headings stay with their first problem.

## Final verification

- 55 PDF pages, ten substantive chapters, 140 numbered teaching objects, thirty
  exercises, and thirty matching instructor solutions.
- All 49 original numbered mathematical expressions and equation identifiers
  match the earlier edition (commit `29fd5a8`), ignoring whitespace and the
  presentation-only `boxed` wrapper removed in favor of result boxes.
- Every numbered equation, teaching-object label, and exercise label appears in
  the exported PDF. All 69 internal PDF links resolve, with 420 named
  destinations and a populated outline. The Markdown has its own linked contents.
- Every final page was rendered and visually inspected. After the last heading
  spacing change, image hashes identified only pages 2, 17, 18, 41, and 42 as
  changed; those pages were inspected again. No clipped math, overlaps, missing
  glyphs, or orphaned formal-object labels remain.
- XeLaTeX completed three passes without overfull boxes or missing characters.
  The unused table-caption-setup warning is harmless; the tables have no captions.
- Manuscript/book/style synchronization and repository whitespace checks pass.
- Quarto rendered all 31 current book pages. The ten fluid-dynamics HTML pages
  contain 620 checked local links, with no missing file or fragment target.
- The book shares general theory, teaching objects, and exercises, with a P prefix
  on companion identifiers. Repository implementation details and instructor
  solutions remain outside its student chapters.
- Bibliography and physical-source provenance were retained. Rendering input
  hashes, source hashes, and the editorial convention are recorded in
  build-record.json. No simulation, training job, or experiment result changed.

The mathematical-prerequisites refactor and the modified Isca submodule were
preserved. Structural checks do not establish turbulent stationarity or numerical
convergence; the conservation results retain their stated model, smoothness,
geometry, and boundary conditions.
