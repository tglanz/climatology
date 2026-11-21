"""Check the Markdown examples, draw teaching figures, and build the PDF."""

from __future__ import annotations

import argparse
from fractions import Fraction
from pathlib import Path
import re
import subprocess
import tempfile

import numpy as np

DIRECTORY = Path(__file__).resolve().parent
SOURCE = DIRECTORY / "textbook.md"

# Keep each equation beside its symbol key and interpretation. These groups fit
# on a page; moving the complete group avoids splitting the reader's lookup.
LUA_FILTER = r'''
local function display_math(block)
  if block.t ~= 'Para' then return false end
  for _, inline in ipairs(block.content) do
    if inline.t == 'Math' and inline.mathtype == 'DisplayMath' then
      return true
    end
  end
  return false
end

function Pandoc(doc)
  local result = pandoc.List()
  local i = 1
  while i <= #doc.blocks do
    local block = doc.blocks[i]
    if display_math(block) then
      local stop = i
      while stop < #doc.blocks do
        stop = stop + 1
        local candidate = doc.blocks[stop]
        if pandoc.utils.stringify(candidate):match('^Plain%-English Translation:') then
          break
        end
        if candidate.t == 'Header' or display_math(candidate) then
          error('An equation is missing its immediate symbol key or translation')
        end
      end
      result:insert(pandoc.RawBlock('latex',
        '\\par\\medskip\\noindent\\begin{minipage}{\\linewidth}'))
      for j = i, stop do result:insert(doc.blocks[j]) end
      result:insert(pandoc.RawBlock('latex', '\\end{minipage}\\par\\medskip'))
      i = stop + 1
    elseif block.t == 'CodeBlock' then
      result:insert(pandoc.RawBlock('latex',
        '\\par\\medskip\\noindent\\begin{minipage}{\\linewidth}'))
      result:insert(block)
      result:insert(pandoc.RawBlock('latex', '\\end{minipage}\\par\\medskip'))
      i = i + 1
    else
      result:insert(block)
      i = i + 1
    end
  end
  return pandoc.Pandoc(result, doc.meta)
end
'''

LATEX_HEADER = r'''
\usepackage{needspace}
\usepackage{etoolbox}
\usepackage{enumitem}
\usepackage{float}
\setlist[itemize]{itemsep=2pt,parsep=0pt,topsep=5pt}
\setlength{\emergencystretch}{2em}
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
\pretocmd{\subsection}{\Needspace{8\baselineskip}}{}{}
\pretocmd{\subsubsection}{\Needspace{9\baselineskip}}{}{}
'''


def check_source(source: str) -> None:
    expected = [
        "The Problem", "The Intuition", "The Mechanism", "Reading the Math",
        "Code Connection", "Sanity Check",
    ]
    if re.findall(r"^## (.+)$", source, re.M) != expected:
        raise ValueError("Chapter sections differ from the requested six-section structure")
    if len(re.findall(r"^# Chapter ", source, re.M)) != 1:
        raise ValueError("This installment must contain only Chapter 1")
    blocks = re.findall(r"^\$\$\n(.*?)\n\$\$", source, re.M | re.S)
    labels = re.findall(r"\\tag\{1\.(\d+)\}", source)
    if labels != [str(i) for i in range(1, len(blocks) + 1)]:
        raise ValueError("Equation labels are not consecutive")
    for marker in ("**Symbol-by-Symbol**", "**Plain-English Translation:**"):
        if source.count(marker) != len(blocks):
            raise ValueError(f"Every equation needs {marker}")
    forbidden = r"\b(?:ell|phi|intuitively|essentially)\b|i\.e\.|it is well known|simply put|as we can see"
    if re.search(forbidden, source, re.I):
        raise ValueError("A prohibited phrase or phonetic symbol name was found")
    if not source.isascii():
        raise ValueError("Use ASCII prose and LaTeX for mathematics")
    for link in re.findall(r"\]\(([^)]+)\)", source):
        if not link.startswith(("https://", "http://")):
            if link.startswith("figures/"):
                continue  # Generated below, then checked by Pandoc.
            if not (DIRECTORY / link).exists():
                raise ValueError(f"Missing local source: {link}")
    print(f"PASS: six sections, {len(blocks)} interpreted equations, notation, and source links")


def check_examples(source: str) -> None:
    blocks = re.findall(r"```python\n(.*?)\n```", source, re.S)
    namespace = {"__name__": "textbook_examples"}
    for index, block in enumerate(blocks, 1):
        exec(compile(block, f"{SOURCE}:example-{index}", "exec"), namespace)
    if len(blocks) != 3:
        raise ValueError("Expected the three worked numerical experiments")

    for height in (2, 4, 8, 16):
        nodes, weights = np.polynomial.legendre.leggauss(height)
        for power in range(2 * height):
            expected = 0.0 if power % 2 else 1 / (power + 1)
            np.testing.assert_allclose(
                np.dot(weights / 2, nodes**power), expected, atol=3e-14, rtol=0
            )
    nodes, weights = np.polynomial.legendre.leggauss(2)
    np.testing.assert_allclose(np.dot(weights / 2, nodes**4), 1 / 9)
    assert not np.isclose(np.dot(weights / 2, nodes**4), 1 / 5)

    radius = 6371.0
    distance = radius * np.arccos(0.75)
    parallel = radius * np.pi / 4
    assert abs(distance - 4604.5) < 0.05
    assert abs(parallel - 5003.8) < 0.05
    half_degree = np.deg2rad(0.5)
    equator_area = radius**2 * np.deg2rad(1) * 2 * np.sin(half_degree)
    sixty = np.deg2rad(60)
    high_area = radius**2 * np.deg2rad(1) * (
        np.sin(sixty + half_degree) - np.sin(sixty - half_degree)
    )
    np.testing.assert_allclose(high_area / equator_area, 0.5)
    assert abs(equator_area - 12364) < 0.5
    assert abs(high_area - 6182) < 0.5
    cap_fraction = (1 - np.sin(sixty)) / 2
    assert abs(100 * cap_fraction - 6.70) < 0.005

    # Independent rational integration of the squared hidden field's latitude
    # polynomial, including its longitude mean square of one-half.
    import math
    hidden_square_mean = sum(
        Fraction((-1)**power * math.comb(4, power), 2 * power + 1)
        for power in range(5)
    ) / 2
    assert hidden_square_mean == Fraction(64, 315)

    nodes, weights = np.polynomial.legendre.leggauss(256)
    altered = weights * np.sqrt(1 - nodes**2)
    assert abs(np.dot(altered, nodes**2) / altered.sum() - 0.25) < 1e-6
    print("PASS: Gaussian exactness and its limit, geometry, cap area, and analytic hidden-field RMS")


def make_figures() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Arc, Circle, Polygon

    plt.rcParams.update({
        "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "savefig.facecolor": "white",
    })
    output = DIRECTORY / "figures"
    output.mkdir(exist_ok=True)
    blue, red, gray = "#24658a", "#a6472e", "#52616a"

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.1), layout="constrained")
    ax = axes[0]
    angle = np.deg2rad(48)
    point = np.array([np.cos(angle), np.sin(angle)])
    ax.add_patch(Circle((0, 0), 1, fill=False, color=gray, lw=1.6))
    ax.plot([-1.1, 1.15], [0, 0], color="0.7", lw=1)
    ax.plot([0, 0], [-1.1, 1.15], color="0.7", lw=1)
    ax.plot([0, point[0]], [0, point[1]], color=blue, lw=2)
    ax.plot([0, point[0]], [point[1], point[1]], color=red, lw=2)
    ax.plot([point[0], point[0]], [0, point[1]], color="0.65", ls="--")
    ax.add_patch(Arc((0, 0), 0.6, 0.6, theta1=0, theta2=48, color=blue))
    ax.scatter(*point, color=blue, zorder=4)
    ax.text(0.12, 0.02, r"$\varphi$", color=blue)
    ax.text(0.23, 0.40, r"$R$", color=blue)
    ax.text(0.0, point[1] + 0.08, "Latitude-circle radius", color=red, fontsize=10)
    ax.text(0.03, 1.1, "North", fontsize=10)
    ax.text(0.74, -0.14, "Equatorial plane", fontsize=9)
    ax.set(xlim=(-1.15, 1.3), ylim=(-1.1, 1.3), aspect="equal", title="A cross-section through the center")
    ax.axis("off")

    ax = axes[1]
    vertices = np.array([[0, 0], [1.8, 0.1], [1.95, 1.05], [0.15, 0.95]])
    ax.add_patch(Polygon(vertices, facecolor="#e6f0f5", edgecolor=gray, lw=1.5))
    ax.annotate("", xy=(1.65, -0.15), xytext=(0.08, -0.24),
                arrowprops={"arrowstyle": "<->", "color": blue})
    ax.text(0.85, -0.46, r"East: $R\cos\varphi\,d\lambda$", ha="center", color=blue)
    ax.annotate("", xy=(2.2, 1.02), xytext=(2.05, 0.08),
                arrowprops={"arrowstyle": "<->", "color": red})
    ax.text(2.35, 0.6, r"North: $R\,d\varphi$", rotation=80, ha="center", color=red)
    ax.text(0.95, 0.47, "Small surface patch", ha="center")
    ax.set(xlim=(-0.3, 2.7), ylim=(-0.8, 1.6), aspect="equal", title="Local lengths set the area scale")
    ax.axis("off")
    fig.savefig(output / "geometry.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.3), layout="constrained")
    x = np.linspace(-0.2, 0.2, 600)
    values = [np.where(x < 0, -1.0, 1.0), np.abs(x), x*x]
    titles = ["No unique pole value", "Continuous, but a cusp", "Smooth at the pole"]
    labels = [r"$f_b$", r"$f_c$", r"$f_s$"]
    for ax, value, title, label in zip(axes, values, titles, labels):
        if title == titles[0]:
            ax.plot(x[x < 0], value[x < 0], color=blue, lw=2)
            ax.plot(x[x > 0], value[x > 0], color=blue, lw=2)
            ax.scatter([0, 0], [-1, 1], facecolors="white", edgecolors=blue, zorder=4)
        else:
            ax.plot(x, value, color=blue, lw=2)
        ax.axvline(0, color="0.65", lw=0.9, ls="--")
        ax.set(title=title, xlabel="Signed displacement / radius", ylabel=label)
        ax.grid(alpha=0.18)
    fig.savefig(output / "polar-regularity.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    heights = np.array([2, 4, 8, 16, 32, 64, 128])
    correct, unweighted, extra = [], [], []
    for height in heights:
        nodes, weights = np.polynomial.legendre.leggauss(int(height))
        correct.append(np.dot(weights / 2, nodes**2))
        unweighted.append(np.mean(nodes**2))
        altered = weights * np.sqrt(1 - nodes**2)
        extra.append(np.dot(altered, nodes**2) / altered.sum())
    fig, ax = plt.subplots(figsize=(8.2, 4.0), layout="constrained")
    ax.plot(heights, correct, "o-", label="Gaussian weights", color=blue)
    ax.plot(heights, unweighted, "s-", label="Equal entry weights", color=red)
    ax.plot(heights, extra, "^-", label="Gaussian weights times cosine", color=gray)
    ax.axhline(1 / 3, color=blue, ls="--", lw=0.8)
    ax.axhline(1 / 2, color=red, ls=":", lw=0.8)
    ax.axhline(1 / 4, color=gray, ls=":", lw=0.8)
    ax.set_xscale("log", base=2)
    ax.set(xticks=heights, xticklabels=[str(h) for h in heights],
           xlabel="Gaussian latitude row count", ylabel="Estimated squared-height mean",
           ylim=(0.22, 0.53), title="Increasing resolution does not repair a wrong averaging measure")
    ax.grid(alpha=0.18)
    ax.legend(loc="center right", fontsize=10)
    fig.savefig(output / "weighting-bias.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print("Wrote three teaching figures")


def build_pdf() -> None:
    with tempfile.TemporaryDirectory(prefix="textboox-build-") as temporary:
        temporary = Path(temporary)
        filter_path = temporary / "readable-math.lua"
        header_path = temporary / "layout.tex"
        filter_path.write_text(LUA_FILTER)
        header_path.write_text(LATEX_HEADER)
        subprocess.run([
            "pandoc", "textbook.md", "--standalone", "--pdf-engine=xelatex",
            f"--lua-filter={filter_path}", f"--include-in-header={header_path}",
            "--metadata", "title=From Spherical Fields to Neural Operators",
            "--metadata", "date=Table of contents and Chapter 1",
            "-V", "documentclass=article", "-V", "fontsize=11pt",
            "-V", "papersize=a4", "-V", "geometry:margin=23mm",
            "-V", "colorlinks=true", "-V", "urlcolor=blue",
            "-V", "linkcolor=blue", "-V", "fig-pos=H",
            "-o", "textbook.pdf",
        ], cwd=DIRECTORY, check=True)
    print(f"Built {DIRECTORY / 'textbook.pdf'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Run checks without rebuilding figures or PDF")
    args = parser.parse_args()
    source = SOURCE.read_text()
    check_source(source)
    check_examples(source)
    if not args.check:
        make_figures()
        build_pdf()


if __name__ == "__main__":
    main()
