#!/usr/bin/env bash
set -euo pipefail

POOL="${1:-bvet85}"
case "$POOL" in
    bvet42|bvet85) ;;
    *) echo "usage: $0 [bvet42|bvet85]" >&2; exit 2 ;;
esac
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="$REPO_ROOT/ml/configs/$POOL/lat-intra-hold-out.toml"
cd "$REPO_ROOT/slurm"
exec sbatch ./preprocess.slurm "$CONFIG" lat-intra-hold-out
