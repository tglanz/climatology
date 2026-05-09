#!/bin/bash

for ((index=0; index<=999; index++)); do
  if [[ -d ./output/barotropic_stirring-T85/simulations/$index ]]; then
    echo "exist $index"
  else
    conda run --no-capture-output -n isca_env python sim/example_barotropic_stirring.py --index "$index"
  fi
done
