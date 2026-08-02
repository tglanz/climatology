#!/bin/bash

set -e

CONFIGS=(
    "./ml/configs/lat0-inter-hold-out.toml"
    "./ml/configs/lat0-extra-low-hold-out.toml"
    "./ml/configs/lat0-extra-hi-hold-out.toml"
)

SPLIT_NAMES=(
    "lat0-inter"
    "lat0-extra-low"
    "lat0-extra-hi"
)

cd "$(dirname "$0")/.."

source ./ml/.venv/bin/activate

for i in "${!CONFIGS[@]}"; do
    sbatch ./slurm/preprocess.slurm "${CONFIGS[$i]}" "${SPLIT_NAMES[$i]}"
done
