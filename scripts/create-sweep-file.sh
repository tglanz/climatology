#!/bin/bash

uv run ml preprocess create-sweep-file \
    --experiment-dir ./output/barotropic_stirring-T85 \
    --key stirring_lat0=stirring_nml.lat0 \
    --key stirring_widthy=stirring_nml.widthy \
    --key stirring_amplitude=stirring_nml.amplitude
