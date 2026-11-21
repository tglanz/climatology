# Math and physics textbook

Read [the table of contents and Chapter 1](textbook.md), or use the matching
[PDF](textbook.pdf). Chapters 2-12 are outlined only. Continue after the reader
responds to Chapter 1.

The Markdown file is the teaching source. It uses the requested six-section
chapter structure. Every displayed equation has a symbol-by-symbol explanation
and a plain-English translation. Source behavior was inspected on 2026-11-21;
concurrent work elsewhere in the repository is outside this addition.

## Rebuild

From the repository root, with Pandoc and XeLaTeX installed:

```sh
pandoc presentations/textboox/textbook.md \
  --standalone --pdf-engine=xelatex \
  --metadata title="From Spherical Fields to Neural Operators" \
  --metadata date="Table of contents and Chapter 1" \
  -V documentclass=article -V fontsize=11pt -V papersize=a4 \
  -V geometry:margin=24mm -V colorlinks=true \
  -V urlcolor=blue -V linkcolor=blue \
  -o presentations/textboox/textbook.pdf
```

To check the small code example, save its Python block and run it with
`uv run --project ml --group train python <saved-example.py>`.
It prints 5.0 for the unweighted mean and about 3.47855 for the Gaussian area mean.
