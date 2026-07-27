#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ML="$REPO_ROOT/ml/.venv/bin/ml"
CONFIGS="$REPO_ROOT/ml/configs"
EXPERIMENT_DIR="$REPO_ROOT/output/barotropic_stirring-T85"

"$ML" preprocess validate-simulations \
    -c "$CONFIGS/default.toml" \
    --invalid-only \
    --validate-convergence \
    --validate-spinup \
    --validate-climatology

"$ML" preprocess create-sweep-file \
    --experiment-dir "$EXPERIMENT_DIR" \
    --key stirring_lat0=stirring_nml.lat0 \
    --key stirring_widthy=stirring_nml.widthy \
    --key stirring_amplitude=stirring_nml.amplitude

"$ML" preprocess generate-splits \
    -c "$CONFIGS/lat0-extra-hi-hold-out.toml" \
    --name lat0-extra-hi-hold-out \
    --description "Hold out the highest lat0 values as test set"

"$ML" preprocess generate-splits \
    -c "$CONFIGS/lat0-extra-low-hold-out.toml" \
    --name lat0-extra-low-hold-out \
    --description "Hold out the lowest lat0 values as test set"

"$ML" preprocess generate-splits \
    -c "$CONFIGS/lat0-inter-hold-out.toml" \
    --name lat0-inter-hold-out \
    --description "Hold out intermediate lat0 values as test set"
