#!/bin/bash

## usage: ./submit-sweep.sh <sweep-file.slurm>
## submits the sweep array job, then chains notify.slurm to fire once all
## array tasks finish (success or failure), via --dependency=afterany.

set -euo pipefail

SWEEP_FILE="$1"
SWEEP_NAME="$(basename "$SWEEP_FILE" .slurm)"

jid=$(sbatch --parsable "$SWEEP_FILE")
echo "submitted $SWEEP_NAME as job $jid"

sbatch --dependency=afterany:"$jid" \
  --export=ALL,SWEEP_NAME="$SWEEP_NAME" \
  notify.slurm
