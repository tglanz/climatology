#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32g
#SBATCH --time=08:00:00

#SBATCH --gres=shard:1
#SBATCH --qos=gpu

#SBATCH --job-name=tglanz-evaluate
#SBATCH --output=output/%x-%j.out
#SBATCH --error=output/%x-%j.err

## usage: sbatch ./slurm/evaluate.slurm <config.toml>

set -e

if [[ "$SLURM_SUBMIT_DIR" != */climatology/slurm ]]; then
    echo "Unexpected submit dir: $SLURM_SUBMIT_DIR" 1>&2
    exit 1
fi

CONFIG="$1"

if [ -z "$CONFIG" ]; then
  echo "usage: sbatch ./evaluate.slurm <config.toml>" >&2
  exit 1
fi

if [ ! -f "$CONFIG" ]; then
  echo "config file not found: $CONFIG" >&2
  exit 1
fi

cd $SLURM_SUBMIT_DIR/..
source ./ml/.venv/bin/activate

TRAINING_DIR=$(python -c "from ml.config import load; import sys; print(load(sys.argv[1]).paths.training_dir)" "$CONFIG")
uv run ml evaluate model --training-dir "$TRAINING_DIR" --n-workers 4
curl -s -d "$(basename "$CONFIG" .toml) eval done" ntfy.sh/tglanz-general-51189
