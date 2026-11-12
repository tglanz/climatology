#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 2 ]]; then
    echo "usage: bash scripts/submit-pipeline.sh PREPARE.toml RUN.toml [SPLIT.json]" >&2
    exit 2
fi
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
mkdir -p slurm/output
prepare_args=(prepare -c "$1")
if [[ $# -ge 3 ]]; then prepare_args+=(--split "$3"); fi
prepare_id=$(sbatch --parsable slurm/pipeline.slurm "${prepare_args[@]}")
# Federated Slurm may return jobid;cluster. Dependencies take the numeric ID.
prepare_id=${prepare_id%%;*}
sbatch --dependency="afterok:$prepare_id" slurm/pipeline.slurm run -c "$2" --device cpu
