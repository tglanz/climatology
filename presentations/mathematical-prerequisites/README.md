# Mathematical prerequisites

Graduate notes from fields and linear algebra to PDEs, Fourier and spherical
analysis, spectral discretization, rotating-fluid diagnostics, probability, and
integral or learned operators.

- [PDF](mathematical-prerequisites.pdf): 48 pages, linked chapter/subchapter
  contents, 83 numbered main equations, running chapter/subchapter headers,
  original-source references, chapter summaries, and separate self-test answers.
- [Complete Markdown source](mathematical-prerequisites.md): assembled from
  `preface.md`, `chapters/*.md`, `answers.md`, and `repository-map.md`.
- [Review record](review.md): the requested CS-graduate and Earth-science-professor
  reviews, corrections, and closure decisions.
- [Build record](build-record.json): hashes of exact manuscript, build inputs,
  supplied source PDFs, and output PDF; compiler details and pre-commit revision.

## Sources

The main source is [Arfken and Weber (2005), sixth edition](../../papers/methods-of-mathemacial-for-physicists.pdf).
The preface maps guide topics to its original sections. Its printed Arabic page
number plus 13 is its one-based PDF page number.

Supplementary sources are identified at the point of use:

- [Vallis (2006), first edition](../../papers/atmospheric-and-oceanic-fluid-dymamics.pdf):
  fluid dynamics, physical assumptions, and time-correlation interpretation.
- [Li et al. (2021), FNO](../../papers/fno.pdf), local arXiv version 3, and
  [Bonev et al. (2023), SFNO](../../papers/sfno.pdf), local version 1: learned operators.
- [Hunter, Notes on Partial Differential Equations](https://www.math.ucdavis.edu/~hunter/m218a_09/pde_notes.pdf),
  Sections 3.1, 3.3, 3.5, 3.9, 4.5: weak derivatives, energy spaces, weak Dirichlet existence.
- [NIST DLMF Section 3.5(v)](https://dlmf.nist.gov/3.5#v): explicit Gaussian quadrature rule.

The bibliography is shared with `book/references.bib`. A quoted theorem is
identified as such; the guide supplies the intermediate algebra for its derived
results. It does not report a new simulation or an empirical learning result.

## Build and book alignment

Requires Python 3, Pandoc with citeproc, and XeLaTeX with the TeX Live packages
used in `header.tex` (including TeX Gyre fonts, fancyhdr, titlesec, and needspace).
Run from the repository root:

```sh
python3 presentations/mathematical-prerequisites/build.py --sync-book
python3 presentations/mathematical-prerequisites/build.py --check
python3 presentations/mathematical-prerequisites/build.py
```

Edit the chapter files, then regenerate the complete Markdown and PDF.
`--source-only` assembles Markdown without rendering; `--sync-book` assembles it
and updates the generated mathematical book chapters. `--check` writes nothing
and checks structure, sequential equation tags, manuscript parity, and book parity.
The PDF build uses three LaTeX passes and rejects overfull boxes or missing glyphs.

Eleven general mathematical chapters are generated in `book/` from these sources.
The physical companion owns its more detailed fluid sequence; mathematical guide
Chapter 10 remains a compact application in this PDF. Book equation tags receive
an M prefix, independent of the book's chapter order. Compatibility pages retain
previous URLs and cross-reference the owning treatment. They render as appendices.
Project-specific source locations appear only in the companion's repository map.

Render the complete book with:

```sh
quarto render book --to html
```

## Verify

With NumPy, pypdf, Pillow, and Poppler available:

```sh
python3 presentations/mathematical-prerequisites/verify.py --render
```

An isolated documentation environment can be used without changing project dependencies:

```sh
uv run --no-project --with numpy --with pypdf --with pillow python presentations/mathematical-prerequisites/verify.py --render
```

The verifier checks 42 bounded mathematical examples, the PDF's input/output
hashes, every numbered equation, all named internal links, unique page numbering,
and chapter/subchapter headers. It renders every page and four-page contact sheets
under ignored `.build/qa/`; inspect those images after layout changes. Automated
text checks do not replace visual inspection. Build intermediates and rendered
proofs remain ignored. No simulation or model-training job is needed.
