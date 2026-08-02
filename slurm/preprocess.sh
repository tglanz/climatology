#!/bin/bash
# Run from the slurm/ directory: bash preprocess.sh

set -e
set -x

CONFIGS=(
    "configs/lat0-inter-hold-out.toml"
    "configs/lat0-extra-low-hold-out.toml"
    "configs/lat0-extra-hi-hold-out.toml"
)

SPLIT_NAMES=(
    "lat0-inter"
    "lat0-extra-low"
    "lat0-extra-hi"
)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ML_DIR="$SCRIPT_DIR/../ml"

cd "$ML_DIR"
source .venv/bin/activate

EXPERIMENT_DIR=$(python -c "from ml.config import load; import sys; print(load(sys.argv[1]).paths.experiment_dir)" "${CONFIGS[0]}")

uv run ml preprocess create-sweep-file \
    --experiment-dir "$EXPERIMENT_DIR" \
    --key stirring_lat0=stirring_nml.lat0 \
    --key stirring_amplitude=stirring_nml.amplitude \
    --key stirring_widthy=stirring_nml.widthy

cd "$SCRIPT_DIR"

for i in "${!CONFIGS[@]}"; do
    sbatch preprocess.slurm "${CONFIGS[$i]}" "${SPLIT_NAMES[$i]}"
done
