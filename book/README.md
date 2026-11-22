# Book Dev Commands

Preview (live reload):
    quarto preview

Render to _site/:
    quarto render

Check project structure:
    quarto check

Publish to gh-pages (manual):
    quarto publish gh-pages

## Physical prerequisites

The fluid-dynamics chapters are generated from the single Markdown source in
[physical-prerequisites](../presentations/physical-prerequisites/README.md).
Edit that manuscript, then run from the repository root:

```sh
python3 presentations/physical-prerequisites/build.py --sync-book
python3 presentations/physical-prerequisites/build.py --check
```

This synchronizes general theory only. The repository-specific implementation
chapter stays in the companion document. The companion's explicitly numbered
teaching objects, exercises, and equations receive a P prefix in the book so
their source numbering is unambiguous. Instructor solutions remain separate from
the student-facing chapters. The synchronization also copies their dedicated
HTML teaching-object stylesheet.
Shared bibliography metadata lives in `references.bib`.

## Mathematical prerequisites

The mathematical chapters are generated from the chapter sources under
[mathematical-prerequisites](../presentations/mathematical-prerequisites/README.md).
Edit those sources, then run from the repository root:

```sh
python3 presentations/mathematical-prerequisites/build.py --sync-book
python3 presentations/mathematical-prerequisites/build.py --check
```

The book uses an M prefix on the companion's equation, object, and exercise numbers. The existing
physical companion continues to own the fluid-dynamics sequence. Short legacy
pages retain their URLs and cross-reference the owning mathematical treatment.
