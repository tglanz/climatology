# BVE, spherical harmonics, and SFNO

A 48-slide lecture and study guide. It develops spherical flow, vorticity,
the SHT as a longitude FFT and a latitude Legendre projection, Gaussian
quadrature and grids, spectral BVE stepping, SFNO layers, and candidate
output heads.
The guide includes worked examples, self-checks, answers, and references.

- [Read the slides](bve-harmonics-sfno.pdf).
- [Edit in PowerPoint](bve-harmonics-sfno.pptx).
- [Read or edit the teaching source](presentation.md).

The current implementation claims refer to the source pins listed in the
deck, inspected on 2026-11-11. Proposed heads are labeled as proposals.

For the repository work, see the [workplan](../../docs/workplan.md) and
[pipeline reconsideration](../../action-items/03-pipeline.md).
The output-head comparison remains a separate research direction.

## Editing and rebuilding

presentation.md is the content source. PowerPoint text remains editable.
Display equations and inline mathematics are rendered from LaTeX.
Prose remains editable; math images retain their LaTeX in alt text.
LaTeX source is also stored in the PowerPoint speaker notes.

render.mjs reads the Markdown, builds the PowerPoint with Artifact Tool,
validates it, and exports the same deck to PDF with LibreOffice. Temporary
files and validation receipts stay in the ignored .build/ directory.

Requirements: the bundled Codex Node runtime and packages, the installed
Presentations skill, Python, pdflatex, pdftocairo, and headless LibreOffice.

Set these variables to the installed paths:

- RUNTIME_NODE_MODULES: the bundled Node package directory.
- PRESENTATION_SKILL_DIR: the installed Presentations skill directory.
- RUNTIME_PYTHON: the bundled Python executable.

Run the script with the bundled Node executable:

~~~sh
node render.mjs
~~~

The script uses pdflatex, pdftocairo, and soffice from PATH.
PDFLATEX, PDFTOCAIRO, and SOFFICE can each override an executable path.
Rebuilding replaces the PDF and PowerPoint beside the source.

## Study

Attempt the SHT/Gaussian-grid self-check, Self-check A, and Self-check B
before their answer slides.
Then derive the zonal-wind example without notes.
Retry missed questions with a different harmonic degree or output cutoff.
