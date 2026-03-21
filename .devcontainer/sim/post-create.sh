#!/bin/bash
set -e

bash .devcontainer/common/post-create.sh

conda env create -f ci/environment-py3.12_frozen.yml
conda run -n isca_env pip install -e src/extra/python
