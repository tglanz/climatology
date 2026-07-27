#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=256m
#SBATCH --time=00:05:00

#SBATCH --job-name=tglanz-notify
#SBATCH --output=output/%x-%j.out
#SBATCH --error=output/%x-%j.err

curl -s -d "${SWEEP_NAME} done" ntfy.sh/tglanz-general-51189
