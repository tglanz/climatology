#!/bin/bash
set -e

bash .devcontainer/common/post-create.sh

git submodule update --init --recursive

conda env create -f submodules/isca/ci/environment-py3.12_frozen.yml
conda run -n isca_env pip install -e submodules/isca/src/extra/python
