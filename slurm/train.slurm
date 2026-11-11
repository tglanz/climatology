#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32g
#SBATCH --time=08:00:00

#SBATCH --gres=shard:1
#SBATCH --qos=gpu

#SBATCH --job-name=tglanz-train
#SBATCH --output=output/%x-%j.out
#SBATCH --error=output/%x-%j.err

## usage: sbatch ./slurm/train.slurm <config.toml> [extra args...]

set -e

if [[ "$SLURM_SUBMIT_DIR" != */climatology/slurm ]]; then
    echo "Unexpected submit dir: $SLURM_SUBMIT_DIR" 1>&2
    exit 1
fi

CONFIG="$1"
shift

if [ -z "$CONFIG" ]; then
  echo "usage: sbatch ./slurm/train.slurm <config.toml> [extra args...]" >&2
  exit 1
fi

if [ ! -f "$CONFIG" ]; then
  echo "config file not found: $CONFIG" >&2
fi

cd $SLURM_SUBMIT_DIR/..
source ./ml/.venv/bin/activate

uv run --project ml ml train -c "$CONFIG" --workers 8 --track-metrics
curl -s -d "train $(basename "$CONFIG" .toml) done" ntfy.sh/tglanz-general-51189
