# Review and verification record

Date: 21 November 2026.

## Requested reviews

Two independent agents reviewed the complete manuscript after the initial PDF
build, using the requested reader roles. These are agent review personas, not
claims of review by credentialed human readers.

| Reviewer role | Findings applied | Re-review result |
|---|---|---|
| Computer science graduate | Added the global-streamfunction path-integral argument; defined elliptic closure, streamlines, and potential temperature; made the grid-to-coefficient analysis map explicit. | No remaining clarity, conciseness, or readability finding. The reviewer could reconstruct the forced BVE, inversion constraints, damping signs, and AR(1) covariance from the text. |
| Earth science professor | Corrected Vallis section locators; removed a nonexistent appendix locator and restricted the viscosity discussion to the sourced model; added the Rhines-scale locator; corrected Coriolis acceleration wording; defined buoyancy, BVE, and white noise; stated self-adjointness before the energy proof; specified constant heat capacity in the potential-temperature formula. | No remaining substantive scientific issue. The reviewer checked the principal derivations, signs, dimensions, budgets, and forcing statistics. |

Both reviewers confirmed that the cover-page header was fixed. The final
running section header names the last section present on that page, including
chapter-opening pages. This is deliberate when multiple sections share a page.
The final layout pass reduced chapter whitespace, kept summaries together,
suppressed the cover's page-number footer, and prevented hyphenation in long
chapter titles. These formatting changes did not alter the approved derivations.

## Final checks

- 41 PDF pages, ten substantive chapters, and 49 numbered main equations.
- Linked PDF chapter/section contents, populated bookmarks, and a separate linked
  chapter contents list in the Markdown source.
- All 61 internal PDF links resolve; all 49 equation tags occur in extracted text.
- Every final page was rendered with Poppler and inspected. After the last title
  adjustment, page image hashes confirmed that only pages 28 and 32 changed;
  both were inspected again individually. No clipped equations, overlaps, or
  missing mathematical glyphs were found.
- XeLaTeX completed three passes with no overfull boxes or missing-character
  reports. Its unused table-caption-setup warning is harmless; there are no
  captioned tables in this document.
- Book/source synchronization and repository whitespace checks passed.
- Quarto 1.11.9 rendered all 25 book pages successfully. The ten fluid-dynamics
  pages (section introduction plus nine chapters) contain 502 checked local
  links, with no missing files or anchors.
- Bibliographic editions, dates, and titles were checked in the supplied PDFs.
  The filename of the supplemental Vallis et al. paper was not used as evidence
  for its publication year. Unsigned model notes remain unattributed.
- The physical equation, discrete integrator, and implemented stirring were
  distinguished. No simulation, training job, or experiment result was changed.

Reproduce the structural and rendering checks using the commands in README.md.
The image renders and compiler log are ignored build products. Input hashes and
code provenance are in build-record.json. Conservation derivations apply under
the stated smoothness, geometry, and boundary assumptions; these checks are not
proofs of turbulent statistical stationarity or numerical convergence.
