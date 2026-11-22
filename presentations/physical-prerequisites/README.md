# Physical prerequisites for barotropic dynamics

Graduate notes from continuum forces and conservation laws to the stochastically
stirred barotropic vorticity equation on a rotating sphere.

- [PDF](physical-prerequisites.pdf): linked contents and bookmarks, numbered main
  equations, chapter/section running headers, source references, notation guide,
  labeled teaching objects, worked examples, and chapter exercises.
- [Markdown manuscript](physical-prerequisites.md): the authoritative content.
- [Instructor solutions](instructor-solutions.md): checked exercise solutions,
  kept separate from the student-facing text.
- [Review record](review.md): fresh graduate-CS and Earth-science reviews.
- [Build record](build-record.json): source hashes, implementation provenance,
  and compiler details. The repository revision is the pre-commit build context;
  hashes identify the exact inputs, including the locally modified Isca files.

## Editorial structure

The revision follows the explicitly requested `tg-make-textbook` skill, with
physics primary and mathematics supporting the derivations. The audience stays
graduate. Each chapter opens with a physical question, develops one objective
per section, then ends with a compact recap and problems grouped by topic and
difficulty. All 49 original numbered mathematical expressions are preserved.

Definitions, models, assumptions, laws, results, examples, and remarks share one
teaching-object counter per chapter. Proofs and derivations name their targets;
exercises use a separate chapter counter. Numbered teaching objects are distinct
from numbered equations. Definitions use a left rule, results a box, and examples
a top rule, so their roles remain visible in grayscale. Student-facing files do
not include exercise answers.

## Sources

The first three provide the main theory. The fourth supplies the specific
stochastic forcing law; its filename has an incorrect year.

1. [Vallis (2006), first edition](../../papers/atmospheric-and-oceanic-fluid-dymamics.pdf).
2. [The barotropic vorticity equation, unsigned model notes](../../papers/barotropic.pdf).
3. [Arfken and Weber (2005), sixth edition](../../papers/methods-of-mathemacial-for-physicists.pdf).
4. [Vallis et al. (2004)](../../papers/vallis-etal-2024.pdf).

The final chapter uses these local implementation sources:

- [Simulation wrapper](../../sim/barotropic_stirring.py).
- [Vorticity dynamics](../../submodules/isca/src/atmos_spectral_barotropic/barotropic_dynamics.F90).
- [Stirring](../../submodules/isca/src/atmos_spectral_barotropic/stirring.F90).
- [Spectral damping](../../submodules/isca/src/atmos_spectral/model/spectral_damping.F90).

## Build and book synchronization

Requires Python 3, Pandoc with citeproc, and XeLaTeX with the standard TeX Live
packages used in `header.tex`, including tcolorbox, titlesec, and needspace. No simulation or ML environment is needed.
From the repository root:

```sh
python3 presentations/physical-prerequisites/build.py
python3 presentations/physical-prerequisites/build.py --check
```

The build compiles three LaTeX passes and rejects overfull boxes and missing
glyphs. It checks teaching-object and exercise numbering, argument targets, and the
separate instructor key. It also generates the book's nine general fluid-dynamics chapters from
the same manuscript. To synchronize without building the PDF:

```sh
python3 presentations/physical-prerequisites/build.py --sync-book
```

The book uses a P prefix on the companion's teaching-object and equation numbers
so its different chapter ordering cannot imply a different identity. The book includes parcel derivatives and transport in its generated kinematics
chapter, and cross-references its existing vector-calculus material for shared
operators and integral theorems. Repository-specific defaults and code remain
in the companion's final chapter. Bibliography metadata is shared through
`book/references.bib`. Do not hand-edit the generated `.qmd` chapters.

## Verification

With pypdf and Pillow installed, and Poppler on PATH:

```sh
python3 presentations/physical-prerequisites/verify.py --render
```

This checks internal destinations, numbered equations, teaching labels, and
student/instructor exercise correspondence. It renders every
page, and creates four-page contact sheets under ignored `qa/`. Those renders
must still be inspected visually; structural checks do not prove good layout.
The final verification and review results are recorded in `review.md`.

Render the book separately with `quarto render book --to html`. Build outputs
under `book/_site/` and temporary QA images are not committed.
