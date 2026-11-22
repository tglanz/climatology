#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Compile shared Isca build files before starting parallel simulations.
conda run --no-capture-output -n isca_env python -m sim.scanner --compile

exec parallel --jobs 3 --line-buffer --halt soon,fail=1 \
    conda run --no-capture-output -n isca_env python -m sim.scanner \
    --fourier-harmonics 85 \
    --segments 150 --segment-days 7 --dt-atmos 600 \
    --cores 2 --max-retries 3 \
    --stirring-lat0 -10 0 30 40 50 60 70 \
    --stirring-widthy 8 12 16 \
    --stirring-amplitude 7.5e-11 1e-10 1.25e-10 \
    --stirring-decay-time 172800 \
    --stirring-lon0 180 --stirring-widthx 45 --stirring-B 0.4 \
    --index '{}' ::: 0 1 2 3
