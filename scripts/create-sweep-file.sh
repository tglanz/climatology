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

exec uv run --project ml --all-groups ml preprocess create-sweep-file \
    -c "$CONFIG" \
    --key stirring_lat0=stirring_nml.lat0 \
    --key stirring_widthy=stirring_nml.widthy \
    --key stirring_amplitude=stirring_nml.amplitude
