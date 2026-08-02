#!/bin/bash
# Run from the slurm/ directory: bash train.sh

set -e
set -x

CONFIGS=(
    "configs/lat0-inter-hold-out.toml"
    "configs/lat0-extra-low-hold-out.toml"
    "configs/lat0-extra-hi-hold-out.toml"
)

for config in "${CONFIGS[@]}"; do
    sbatch train.slurm "$config"
done
