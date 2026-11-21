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
equations receive a P prefix in the book so their source numbering is unambiguous.
Shared bibliography metadata lives in `references.bib`.
