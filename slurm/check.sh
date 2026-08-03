#!/bin/bash
# Run from the slurm/ directory: bash preprocess.sh

set -e

CONFIGS=(
    "./ml/configs/lat0-inter-hold-out.toml"
    # TODO: add configs
)

SPLIT_NAMES=(
    "lat0-inter"
    # TODO: add split names
)

# cd into the project's root
cd $(dirname $0)/..

source ./ml/.venv/bin/activate

EXPERIMENT_DIR=./output/barotropic_stirring-T85

# TODO: for each config in configs, verify that its experiment_dir is $EXPERIMENT_DIR, if not, error

uv run ml preprocess create-sweep-file \
    --experiment-dir "$EXPERIMENT_DIR" \
    --key stirring_lat0=stirring_nml.lat0 \
    --key stirring_amplitude=stirring_nml.amplitude \
    --key stirring_widthy=stirring_nml.widthy

for i in "${!CONFIGS[@]}"; do
    sbatch ./slurm/preprocess.slurm "${CONFIGS[$i]}" "${SPLIT_NAMES[$i]}"
done
