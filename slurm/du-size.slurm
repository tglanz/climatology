#!/bin/bash

#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1g
#SBATCH --time=02:00:00

#SBATCH --job-name=tglanz-du-size
#SBATCH --output=output/%x-%j.out
#SBATCH --error=output/%x-%j.err

## usage: sbatch du-size.slurm <path-to-dir>

set -x

TARGET_DIR="$1"

if [ -z "$TARGET_DIR" ]; then
  echo "usage: sbatch du-size.slurm <path-to-dir>" >&2
  exit 1
fi

du -sh "$TARGET_DIR"
