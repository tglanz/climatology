---
title: "Pandoc Demo"
author: "Your Name"
date: \today

toc: true
numbersections: true

figureTitle: Figure
tableTitle: Table
eqnPrefix:
  - Equation
  - Equations
---

# Introduction

This document demonstrates many of Pandoc's features.

Inline math:

$e^{i\pi}+1=0$

Display math:

$$
\int_{-\infty}^{\infty} e^{-x^2}\,dx=\sqrt{\pi}
$$

---

# Text Formatting

**Bold**

*Italic*

~~Strikethrough~~

`Inline code`

> This is a block quote.

---

# Lists

## Bullet List

- Apples
- Bananas
    - Yellow
    - Green
- Oranges

## Numbered List

1. First
2. Second
3. Third

---

# Tables

| Name | Age | Score |
|------|----:|------:|
| Alice | 25 | 98 |
| Bob   | 31 | 87 |
| Carol | 29 | 93 |

---

# Code

```python
from math import sqrt

def norm(x, y):
    return sqrt(x*x + y*y)

print(norm(3,4))
```

---

# Figures

Figure @fig:lake shows a beautiful landscape.

![Mountain lake.](image.png){#fig:lake width=60%}

---

# Mathematics

The quadratic formula is shown in Equation @eq:quadratic.

$$
x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}
$$ {#eq:quadratic}

We can also define a matrix:

$$
A=
\begin{bmatrix}
1 & 2 & 3\\
4 & 5 & 6\\
7 & 8 & 9
\end{bmatrix}
$$

A summation:

$$
\sum_{i=1}^{n}i=\frac{n(n+1)}{2}
$$

---

# References

We referenced:

- Equation @eq:quadratic
- Figure @fig:lake

---

# Links

- <https://pandoc.org>
- [Pandoc User Guide](https://pandoc.org/MANUAL.html)

---

# Footnotes

Pandoc supports footnotes.[^1]

[^1]: This is an example footnote.

---

# Definition List

Pandoc
: A universal document converter.

Markdown
: A lightweight markup language.

---

# Conclusion

This document demonstrates:

- Metadata
- TOC
- Numbered sections
- Figures
- Figure references
- Equations
- Equation references
- Tables
- Code blocks
- Lists
- Footnotes
- Links
- Images
