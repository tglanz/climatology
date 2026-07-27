#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SLURM_DIR="$REPO_ROOT/slurm"

if [[ $# -ne 1 ]]; then
    echo "usage: $0 <sweep-script.slurm>"
    exit 1
fi

SWEEP_SCRIPT="$SLURM_DIR/$1"

if [[ ! -f "$SWEEP_SCRIPT" ]]; then
    echo "not found: $SWEEP_SCRIPT"
    exit 1
fi

SWEEP_NAME="${1%.slurm}"

JOBID=$(sbatch "$SWEEP_SCRIPT" | awk '{print $NF}')
echo "submitted $SWEEP_NAME as job $JOBID"

sbatch --dependency=afterany:"$JOBID" --export=SWEEP_NAME="$SWEEP_NAME" "$SLURM_DIR/notify.slurm"
echo "notify job queued after $JOBID"
