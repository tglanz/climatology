# Book Development Guidelines

This file governs all work inside `book/`. It overrides general repo conventions where they conflict.

---

## Purpose

Personal learning book documenting the path toward implementing GSNO (Green's Spherical Neural Operator) for the BVE (Barotropic Vorticity Equation). Written for the author, not for general readers. Tone: formal, concise, no filler.

---

## Character and Formatting Rules

- **ASCII only.** No em dashes (`--`, `---`, Unicode `--`). Use standard hyphens `-` only.
- **No special characters.** No emojis, no Unicode arrows, no fancy symbols.
- **LaTeX allowed** for all mathematics. Use `$...$` inline, `$$...$$` display.
- **No filler prose.** No "it is worth noting", "it can be shown", "as we will see". State facts directly.

---

## Content Style

- **"Worked Examples"** not "Exercises". This is not a textbook. No prompt-style "Answer." formatting.
- **Formal and concise.** Definitions first, intuition second, example third. No padding.
- **Further reading** at the end of each section, formatted as:
  ```
  *Further reading: @RefKey, Sec. X.Y (brief description).*
  ```
  Use BibTeX keys from `references.bib`.
- **Cross-reference, do not duplicate.** If theory is developed in one section, later sections reference it with a one-sentence bridge. No re-stating definitions already established.

---

## References

All references live in `references.bib`.