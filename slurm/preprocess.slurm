#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32g
#SBATCH --time=08:00:00

#SBATCH --job-name=tglanz-preprocess
#SBATCH --output=output/%x-%j.out
#SBATCH --error=output/%x-%j.err

## usage: sbatch ./slurm/preprocess.slurm <config.toml> <split-name>
##
## Example:
##   sbatch ./preprocess.slurm ./ml/configs/lat0-inter-hold-out.toml lat0-inter

set -e

if [[ "$SLURM_SUBMIT_DIR" != */climatology/slurm ]]; then
    echo "Unexpected submit dir: $SLURM_SUBMIT_DIR" 1>&2
    exit 1
fi

CONFIG="$1"
echo "Config: $CONFIG"

SPLIT_NAME="$2"
echo "Split name: $SPLIT_NAME"

if [ -z "$CONFIG" ] || [ -z "$SPLIT_NAME" ]; then
  echo "usage: sbatch ./preprocess.slurm <config.toml> <split-name>" >&2
  exit 1
fi

if [ ! -f "$CONFIG" ]; then
  echo "config file not found: $CONFIG" >&2
  exit 1
fi

cd $SLURM_SUBMIT_DIR/..

source ./ml/.venv/bin/activate

SPLITS_DIR=$(python -c "from ml.config import load; import sys; print(load(sys.argv[1]).paths.splits_dir)" "$CONFIG")
echo "Splits dir: $SPLITS_DIR"


echo "Generating splits..."
uv run ml preprocess generate-splits -c "$CONFIG" --name "$SPLIT_NAME"
curl -s -d "generate splits $SPLIT_NAME done" ntfy.sh/tglanz-general-51189

echo "Preprocessing..."
uv run ml preprocess training-data -c "$CONFIG" \
    --split "$SPLITS_DIR/$SPLIT_NAME.json" \
    --workers 8

curl -s -d "preprocess $SPLIT_NAME done" ntfy.sh/tglanz-general-51189
