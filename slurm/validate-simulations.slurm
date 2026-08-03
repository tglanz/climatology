#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64g
#SBATCH --time=08:00:00

#SBATCH --job-name=tglanz-validate-simulations
#SBATCH --output=output/%x.out
#SBATCH --error=output/%x.err

if [[ "$SLURM_SUBMIT_DIR" != */climatology/slurm ]]; then
    echo "Unexpected submit dir: $SLURM_SUBMIT_DIR" 1>&2
    exit 1
fi

echo "Slurm submit dir: $SLURM_SUBMIT_DIR"

ROOT_DIR="$(realpath $SLURM_SUBMIT_DIR/..)"
cd $ROOT_DIR

echo "Root dir: $ROOT_DIR"

CONFIG="$ROOT_DIR/ml/configs/default.toml"
echo "Config $CONFIG"


echo ""
echo "Content:"
cat "$CONFIG"
echo ""

echo "Validating: "
uv run ml preprocess validate-simulations -c "$CONFIG" \
    --validate-spinup \
    --validate-convergence \
    --validate-climatology \
    --workers 32


curl -s -d "validate-simulations done: config=$CONFIG" ntfy.sh/tglanz-general-51189
