#!/bin/bash

## --cores below must match ntasks*cpus-per-task; nodes=1 keeps mpirun's
## slots on a single machine.

#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=2
#SBATCH --mem=8g
#SBATCH --time=08:00:00

#SBATCH --job-name=tglanz-sweep-8-replica
#SBATCH --output=output/%x-%A_%a.out
#SBATCH --error=output/%x-%A_%a.err

## Matrix
##   10 lat0 values x 3 amplitude values x 3 widthy values x 8 replicas
##   = 720 simulations, task ids 0..719
#SBATCH --array=0-719%30

LAT0=(-10 0 10 20 30 40 50 60 70 80)
AMPLITUDE=(0.75e-10 1.0e-10 1.25e-10)
WIDTHY=(8 12 16)
REPLICATES=8

SEGMENTS=200

set -x

## decode SLURM_ARRAY_TASK_ID into one (lat0, amplitude, widthy, replicate)
## combination -- nested div/mod, same trick as reading digits of a
## mixed-radix number. every task id in range maps to exactly one
## combination, no two collide.

t=$SLURM_ARRAY_TASK_ID

replicate=$(( t % REPLICATES ))
t=$(( t / REPLICATES ))

widthy_idx=$(( t % ${#WIDTHY[@]} ))
t=$(( t / ${#WIDTHY[@]} ))

amp_idx=$(( t % ${#AMPLITUDE[@]} ))
t=$(( t / ${#AMPLITUDE[@]} ))

lat0_idx=$t

lat0=${LAT0[$lat0_idx]}
amplitude=${AMPLITUDE[$amp_idx]}
widthy=${WIDTHY[$widthy_idx]}

cd ..

conda run -n isca_env python -m sim.scanner \
  --segments "$SEGMENTS" \
  --stirring-lat0 "$lat0" \
  --stirring-amplitude "$amplitude" \
  --stirring-widthy "$widthy" \
  --cores 4 \
  --index "$replicate"
