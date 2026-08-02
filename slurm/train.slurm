#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16g
#SBATCH --time=08:00:00

#SBATCH --gres=shard:1
#SBATCH --qos=gpu

#SBATCH --job-name=tglanz-train
#SBATCH --output=output/%x-%j.out
#SBATCH --error=output/%x-%j.err

## usage: sbatch train.slurm <config.toml> [extra ml train args...]

set -x

CONFIG="$1"
shift

if [ -z "$CONFIG" ]; then
  echo "usage: sbatch train.slurm <config.toml> [extra ml train args...]" >&2
  exit 1
fi

cd ../ml

source .venv/bin/activate

ml train -c "$CONFIG" "$@"
