#!/bin/bash

##resource allocation

#SBATCH --ntasks=2
#SBATCH --cpus-per-task=2
#SBATCH --mem=8g

#SBATCH --job-name=tglanz-example-1
#SBATCH --output=output/%x-%j.out
#SBATCH --error=output/%x-%j.err

## Modules

## run time

set -x

cd ..

pwd

ls

conda run -n isca_env python -m sim.scanner \
  --segments 10 \
  --stirring-lat0 30 \
  --stirring-amplitude 0.75e-10 \
  --stirring-widthy 8 \
  --cores 2 \
  --index 0
