#!/bin/bash

set -e

cd "$(dirname "$0")/.."

CONFIGS=(
  "$(realpath ./ml/configs/lat0-inter-hold-out.toml)"
  "$(realpath ./ml/configs/lat0-extra-low-hold-out.toml)"
  "$(realpath ./ml/configs/lat0-extra-hi-hold-out.toml)"
)

for i in "${!CONFIGS[@]}"; do
    config="${CONFIGS[$i]}"
    if [ ! -f "$config" ]; then
        echo "config not found: $config" >&2
        exit 1
    fi
done

cd ./slurm
for i in "${!CONFIGS[@]}"; do
    sbatch ./train.slurm "${CONFIGS[$i]}"
done
