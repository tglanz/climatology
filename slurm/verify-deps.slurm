#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1g
#SBATCH --time=00:05:00

#SBATCH --job-name=tglanz-verify-deps
#SBATCH --output=output/%x-%j.out
#SBATCH --error=output/%x-%j.err

set -x

cd ../ml

source .venv/bin/activate

uv pip list
