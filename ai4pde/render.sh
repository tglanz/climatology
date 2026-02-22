#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PATH="/Library/TeX/texbin:$PATH"

latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" presentation.tex

echo "Output: ${SCRIPT_DIR}/presentation.pdf"
