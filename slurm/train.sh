#!/usr/bin/env bash
set -euo pipefail

POOL="${1:-bvet85}"
case "$POOL" in
    bvet42|bvet85) ;;
    *) echo "usage: $0 [bvet42|bvet85]" >&2; exit 2 ;;
esac

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIGS=(
    "$REPO_ROOT/ml/configs/$POOL/default.toml"
    "$REPO_ROOT/ml/configs/$POOL/lat-extra-hi-hold-out.toml"
    "$REPO_ROOT/ml/configs/$POOL/lat-intra-hold-out.toml"
)

for config in "${CONFIGS[@]}"; do
    if [[ ! -f "$config" ]]; then
        echo "config not found: $config" >&2
        exit 1
    fi
done

cd "$REPO_ROOT/slurm"
for config in "${CONFIGS[@]}"; do
    sbatch ./train.slurm "$config"
done
