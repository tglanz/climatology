#!/bin/bash
# Run from the repository root: bash slurm/check.sh

set -e

CONFIGS=(
    "./ml/configs/lat0-inter-hold-out.toml"
)

SPLIT_NAMES=(
    "lat0-inter"
)

# cd into the project's root
cd $(dirname $0)/..

source ./ml/.venv/bin/activate

EXPERIMENT_DIR=./output/barotropic_stirring-T85


uv run --project ml ml preprocess create-sweep-file \
    --experiment-dir "$EXPERIMENT_DIR" \
    --key stirring_lat0=stirring_nml.lat0 \
    --key stirring_amplitude=stirring_nml.amplitude \
    --key stirring_widthy=stirring_nml.widthy

for i in "${!CONFIGS[@]}"; do
    sbatch ./slurm/preprocess.slurm "${CONFIGS[$i]}" "${SPLIT_NAMES[$i]}"
done
