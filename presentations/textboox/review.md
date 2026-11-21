# Source-grounded textbook and implementation review

Date: 2026-11-21.

Scope: reformulate Chapter 1 around the supplied primary references; add the
authorized technical Chapter 13 with exactly three main sections; make contents
entries internal links; add a running chapter indication on every PDF page.
Chapters 2-12 remain explicitly marked linked roadmap entries.

## Fresh student-perspective review

A new reviewer agent, `student_review_revision`, read as a CS student with little
physics background, checked source claims against implementation, and inspected
all pages of both draft and final PDFs.

1. **REVISE:** reconcile the definition of saved snapshots with daily interval
   averaging; define rotation and retention notation before its formulas; define
   float64; fix joined numerical prose and the V04 appendix page reference.
2. **REVISE layout:** keep the capstone question intact and make its source-route
   entry a real table row. The reader additionally requested running chapter
   headers; these were added to all pages, including contents and reference pages.
3. **ACCEPT:** re-reviewed corrected Markdown and all 58 final rendered pages,
   with full-size checks of code, spinup and relative-loss formulas, and the
   averaging ledger. The reviewer explicitly accepted the final artifact with
   no substantive learning, accuracy, or layout issue.

The author independently inspected all 58 final pages. The source hierarchy is
original SFNO/FNO papers, Vallis for physical formulations, and Arfken and Weber
for supporting mathematics. Local books remain outside the textbook commit.

## Verification

- Built from Markdown using Pandoc/XeLaTeX. Source checks passed for Chapter 1's
  six sections and Chapter 13's requested three-section exception.
- Checked consecutive labels and immediate symbol keys/translations for all
  45 displayed equations, ASCII prose, prohibited phrases, and local references.
- Executed all three Markdown Python examples and existing analytic geometry,
  quadrature, projection, and sampling checks through `uv run --project ml`.
- Checked current spinup and convergence return indices on small arrays;
  population moments, normalization inverse, weighted relative-loss reduction,
  window-prediction aggregation, batch weighting, and default grid arithmetic.
- Verified all 18 contents annotations are internal PDF GoTo links and resolve
  to the written chapters, roadmap entries, implementation sections, or sources.
- Verified the appropriate running header on every page, all equation labels,
  symbol keys/translations, updated source phrases, and extracted word bounds.
- Visually inspected all final pages, figures, formulas, tables, and code.
  The final PDF contains 58 pages. No simulations or training jobs were run.

## Accepted artifact identity

- Markdown SHA-256: `6629afbcd96c60e4eeb0a810803fa3f325ecb533df1592a5624a885f1daffaf1`
- PDF SHA-256: `a94a665d29f3c29a4df7685a296b6db8be726a3b41c40491e820f84ce6b962ef`

The reader requested that periodic ntfy polling stop. Its automation is paused.
The final authorized completion notification is separate from periodic polling.

---

# Previous accepted revision

# Chapter 1 review and verification

Date: 2026-11-21.

Scope: the table of contents and Chapter 1. Chapters 2-12 remain outlines.
The chapter was rewritten for mathematical-physics textbook depth while defining
prerequisites for a computer science reader with little physics background.

## Student-perspective review

A separate reviewer agent adopted the requested CS-student perspective.

1. Initial result: **REVISE**. The reviewer requested one worked integral
   evaluation, removal of unnecessary function-space abstraction, definitions
   for remaining specialist vocabulary, and explicit projection arithmetic.
2. Revision: added the antiderivative and upper-minus-lower evaluation producing
   one-third, simplified the zero-area discussion, defined the remaining terms,
   and showed the projection numerator and denominator. Result: **ACCEPT**.
3. Final PDF review: the same reviewer inspected all 30 final pages through
   rendered contact sheets and inspected the integral, figures, and code at full
   size. Result: **ACCEPT**. No substantive learning or layout issues remained.

The author independently inspected every final PDF page. The acceptance concerns
this chapter's prerequisites and presentation; it does not claim that the unwritten
chapters or the whole project have already been taught.

## Executed verification

- Built the PDF from Markdown with Pandoc and XeLaTeX.
- Executed the three Python blocks directly from the Markdown in the existing
  ML environment using `uv run --project ml --no-sync --group train --group vis`.
- Checked Gaussian moments through each rule's promised degree, the two-node
  fourth-moment failure, coordinate-order invariance, area mean and RMS,
  projection and its residual, and the smooth hidden-pattern counterexample.
- Independently checked the geodesic example, finite cell areas, polar cap area,
  extra-cosine limit, and the hidden pattern's exact rational mean square.
- Verified the six-section structure, consecutive labels for 25 interpreted
  equations, local source links, and notation restrictions.
- Extracted the final PDF text to verify all 25 equation labels, symbol keys,
  translations, and three figure captions. Checked all extracted text bounds.
- Rendered and visually inspected all 30 pages. Equations and code remain intact;
  figures and mathematical notation are legible.

No simulations, model training, or experiment-data changes were required.

## Accepted artifact identity

- Markdown SHA-256: `be8f7c21c3818002b5d0a6842b4c5cce3d64ce35b2f52060b58aa835cce32227`
- PDF SHA-256: `64919a17b1037d141d6a898f9fb3e9e2c5f12a1fc5678d7b20d97705a2836ac1`

At that earlier revision, the three-minute listener was active. The later user
instruction above pauses it; the student review loop still applies.
