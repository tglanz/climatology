#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --job-name=climatology-pipeline
#SBATCH --output=slurm/output/%x-%j.out
set -euo pipefail
# Submit from the repository root. Override resources at submission for full runs.
cd "${SLURM_SUBMIT_DIR:?submit from the repository root}"
exec bash scripts/pipeline.sh "$@"
