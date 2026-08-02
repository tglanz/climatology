#!/bin/bash

set -e

CONFIGS=(
    "./ml/configs/lat0-inter-hold-out.toml"
    "./ml/configs/lat0-extra-low-hold-out.toml"
    "./ml/configs/lat0-extra-hi-hold-out.toml"
)

cd "$(dirname "$0")/.."

source ./ml/.venv/bin/activate

for i in "${!CONFIGS[@]}"; do
    sbatch ./slurm/train.slurm "${CONFIGS[$i]}"
done
