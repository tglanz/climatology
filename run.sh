#!/bin/bash

conda run -n isca_env python -m sim.scanner --segments 10 --stirring-lat0 30 --stirring-amplitude 0.75e-10 --stirring-widthy 8 --cores 2 --index 0 2>&1 | tee sim.log
