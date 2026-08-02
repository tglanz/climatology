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

## usage: sbatch train.slurm <config.toml> [extra uv run ml train args...]

set -e
set -x

CONFIG="$1"
shift

if [ -z "$CONFIG" ]; then
  echo "usage: sbatch train.slurm <config.toml> [extra uv run ml train args...]" >&2
  exit 1
fi

cd ../ml

source .venv/bin/activate

uv run ml train -c "$CONFIG" "$@"
curl -s -d "$(basename "$CONFIG" .toml) train done" ntfy.sh/tglanz-general-51189

TRAINING_DIR=$(python -c "from ml.config import load; import sys; print(load(sys.argv[1]).paths.training_dir)" "$CONFIG")
uv run ml evaluate model --training-dir "$TRAINING_DIR" --n-workers 4
curl -s -d "$(basename "$CONFIG" .toml) eval done" ntfy.sh/tglanz-general-51189
