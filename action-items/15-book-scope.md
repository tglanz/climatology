# 15. Make the book independent of the implementation

Priority: P2. Guidance was updated now. Content changes remain open.

## Evidence

The harmonic-analysis, PDE, GFD, and neural-operator introductions promise a particular GSNO implementation.
`book/04-geophysical-fluid-dynamics/vorticity.qmd:80` ties theory to that implementation.
The PDE and neural-operator parts have no chapters in `book/_quarto.yml:23-31`.

## Work

Keep theory relevant to the research: spherical calculus, BVE, spectral methods, statistics, and operator learning.
Explain these without assuming Isca, this ML package, a chosen model, or a particular dataset.
Use named architectures only as cited examples with their assumptions.
Keep experiments, file paths, implementation choices, and plans in project documents.
Mark incomplete coverage honestly. Do not add chapters merely to satisfy an old promise.
Cross-reference shared definitions and remove redundant explanations.

## Verify

1. Read every QMD file in order without project documents. Define all required symbols and prerequisites within the book.
2. Search for repo paths, GSNO implementation promises, current run settings, and assumed software choices. Remove or generalize each.
3. Check that cross-references point to existing content.
4. Render the book and inspect changed chapters, navigation, equations, and citations.
