#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16g
#SBATCH --time=08:00:00

#SBATCH --job-name=tglanz-preprocess
#SBATCH --output=output/%x-%j.out
#SBATCH --error=output/%x-%j.err

## usage: sbatch ./slurm/preprocess.slurm <config.toml> <split-name>
##
## Example:
##   sbatch ./slurm/preprocess.slurm ./ml/configs/lat0-inter-hold-out.toml lat0-inter

set -e

CONFIG="$1"
SPLIT_NAME="$2"

if [ -z "$CONFIG" ] || [ -z "$SPLIT_NAME" ]; then
  echo "usage: sbatch ./slurm/preprocess.slurm <config.toml> <split-name>" >&2
  exit 1
fi

source ./ml/.venv/bin/activate

SPLITS_DIR=$(python -c "from ml.config import load; import sys; print(load(sys.argv[1]).paths.splits_dir)" "$CONFIG")

uv run ml preprocess validate-simulations -c "$CONFIG" \
    --validate-spinup \
    --validate-convergence \
    --validate-climatology \
    --workers 4

uv run ml preprocess generate-splits -c "$CONFIG" --name "$SPLIT_NAME"

uv run ml preprocess training-data -c "$CONFIG" \
    --split "$SPLITS_DIR/$SPLIT_NAME.json" \
    --workers 4

curl -s -d "preprocess $SPLIT_NAME done" ntfy.sh/tglanz-general-51189
