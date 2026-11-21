# Math and physics textbook

Read the [linked table of contents and textbook](textbook.md), or the matching
[PDF](textbook.pdf). Chapters 1 and 13 are written. Chapters 2-12 remain linked
roadmap entries; continue those chapters only when requested in chat or through
the authorized ntfy listener.

Chapter 1 develops fields and operators, spherical coordinates and geometry,
physical surface integration, inner products, projection, finite expansions,
Gaussian quadrature, and sampling limits. Chapter 13 documents the inspected
simulation, preprocessing, training, and evaluation implementation, including its
mathematical formulations and every important averaging level. Both define
prerequisites for a computer science reader without a large physics background.

Prioritize the original SFNO and FNO papers in `papers/` for operator architecture,
Vallis's *Atmospheric and Oceanic Fluid Dynamics* for physical formulations, then
Arfken and Weber for mathematical support. Cite source sections/equations inline,
with one-based PDF pages. Translate coordinate and normalization conventions.
The supplied book files remain local and are not staged with textbook changes.
The full bibliography and reading route are included in the textbook itself.

Foundational chapters use exactly these sections: The Problem, The Intuition,
The Mechanism, Reading the Math, Code Connection, Sanity Check. The reader
explicitly requested one exception: Chapter 13 has exactly three main sections,
Simulations and preprocessing; Training; Evaluation. Every displayed equation has
a symbol-by-symbol explanation and a plain-English translation. Define symbols
before formulas. Use mathematical symbols rather than phonetic Greek names.
Prose remains ASCII; mathematics uses LaTeX. State units and array axes.

Source behavior was inspected on 2026-11-21. See the
[review and verification record](review.md) for the required student review and
rendered-PDF acceptance of each delivered revision.

## Build and check

From the repository root, with Pandoc, XeLaTeX, and the existing ML environment:

```sh
uv run --project ml --group train --group vis \
  python presentations/textboox/build.py
```

The script executes the three Python examples directly from the Markdown, checks
additional analytic reference values, regenerates the three figures, and rebuilds
the PDF. Its temporary LaTeX and Pandoc filter keep equations with their symbol
keys and translations, and keep code examples intact. The Markdown remains the
single teaching source. The build does not modify simulation or experiment data.

To run only the source and numerical checks:

```sh
uv run --project ml --group train --group vis \
  python presentations/textboox/build.py --check
```

Render and visually inspect every final PDF page before delivering an update.
Check text/figure legibility, equation numbering, pagination, source/PDF parity,
and current source links. Verify internal PDF contents links and running chapter
headers on every page. Keep rendering intermediates outside the repository.

## Required student review loop

After each update, start a reviewer agent that reads as a computer science
student with little physics background. Ask whether the chapter supplies all
necessary information, enough mathematical and physical detail, and no unrelated
complexity or excessive precision. Check definitions, conceptual dependencies,
worked examples, and connections needed to understand the whole project.

Revise substantive gaps, confusing passages, factual issues, and unnecessary
digressions. Return the revision to the reviewer. Repeat until the reviewer
explicitly accepts. Record the review outcome and verification performed in the
completion message. Do not replace this review with a formatting checklist.

Commit only explicitly named files under `presentations/textboox`, push the
verified textbook commit without overwriting concurrent work, and notify
`tglan-clim-51189` on ntfy.sh when requested. The reader stopped periodic ntfy
polling on 2026-11-21; the automation is paused. Do not resume polling unless
requested. Future textbook updates still require the same student review loop.
