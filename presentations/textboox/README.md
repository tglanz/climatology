# Math and physics textbook

Read [the table of contents and Chapter 1](textbook.md), or the matching
[PDF](textbook.pdf). Chapters 2-12 are outlined only. Continue after the reader
requests the next chapter, in chat or through the authorized ntfy listener.

Chapter 1 develops the mathematical prerequisites in depth: coordinate geometry,
local directions and distance, pole regularity, surface integration, field inner
products and projection, Gaussian quadrature, and the limits of finite samples.
Worked examples and reproducible numerical experiments connect the mathematics
to the repository. The target is mathematical-physics textbook substance with
prerequisites explained for a computer science reader, without long derivations
or detail that does not support understanding the project.

Every chapter uses exactly these sections, in order: The Problem, The Intuition,
The Mechanism, Reading the Math, Code Connection, and Sanity Check. Every displayed
equation has a symbol-by-symbol explanation and a plain-English translation.
Use mathematical symbols rather than phonetic names for Greek letters. Prose
remains ASCII; mathematics uses LaTeX. Physical units and conventions are explicit.
Source behavior was inspected on 2026-11-21. The current 30-page PDF was
accepted after the required student-perspective review and revision loop; see
the [review and verification record](review.md).

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
and current source links. Keep rendering intermediates outside the repository.

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
`tglan-clim-51189` on ntfy.sh. The existing three-minute listener handles messages
starting with `task: ` when they relate to this textbook. It remains active until
asked to stop and must apply the same student review loop to each update.
