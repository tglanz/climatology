#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "usage: $0 <config.toml>" >&2
    exit 2
fi
if [[ ! -f "$1" ]]; then
    echo "config not found: $1" >&2
    exit 1
fi
CONFIG="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

uv run --project ml --all-groups ml preprocess validate-simulations \
    -c "$CONFIG" --invalid-only --workers 0 \
    --validate-convergence --validate-spinup --validate-climatology

"$REPO_ROOT/scripts/create-sweep-file.sh" "$CONFIG"

uv run --project ml --all-groups ml preprocess generate-splits \
    -c "$CONFIG" --name fixed
